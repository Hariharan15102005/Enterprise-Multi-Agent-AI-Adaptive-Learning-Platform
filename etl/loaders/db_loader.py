import os
import sqlite3
import pandas as pd
from sqlalchemy import text
from config.settings import settings
from database.connection import engine, Base
from database.schema import (
    DimGeolocation, DimCustomer, DimProduct, DimSeller, DimDate,
    FactOrders, FactOrderItems, FactPayments, FactReviews
)

VIEWS_SQL = [
    """
    CREATE VIEW IF NOT EXISTS analytics_obt_orders AS
    SELECT 
        fo.order_id,
        fo.customer_unique_id,
        dc.current_city AS customer_city,
        dc.current_state AS customer_state,
        dc.rfm_segment AS customer_rfm_segment,
        fo.order_status,
        fo.purchase_timestamp,
        dd.year AS purchase_year,
        dd.month AS purchase_month,
        dd.month_name AS purchase_month_name,
        dd.quarter AS purchase_quarter,
        dd.day_name AS purchase_day_name,
        dd.is_holiday_br,
        fo.gross_order_value_brl,
        fo.total_items_price_brl,
        fo.total_freight_value_brl,
        fo.total_item_count,
        fo.primary_payment_type,
        fo.max_payment_installments,
        fo.total_delivery_duration_days,
        fo.delivery_delay_vs_estimated_days,
        fo.is_delivered_late,
        fo.review_score,
        fo.has_review
    FROM fact_orders fo
    LEFT JOIN dim_customer dc ON fo.customer_unique_id = dc.customer_unique_id
    LEFT JOIN dim_date dd ON fo.order_date_key = dd.date_key;
    """,
    """
    CREATE VIEW IF NOT EXISTS agg_daily_sales_ops AS
    SELECT 
        dd.full_date AS order_date,
        dd.year,
        dd.month,
        dd.quarter,
        dd.is_weekend,
        dd.is_holiday_br,
        COUNT(fo.order_id) AS total_orders,
        COUNT(DISTINCT fo.customer_unique_id) AS unique_customers,
        SUM(fo.total_items_price_brl) AS gmv_brl,
        SUM(fo.total_freight_value_brl) AS total_freight_brl,
        SUM(fo.total_payment_value_brl) AS net_revenue_brl,
        AVG(fo.gross_order_value_brl) AS aov_brl,
        AVG(fo.total_delivery_duration_days) AS avg_delivery_days,
        SUM(CASE WHEN fo.is_delivered_late THEN 1 ELSE 0 END) AS late_orders_count,
        AVG(fo.review_score) AS avg_daily_review_score
    FROM fact_orders fo
    JOIN dim_date dd ON fo.order_date_key = dd.date_key
    GROUP BY dd.full_date, dd.year, dd.month, dd.quarter, dd.is_weekend, dd.is_holiday_br;
    """,
    """
    CREATE VIEW IF NOT EXISTS agg_monthly_category_perf AS
    SELECT 
        dd.year,
        dd.month,
        dp.category_name_en,
        COUNT(foi.order_id) AS total_items_sold,
        COUNT(DISTINCT foi.order_id) AS total_orders,
        SUM(foi.item_price_brl) AS total_sales_brl,
        SUM(foi.freight_value_brl) AS total_freight_brl,
        AVG(foi.item_price_brl) AS avg_item_price_brl,
        AVG(foi.carrier_transit_days) AS avg_transit_days,
        SUM(CASE WHEN foi.is_delayed THEN 1 ELSE 0 END) * 100.0 / COUNT(foi.order_id) AS late_rate_pct
    FROM fact_order_items foi
    JOIN dim_product dp ON foi.product_id = dp.product_id
    JOIN dim_date dd ON foi.order_date_key = dd.date_key
    GROUP BY dd.year, dd.month, dp.category_name_en;
    """
]

class DatabaseLoader:
    def __init__(self, db_engine=engine):
        self.engine = db_engine

    def initialize_schema(self, drop_first: bool = False):
        if drop_first:
            with self.engine.begin() as conn:
                for v in ["analytics_obt_orders", "agg_daily_sales_ops", "agg_monthly_category_perf"]:
                    try:
                        conn.execute(text(f"DROP VIEW IF EXISTS {v}"))
                    except Exception:
                        pass
            Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def load_table(self, df: pd.DataFrame, table_name: str, if_exists: str = "append", chunksize: int = 10000):
        if df.empty:
            return 0
        raw_conn = self.engine.raw_connection()
        try:
            df.to_sql(
                table_name,
                con=raw_conn,
                if_exists=if_exists,
                index=False,
                chunksize=chunksize
            )
            raw_conn.commit()
        finally:
            raw_conn.close()
        return len(df)

    def create_analytical_views(self):
        with self.engine.begin() as conn:
            for query in VIEWS_SQL:
                try:
                    conn.execute(text(query))
                except Exception as e:
                    print(f"Warning creating view: {e}")

    def get_table_counts(self) -> dict:
        counts = {}
        tables = [
            "dim_geolocation", "dim_customer", "dim_product", "dim_seller", "dim_date",
            "fact_orders", "fact_order_items", "fact_payments", "fact_reviews"
        ]
        with self.engine.connect() as conn:
            for t in tables:
                try:
                    res = conn.execute(text(f"SELECT COUNT(*) FROM {t}"))
                    counts[t] = res.scalar()
                except Exception as e:
                    counts[t] = f"Error: {e}"
        return counts
