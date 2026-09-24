"""Evaluation suite and metrics calculators for OlistIQ ML models."""

import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
    calinski_harabasz_score,
)


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray
) -> Dict[str, Any]:
    """Calculates comprehensive classification metrics for imbalanced datasets."""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5
        
    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = float(np.mean(y_true))
        
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "sample_size": int(len(y_true)),
        "positive_class_ratio": round(float(np.mean(y_true)), 4)
    }


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, Any]:
    """Calculates standard regression and time series forecast metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    
    # Safe MAPE calculation
    mask = y_true != 0
    if np.any(mask):
        mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)
    else:
        mape = 0.0
        
    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
        "mape_pct": round(mape, 2),
        "sample_size": int(len(y_true))
    }


def evaluate_clustering(
    X_scaled: np.ndarray,
    labels: np.ndarray
) -> Dict[str, Any]:
    """Evaluates unsupervised clustering quality."""
    # Subsample if dataset is very large for fast silhouette computation
    if len(X_scaled) > 10000:
        indices = np.random.RandomState(42).choice(len(X_scaled), size=10000, replace=False)
        sil_score = float(silhouette_score(X_scaled[indices], labels[indices]))
    else:
        sil_score = float(silhouette_score(X_scaled, labels))
        
    ch_score = float(calinski_harabasz_score(X_scaled, labels))
    
    unique_labels, counts = np.unique(labels, return_counts=True)
    cluster_distribution = {
        f"Cluster_{int(k)}": {
            "count": int(v),
            "percentage": round(float(v / len(labels) * 100.0), 2)
        }
        for k, v in zip(unique_labels, counts)
    }
    
    return {
        "silhouette_score": round(sil_score, 4),
        "calinski_harabasz_score": round(ch_score, 2),
        "n_clusters": int(len(unique_labels)),
        "cluster_distribution": cluster_distribution,
        "total_samples": int(len(labels))
    }
