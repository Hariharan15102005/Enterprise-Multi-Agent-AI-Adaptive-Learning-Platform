# OlistIQ Machine Learning & Predictive Intelligence Architecture

## 1. System Overview

The **OlistIQ Machine Learning & Predictive Intelligence Layer (Phase 5)** introduces production-grade, reproducible intelligence models to power automated business decision-making. Operating downstream from the Phase 3 Analytical Data Warehouse (`data/processed/olistiq.db`) and seamlessly integrated with the Phase 4 FastAPI backend, this layer provides customer segmentation, fulfillment delay risk scoring, customer satisfaction risk prediction, demand forecasting, and operational anomaly detection.

```
┌─────────────────────────────────────────────────────────────┐
│                 Analytical Database (PostgreSQL / SQLite)   │
│           (dim_customer, dim_seller, dim_product, fact_*)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Data Extraction Layer (DataExtractor)           │
│        - Out-of-Time & Customer-level Feature Slices        │
│        - Strict Post-Purchase Leakage Elimination           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Feature & Preprocessing Pipelines               │
│        - RobustScaler, StandardScaler, OneHotEncoder        │
│        - Autoregressive Lag & Rolling Window Transforms     │
└──────────────────────────────┬──────────────────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼
┌──────────────┐       ┌──────────────┐         ┌──────────────┐
│ Segmentation │       │ DeliveryRisk │         │ Satisfaction │
│  (K-Means)   │       │(HistGradBst) │         │ (RandForest) │
└──────┬───────┘       └──────┬───────┘         └──────┬───────┘
       │                       │                        │
       └───────────────────────┼────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Model Registry & Metadata Store                 │
│        - Versioned Artifacts (.joblib)                      │
│        - Empirical Evaluation Metrics & Parameters          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             ML Inference Service (ml_service)               │
│        - High-performance Model Loading & Explainability    │
│        - Risk Factor Attribution & Benchmark Comparisons    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             FastAPI REST API Layer (/api/v1/ml/*)           │
│        - Clean JSON Response Contracts for React UI         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Principles

1. **Zero Data Leakage:** Models designed for pre-fulfillment decisions strictly use features available at checkout or order approval. Post-fulfillment dates, actual delivery duration, and review ratings are never allowed into pre-dispatch feature sets.
2. **Chronological Splitting:** Supervised time-sensitive models use out-of-time chronological train/test splits (Train: $< \text{2018-05-01}$, Test: $\ge \text{2018-05-01}$) to guarantee genuine generalization performance.
3. **Decoupled Serving:** Training pipelines (`ml/pipelines/`) are strictly isolated from runtime serving (`ml/inference/ml_inference_service.py` and `backend/app/api/v1/ml.py`).
4. **Explainability by Default:** Every risk and segmentation prediction provides human-interpretable risk factors, drivers, and benchmark metrics for business users.
5. **Reproducibility:** Deterministic random seeds (`seed=42`), persistent metadata, and standalone CLI pipeline commands guarantee exact reproducibility.

---

## 3. Directory Structure

```
ml/
├── __init__.py
├── config/
│   └── ml_config.py               # Hyperparameters, seeds, and storage paths
├── data/
│   └── data_extractor.py          # SQL feature extractors with raw connection pool
├── features/
│   └── definitions.py             # Feature constants & leakage schemas
├── preprocessing/
│   └── transformers.py            # Log1p, RobustScaler, and Tabular ColumnTransformers
├── models/
│   ├── customer_segmentation/     # RFM K-Means clustering + profile mapping
│   ├── delivery_risk/             # HistGradientBoosting delay classifier
│   ├── satisfaction/              # RandomForest review risk classifier
│   ├── forecasting/               # GradientBoosting autoregressive forecaster
│   └── anomaly_detection/         # Rolling Z-Score & statistical anomaly detector
├── evaluation/
│   └── evaluator.py               # Classification, regression, & clustering metrics
├── registry/
│   ├── model_registry.py          # JSON metadata store & joblib loader
│   └── artifacts/                 # Serialized model binaries & detected anomalies
├── inference/
│   └── ml_inference_service.py    # Backend inference & explainability engine
└── pipelines/
    ├── train_customer_segmentation.py
    ├── train_delivery_risk.py
    ├── train_satisfaction_model.py
    ├── train_forecasting.py
    ├── run_anomaly_detection.py
    └── train_all_models.py
```
