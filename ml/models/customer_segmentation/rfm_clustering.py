"""Customer Segmentation model using RFM features and K-Means Clustering."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline

from ml.features.definitions import RFM_FEATURES
from ml.preprocessing.transformers import build_rfm_preprocessor
from ml.evaluation.evaluator import evaluate_clustering
from ml.config.ml_config import ml_config

logger = logging.getLogger("olistiq.ml.customer_segmentation")


class CustomerSegmentationModel:
    """RFM Customer Segmentation clustering engine with business profile mapping."""

    def __init__(self, n_clusters: int = 4, random_state: int = ml_config.RANDOM_SEED):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.features = RFM_FEATURES
        self.preprocessor = build_rfm_preprocessor(self.features)
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            n_init=10,
            max_iter=300,
            random_state=self.random_state
        )
        self.pipeline: Pipeline = None
        self.cluster_profiles: Dict[int, Dict[str, Any]] = {}
        self.cluster_labels_map: Dict[int, str] = {}

    def fit(self, df: pd.DataFrame) -> Tuple["CustomerSegmentationModel", Dict[str, Any]]:
        """Fits segmentation clustering pipeline and derives dynamic segment labels."""
        X = df[self.features].copy()
        
        # Build end-to-end pipeline
        self.pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("clusterer", self.kmeans)
        ])
        
        # Fit pipeline
        self.pipeline.fit(X)
        
        # Transform and evaluate
        X_scaled = self.pipeline.named_steps["preprocessor"].transform(X)
        labels = self.pipeline.named_steps["clusterer"].labels_
        
        eval_metrics = evaluate_clustering(X_scaled, labels)
        
        # Build business segment interpretation from cluster centers
        df_assigned = df.copy()
        df_assigned["cluster"] = labels
        self._build_cluster_profiles(df_assigned)
        
        eval_metrics["cluster_profiles"] = self.cluster_profiles
        return self, eval_metrics

    def _build_cluster_profiles(self, df_with_clusters: pd.DataFrame) -> None:
        """Inspects empirical cluster characteristics and assigns business labels."""
        grouped = df_with_clusters.groupby("cluster")
        centroids = grouped[self.features].mean()
        counts = grouped.size()
        total = len(df_with_clusters)

        # Dynamic label ranking based on spend and recency
        for cluster_id, row in centroids.iterrows():
            cid = int(cluster_id)
            recency = row["recency_days"]
            frequency = row["frequency_orders"]
            spend = row["monetary_spend_brl"]
            aov = row["avg_order_value"]
            
            # Formulate business label
            if spend > 250 or frequency > 1.2:
                if recency < 180:
                    label = "Champions & High-Value"
                    desc = "Highest lifetime spend and strong engagement with recent purchases."
                else:
                    label = "High-Value At-Risk"
                    desc = "Historical big spenders who have not made a purchase recently."
            elif recency < 120:
                label = "Active & Promising"
                desc = "Recent customers with standard order values; prime for repeat nurturing."
            else:
                label = "Low-Engagement / Inactive"
                desc = "One-time historical buyers with older purchase dates and modest spend."

            self.cluster_labels_map[cid] = label
            self.cluster_profiles[cid] = {
                "segment_name": label,
                "description": desc,
                "customer_count": int(counts[cluster_id]),
                "share_pct": round(float(counts[cluster_id] / total * 100.0), 2),
                "avg_recency_days": round(float(recency), 1),
                "avg_frequency": round(float(frequency), 2),
                "avg_monetary_brl": round(float(spend), 2),
                "avg_order_value_brl": round(float(aov), 2),
                "avg_category_diversity": round(float(row["category_diversity"]), 2)
            }

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predicts cluster and business segment for new customer feature vectors."""
        X = df[self.features].copy()
        preds = self.pipeline.predict(X)
        df_out = df.copy()
        df_out["cluster_id"] = preds
        df_out["segment_name"] = df_out["cluster_id"].map(self.cluster_labels_map)
        return df_out

    def explain_customer(self, customer_features: Dict[str, Any]) -> Dict[str, Any]:
        """Provides human-interpretable explanation for a customer's segmentation."""
        df_single = pd.DataFrame([customer_features])
        for col in self.features:
            if col not in df_single.columns:
                df_single[col] = 0.0
                
        cluster_id = int(self.pipeline.predict(df_single[self.features])[0])
        profile = self.cluster_profiles.get(cluster_id, {})
        
        return {
            "cluster_id": cluster_id,
            "segment_name": profile.get("segment_name", f"Cluster {cluster_id}"),
            "description": profile.get("description", ""),
            "customer_metrics": {
                "recency_days": customer_features.get("recency_days"),
                "frequency_orders": customer_features.get("frequency_orders"),
                "monetary_spend_brl": customer_features.get("monetary_spend_brl")
            },
            "benchmark_comparison": {
                "segment_avg_spend": profile.get("avg_monetary_brl"),
                "segment_avg_recency": profile.get("avg_recency_days")
            }
        }
