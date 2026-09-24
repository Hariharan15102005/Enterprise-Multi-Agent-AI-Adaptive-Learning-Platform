"""Business Anomaly Detection engine for e-commerce performance metrics."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("olistiq.ml.anomaly_detection")


class BusinessAnomalyDetector:
    """Detects metric anomalies using rolling statistical thresholds and z-scores."""

    def __init__(self, z_threshold: float = 2.5, window_days: int = 14):
        self.z_threshold = z_threshold
        self.window_days = window_days

    def detect_anomalies(self, df_timeseries: pd.DataFrame) -> List[Dict[str, Any]]:
        """Scans time series metrics for significant operational surges or drops."""
        df = df_timeseries.copy().sort_values("order_date").reset_index(drop=True)
        anomalies = []

        metrics_to_check = [
            {
                "col": "daily_gmv",
                "label": "Gross Merchandise Value (GMV)",
                "unit": "BRL",
                "format": "currency"
            },
            {
                "col": "daily_orders",
                "label": "Order Volume",
                "unit": "orders",
                "format": "integer"
            },
            {
                "col": "daily_late_rate",
                "label": "Delivery SLA Breach Rate",
                "unit": "%",
                "format": "percent"
            },
            {
                "col": "avg_order_value",
                "label": "Average Order Value (AOV)",
                "unit": "BRL",
                "format": "currency"
            }
        ]

        for m in metrics_to_check:
            col = m["col"]
            if col not in df.columns:
                continue

            # Compute rolling window baseline
            rolling_mean = df[col].rolling(window=self.window_days, min_periods=7).mean()
            rolling_std = df[col].rolling(window=self.window_days, min_periods=7).std().replace(0, 1e-5)
            z_scores = (df[col] - rolling_mean) / rolling_std

            for idx, z in z_scores.items():
                if abs(z) >= self.z_threshold and not np.isnan(z):
                    date_val = df.loc[idx, "order_date"]
                    date_str = str(pd.to_datetime(date_val).date())
                    actual = float(df.loc[idx, col])
                    expected = float(rolling_mean.loc[idx])
                    diff_pct = round(((actual - expected) / expected * 100.0), 1) if expected > 0 else 0.0

                    direction = "Spike" if z > 0 else "Drop"
                    severity = "Critical" if abs(z) >= 3.5 else ("High" if abs(z) >= 2.8 else "Moderate")

                    # Formulate business reason
                    if col == "daily_gmv" and direction == "Spike":
                        reason = f"High-revenue surge ({diff_pct:+.1f}% vs {self.window_days}-day baseline) driven by promotion or seasonal campaign."
                    elif col == "daily_late_rate" and direction == "Spike":
                        reason = f"Logistics SLA breakdown: Late delivery rate surged to {actual:.1f}% (baseline {expected:.1f}%)."
                    elif col == "daily_orders" and direction == "Drop":
                        reason = f"Sharp contraction in customer checkout volume ({diff_pct:+.1f}% vs baseline)."
                    else:
                        reason = f"{m['label']} exhibited an unusual {direction.lower()} of {abs(diff_pct):.1f}% compared to normal baseline."

                    anomalies.append({
                        "id": f"anom_{col}_{date_str}",
                        "metric": col,
                        "metric_label": m["label"],
                        "date": date_str,
                        "observed_value": round(actual, 2),
                        "baseline_value": round(expected, 2),
                        "deviation_pct": diff_pct,
                        "z_score": round(float(z), 2),
                        "direction": direction,
                        "severity": severity,
                        "explanation": reason
                    })

        # Sort anomalies chronologically descending
        anomalies.sort(key=lambda x: x["date"], reverse=True)
        logger.info("Detected %d business metric anomalies across historical period.", len(anomalies))
        return anomalies
