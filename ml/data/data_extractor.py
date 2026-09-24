"""Data extraction utilities for OlistIQ Machine Learning pipelines.

Pulls clean training and inference datasets from the analytical database.
"""

import logging
import pandas as pd
from typing import Optional
from database.connection import engine

logger = logging.getLogger("olistiq.ml.data_extractor")


class DataExtractor:
    """Extracts analytical datasets for ML training and evaluation."""

    def __init__(self, db_engine=None):
        self.engine = db_engine or engine

    def _read_sql(self, query: str) -> pd.DataFrame:
        """Helper to reliably read query into pandas DataFrame across SQLite & PostgreSQL."""
        conn = self.engine.raw_connection()
        try:
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    def get_customer_segmentation_data(self) -> pd.DataFrame:
        """Extract customer-level RFM features using customer_unique_id."""
        query = """
        SELECT 
            c.customer_unique_id,
            c.current_state AS customer_state,
            c.lifetime_order_count AS frequency_orders,
            c.lifetime_spend_brl AS monetary_spend_brl,
            c.rfm_recency_days AS recency_days,
            CASE 
                WHEN c.lifetime_order_count > 0 
                THEN c.lifetime_spend_brl / c.lifetime_order_count 
                ELSE c.lifetime_spend_brl 
            END AS avg_order_value,
            COALESCE(cat.category_diversity, 1) AS category_diversity,
            COALESCE(cat.avg_items_per_order, 1.0) AS avg_items_per_order
        FROM dim_customer c
        LEFT JOIN (
            SELECT 
                foi.customer_unique_id,
                COUNT(DISTINCT dp.category_name_en) AS category_diversity,
                CAST(COUNT(foi.order_item_id) AS FLOAT) / COUNT(DISTINCT foi.order_id) AS avg_items_per_order
            FROM fact_order_items foi
            JOIN dim_product dp ON foi.product_id = dp.product_id
            GROUP BY foi.customer_unique_id
        ) cat ON c.customer_unique_id = cat.customer_unique_id
        WHERE c.lifetime_spend_brl > 0
        """
        logger.info("Extracting customer segmentation dataset...")
        df = self._read_sql(query)
        logger.info("Extracted %d customer records for RFM segmentation.", len(df))
        return df

    def get_delivery_risk_data(self) -> pd.DataFrame:
        """Extract order-level delivery risk training dataset.
        
        Strictly excludes actual delivery dates/durations from features.
        """
        query = """
        SELECT 
            fo.order_id,
            fo.purchase_timestamp,
            fo.total_items_price_brl,
            fo.total_freight_value_brl,
            CASE 
                WHEN fo.gross_order_value_brl > 0 
                THEN (fo.total_freight_value_brl / fo.gross_order_value_brl) * 100 
                ELSE 0.0 
            END AS freight_ratio_pct,
            fo.total_item_count,
            fo.unique_product_count,
            CAST((julianday(fo.estimated_delivery_timestamp) - julianday(fo.purchase_timestamp)) AS FLOAT) AS estimated_delivery_duration_days,
            strftime('%m', fo.purchase_timestamp) AS purchase_month,
            strftime('%w', fo.purchase_timestamp) AS purchase_dayofweek,
            strftime('%H', fo.purchase_timestamp) AS purchase_hour,
            dc.current_state AS customer_state,
            COALESCE(item_agg.seller_state, 'SP') AS seller_state,
            COALESCE(item_agg.is_interstate_shipment, 0) AS is_interstate_shipment,
            COALESCE(item_agg.haversine_distance_km, 500.0) AS haversine_distance_km,
            COALESCE(item_agg.max_product_weight_g, 500.0) AS max_product_weight_g,
            COALESCE(item_agg.total_product_volume_cm3, 5000.0) AS total_product_volume_cm3,
            COALESCE(item_agg.top_category_name, 'uncategorized') AS top_category_name,
            COALESCE(item_agg.seller_historical_delay_rate, 5.0) AS seller_historical_delay_rate,
            COALESCE(fo.primary_payment_type, 'credit_card') AS primary_payment_type,
            CASE 
                WHEN fo.is_delivered_late = 1 OR fo.delivery_delay_vs_estimated_days > 0 
                THEN 1 
                ELSE 0 
            END AS is_delivered_late
        FROM fact_orders fo
        JOIN dim_customer dc ON fo.customer_unique_id = dc.customer_unique_id
        LEFT JOIN (
            SELECT 
                foi.order_id,
                MAX(ds.seller_state) AS seller_state,
                MAX(CAST(foi.is_interstate_shipment AS INT)) AS is_interstate_shipment,
                AVG(foi.haversine_distance_km) AS haversine_distance_km,
                MAX(dp.weight_g) AS max_product_weight_g,
                SUM(dp.volume_cm3) AS total_product_volume_cm3,
                MAX(dp.category_name_en) AS top_category_name,
                AVG(ds.sla_breach_rate_pct) AS seller_historical_delay_rate
            FROM fact_order_items foi
            LEFT JOIN dim_seller ds ON foi.seller_id = ds.seller_id
            LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
            GROUP BY foi.order_id
        ) item_agg ON fo.order_id = item_agg.order_id
        WHERE fo.order_status = 'delivered'
          AND fo.delivered_customer_timestamp IS NOT NULL
          AND fo.estimated_delivery_timestamp IS NOT NULL
          AND fo.purchase_timestamp IS NOT NULL
        ORDER BY fo.purchase_timestamp ASC
        """
        logger.info("Extracting delivery risk dataset...")
        df = self._read_sql(query)
        df["purchase_month"] = df["purchase_month"].astype(int)
        df["purchase_dayofweek"] = df["purchase_dayofweek"].astype(int)
        df["purchase_hour"] = df["purchase_hour"].astype(int)
        logger.info("Extracted %d orders for delivery risk modeling.", len(df))
        return df

    def get_satisfaction_data(self) -> pd.DataFrame:
        """Extract customer review risk / satisfaction modeling dataset.
        
        Target: is_negative_review (review_score <= 2).
        Strictly excludes review comments, sentiments, and review timestamps.
        """
        query = """
        SELECT 
            fo.order_id,
            fo.purchase_timestamp,
            fo.total_delivery_duration_days,
            COALESCE(fo.delivery_delay_vs_estimated_days, 0.0) AS delivery_delay_vs_estimated_days,
            CASE 
                WHEN fo.gross_order_value_brl > 0 
                THEN (fo.total_freight_value_brl / fo.gross_order_value_brl) * 100 
                ELSE 0.0 
            END AS freight_ratio_pct,
            fo.total_items_price_brl,
            fo.total_freight_value_brl,
            fo.total_item_count,
            CASE WHEN fo.is_delivered_late = 1 THEN 1 ELSE 0 END AS is_delivered_late,
            COALESCE(fo.primary_payment_type, 'credit_card') AS primary_payment_type,
            dc.current_state AS customer_state,
            COALESCE(item_agg.is_interstate_shipment, 0) AS is_interstate_shipment,
            COALESCE(item_agg.haversine_distance_km, 500.0) AS haversine_distance_km,
            COALESCE(item_agg.top_category_name, 'uncategorized') AS top_category_name,
            COALESCE(item_agg.seller_historical_review_score, 4.0) AS seller_historical_review_score,
            CASE 
                WHEN fo.review_score <= 2 THEN 1 
                ELSE 0 
            END AS is_negative_review
        FROM fact_orders fo
        JOIN dim_customer dc ON fo.customer_unique_id = dc.customer_unique_id
        LEFT JOIN (
            SELECT 
                foi.order_id,
                MAX(CAST(foi.is_interstate_shipment AS INT)) AS is_interstate_shipment,
                AVG(foi.haversine_distance_km) AS haversine_distance_km,
                MAX(dp.category_name_en) AS top_category_name,
                AVG(ds.avg_review_score) AS seller_historical_review_score
            FROM fact_order_items foi
            LEFT JOIN dim_seller ds ON foi.seller_id = ds.seller_id
            LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
            GROUP BY foi.order_id
        ) item_agg ON fo.order_id = item_agg.order_id
        WHERE fo.order_status = 'delivered'
          AND fo.review_score IS NOT NULL
          AND fo.total_delivery_duration_days IS NOT NULL
        ORDER BY fo.purchase_timestamp ASC
        """
        logger.info("Extracting customer satisfaction dataset...")
        df = self._read_sql(query)
        logger.info("Extracted %d records for satisfaction modeling.", len(df))
        return df

    def get_time_series_data(self) -> pd.DataFrame:
        """Extract daily aggregated GMV and Order volume time series."""
        query = """
        SELECT 
            DATE(fo.purchase_timestamp) AS order_date,
            COUNT(fo.order_id) AS daily_orders,
            SUM(fo.gross_order_value_brl) AS daily_gmv,
            AVG(fo.gross_order_value_brl) AS avg_order_value,
            AVG(CASE WHEN fo.is_delivered_late = 1 THEN 1.0 ELSE 0.0 END) * 100.0 AS daily_late_rate,
            AVG(fo.review_score) AS avg_review_score
        FROM fact_orders fo
        WHERE fo.purchase_timestamp >= '2017-01-01'
          AND fo.purchase_timestamp <= '2018-08-31'
        GROUP BY DATE(fo.purchase_timestamp)
        ORDER BY order_date ASC
        """
        logger.info("Extracting daily aggregated time-series data...")
        df = self._read_sql(query)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df = df.set_index("order_date").asfreq("D").fillna({
            "daily_orders": 0,
            "daily_gmv": 0.0,
            "avg_order_value": 0.0,
            "daily_late_rate": 0.0,
            "avg_review_score": 4.0
        }).reset_index()
        logger.info("Extracted %d daily time-series records.", len(df))
        return df
