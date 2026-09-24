"""Inference and Model Serving Layer for OlistIQ ML models.

Decouples FastAPI routes from direct ML artifact mechanics.
"""

import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy import text

from database.connection import engine
from ml.registry.model_registry import model_registry
from ml.config.ml_config import ml_config

logger = logging.getLogger("olistiq.ml.inference")


class MLInferenceService:
    """Provides structured inference, explainability, and analytics for ML models."""

    def __init__(self):
        self.registry = model_registry
        self.engine = engine

    def list_models(self) -> List[Dict[str, Any]]:
        """Returns metadata for all active models in the registry."""
        return self.registry.list_models()

    def get_model_details(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Returns deep metadata, features, and evaluation metrics for a specific model."""
        return self.registry.get_model_metadata(model_name)

    def get_customer_segments_summary(self) -> Dict[str, Any]:
        """Returns overall customer segmentation distribution, cluster profiles, and metrics."""
        meta = self.registry.get_model_metadata("customer_segmentation")
        if not meta:
            raise FileNotFoundError("Customer segmentation model is not registered.")
            
        eval_metrics = meta.get("evaluation_metrics", {})
        profiles = meta.get("extra_metadata", {}).get("cluster_profiles", eval_metrics.get("cluster_profiles", {}))
        
        return {
            "model_version": meta.get("version"),
            "model_type": meta.get("model_type"),
            "total_customers_analyzed": eval_metrics.get("total_samples", 95420),
            "silhouette_score": eval_metrics.get("silhouette_score"),
            "n_clusters": eval_metrics.get("n_clusters", 4),
            "segments": list(profiles.values())
        }

    def predict_customer_segment(self, customer_unique_id: str) -> Dict[str, Any]:
        """Classifies a customer into an RFM segment with personalized explanation."""
        model = self.registry.load_model("customer_segmentation")
        
        # Query customer features from DB
        query = text("""
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
        WHERE c.customer_unique_id = :cid
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"cid": customer_unique_id}).fetchone()
            
        if not result:
            raise KeyError(f"Customer '{customer_unique_id}' not found in analytical database.")
            
        row = dict(result._mapping)
        explanation = model.explain_customer(row)
        explanation["customer_unique_id"] = customer_unique_id
        explanation["customer_state"] = row.get("customer_state")
        return explanation

    def predict_delivery_risk(self, order_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts delivery delay risk for arbitrary pre-dispatch order features."""
        model = self.registry.load_model("delivery_risk")
        meta = self.registry.get_model_metadata("delivery_risk")
        result = model.predict_risk(order_dict)
        result["model_version"] = meta.get("version", "v1.0") if meta else "v1.0"
        return result

    def predict_delivery_risk_for_order(self, order_id: str) -> Dict[str, Any]:
        """Fetches pre-dispatch features for an order from DB and computes delivery risk."""
        query = text("""
        SELECT 
            fo.order_id,
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
            COALESCE(fo.primary_payment_type, 'credit_card') AS primary_payment_type
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
        WHERE fo.order_id = :oid
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"oid": order_id}).fetchone()
            
        if not result:
            raise KeyError(f"Order '{order_id}' not found in database.")
            
        row = dict(result._mapping)
        row["purchase_month"] = int(row["purchase_month"])
        row["purchase_dayofweek"] = int(row["purchase_dayofweek"])
        row["purchase_hour"] = int(row["purchase_hour"])
        
        prediction = self.predict_delivery_risk(row)
        prediction["order_id"] = order_id
        return prediction

    def predict_satisfaction_risk_for_order(self, order_id: str) -> Dict[str, Any]:
        """Infers review risk and dissatisfaction drivers for a completed order."""
        model = self.registry.load_model("satisfaction_risk")
        meta = self.registry.get_model_metadata("satisfaction_risk")
        
        query = text("""
        SELECT 
            fo.order_id,
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
            COALESCE(item_agg.seller_historical_review_score, 4.0) AS seller_historical_review_score
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
        WHERE fo.order_id = :oid
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"oid": order_id}).fetchone()
            
        if not result:
            raise KeyError(f"Order '{order_id}' not found in database.")
            
        row = dict(result._mapping)
        prediction = model.predict_risk(row)
        prediction["order_id"] = order_id
        prediction["model_version"] = meta.get("version", "v1.0") if meta else "v1.0"
        return prediction

    def get_forecast(self, target: str = "daily_gmv", horizon_days: int = 30) -> Dict[str, Any]:
        """Returns multi-step forecast along with model evaluation performance."""
        model_name = "gmv_forecaster" if target == "daily_gmv" else "orders_forecaster"
        forecaster = self.registry.load_model(model_name)
        meta = self.registry.get_model_metadata(model_name)
        
        horizon = forecaster.forecast_horizon(steps=horizon_days)
        
        return {
            "target_metric": target,
            "horizon_days": horizon_days,
            "unit": "BRL" if target == "daily_gmv" else "orders",
            "model_version": meta.get("version", "v1.0") if meta else "v1.0",
            "model_type": meta.get("model_type", "GradientBoostingRegressor") if meta else "GradientBoostingRegressor",
            "evaluation_metrics": meta.get("evaluation_metrics", {}) if meta else {},
            "forecast": horizon
        }

    def get_anomalies(
        self,
        metric: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Returns detected metric anomalies with filtering options."""
        anomalies_file = ml_config.ARTIFACTS_PATH / "detected_anomalies.json"
        if not anomalies_file.exists():
            return {"total_anomalies": 0, "anomalies": []}
            
        with open(anomalies_file, "r", encoding="utf-8") as f:
            anomalies = json.load(f)
            
        if metric:
            anomalies = [a for a in anomalies if a["metric"] == metric]
        if severity:
            anomalies = [a for a in anomalies if a["severity"].lower() == severity.lower()]
            
        return {
            "total_anomalies": len(anomalies),
            "anomalies": anomalies[:limit]
        }


# Global singleton inference service instance
ml_service = MLInferenceService()
