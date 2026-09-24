"""Time Series Forecasting models for daily GMV and Order volume."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.evaluation.evaluator import evaluate_regression
from ml.config.ml_config import ml_config

logger = logging.getLogger("olistiq.ml.forecasting")


class DemandForecaster:
    """Time-series demand and GMV forecasting engine with lag features and confidence bounds."""

    def __init__(
        self,
        target_col: str = "daily_gmv",
        horizon_days: int = ml_config.FORECAST_HORIZON_DAYS,
        random_state: int = ml_config.RANDOM_SEED
    ):
        self.target_col = target_col
        self.horizon_days = horizon_days
        self.random_state = random_state
        self.model = GradientBoostingRegressor(
            n_estimators=120,
            learning_rate=0.05,
            max_depth=4,
            random_state=self.random_state
        )
        self.feature_cols: List[str] = []
        self.residual_std: float = 0.0
        self.last_known_data: pd.DataFrame = None

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Constructs temporal calendar and autoregressive lag features."""
        df_feat = df.copy()
        if "order_date" in df_feat.columns:
            df_feat["order_date"] = pd.to_datetime(df_feat["order_date"])
            df_feat = df_feat.sort_values("order_date").reset_index(drop=True)
            df_feat["dayofweek"] = df_feat["order_date"].dt.dayofweek
            df_feat["month"] = df_feat["order_date"].dt.month
            df_feat["day"] = df_feat["order_date"].dt.day
            df_feat["is_weekend"] = df_feat["dayofweek"].isin([5, 6]).astype(int)
        
        # Lag features
        target = df_feat[self.target_col]
        df_feat["lag_1"] = target.shift(1)
        df_feat["lag_7"] = target.shift(7)
        df_feat["lag_14"] = target.shift(14)
        df_feat["lag_28"] = target.shift(28)
        
        # Rolling window features
        df_feat["rolling_mean_7"] = target.shift(1).rolling(window=7).mean()
        df_feat["rolling_std_7"] = target.shift(1).rolling(window=7).std()
        df_feat["rolling_mean_30"] = target.shift(1).rolling(window=30).mean()
        
        return df_feat

    def fit(
        self,
        df_timeseries: pd.DataFrame,
        split_date: str = "2018-05-31"
    ) -> Tuple["DemandForecaster", Dict[str, Any]]:
        """Fits forecasting model with chronological train/test validation."""
        df_feat = self._create_features(df_timeseries)
        
        # Drop initial NaN rows created by rolling windows
        df_clean = df_feat.dropna().reset_index(drop=True)
        
        self.feature_cols = [
            "dayofweek", "month", "day", "is_weekend",
            "lag_1", "lag_7", "lag_14", "lag_28",
            "rolling_mean_7", "rolling_std_7", "rolling_mean_30"
        ]
        
        # Chronological Split
        train_mask = df_clean["order_date"] <= pd.to_datetime(split_date)
        test_mask = df_clean["order_date"] > pd.to_datetime(split_date)
        
        df_train = df_clean[train_mask]
        df_test = df_clean[test_mask]
        
        if len(df_test) == 0:
            # Fallback to 80/20 sequential split
            split_idx = int(len(df_clean) * 0.8)
            df_train = df_clean.iloc[:split_idx]
            df_test = df_clean.iloc[split_idx:]
            
        X_train = df_train[self.feature_cols]
        y_train = df_train[self.target_col].values
        
        X_test = df_test[self.feature_cols]
        y_test = df_test[self.target_col].values
        
        # 1. Baseline Model: 7-day Rolling Average
        y_baseline_pred = df_test["rolling_mean_7"].values
        baseline_metrics = evaluate_regression(y_test, y_baseline_pred)
        
        # 2. ML Model Fit
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        ml_metrics = evaluate_regression(y_test, y_pred)
        
        self.residual_std = float(np.std(y_test - y_pred))
        self.last_known_data = df_timeseries.tail(60).copy()
        
        evaluation = {
            "target": self.target_col,
            "train_samples": len(df_train),
            "test_samples": len(df_test),
            "test_period": {
                "start": str(df_test["order_date"].min().date()),
                "end": str(df_test["order_date"].max().date())
            },
            "baseline_metrics": baseline_metrics,
            "ml_metrics": ml_metrics,
            "mae_improvement_pct": round(
                float((baseline_metrics["mae"] - ml_metrics["mae"]) / baseline_metrics["mae"] * 100.0), 2
            ) if baseline_metrics["mae"] > 0 else 0.0
        }
        
        logger.info(
            "Forecasting [%s] - Baseline MAE: %.2f vs ML MAE: %.2f (%.1f%% improvement)",
            self.target_col, baseline_metrics["mae"], ml_metrics["mae"], evaluation["mae_improvement_pct"]
        )
        return self, evaluation

    def forecast_horizon(self, steps: int = 30) -> List[Dict[str, Any]]:
        """Generates forward multi-step daily forecasts with 95% confidence intervals."""
        history = self.last_known_data.copy()
        last_date = pd.to_datetime(history["order_date"].max())
        
        forecasts = []
        
        for i in range(1, steps + 1):
            next_date = last_date + pd.Timedelta(days=i)
            
            # Construct row with latest lags from history
            target_series = history[self.target_col]
            
            row = {
                "order_date": next_date,
                "dayofweek": next_date.dayofweek,
                "month": next_date.month,
                "day": next_date.day,
                "is_weekend": 1 if next_date.dayofweek in [5, 6] else 0,
                "lag_1": float(target_series.iloc[-1]),
                "lag_7": float(target_series.iloc[-7]) if len(target_series) >= 7 else float(target_series.iloc[-1]),
                "lag_14": float(target_series.iloc[-14]) if len(target_series) >= 14 else float(target_series.iloc[-1]),
                "lag_28": float(target_series.iloc[-28]) if len(target_series) >= 28 else float(target_series.iloc[-1]),
                "rolling_mean_7": float(target_series.tail(7).mean()),
                "rolling_std_7": float(target_series.tail(7).std()) if len(target_series) >= 7 else 0.0,
                "rolling_mean_30": float(target_series.tail(30).mean()),
            }
            
            X_step = pd.DataFrame([row])[self.feature_cols]
            pred_val = max(0.0, float(self.model.predict(X_step)[0]))
            
            # Confidence interval
            ci_margin = 1.96 * max(self.residual_std, pred_val * 0.1)
            lower_bound = max(0.0, pred_val - ci_margin)
            upper_bound = pred_val + ci_margin
            
            forecast_item = {
                "date": next_date.strftime("%Y-%m-%d"),
                "forecast_value": round(pred_val, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "day_name": next_date.strftime("%A"),
                "is_weekend": bool(row["is_weekend"])
            }
            forecasts.append(forecast_item)
            
            # Append predicted value into history to feed next step lags
            new_hist_row = {"order_date": next_date, self.target_col: pred_val}
            history = pd.concat([history, pd.DataFrame([new_hist_row])], ignore_index=True)
            
        return forecasts
