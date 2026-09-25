# OLISTIQ — COMPLETE PROJECT INTELLIGENCE & IMPLEMENTATION MAP

**Project Name:** OlistIQ — AI-Powered E-Commerce Decision Intelligence Platform  
**Audit Date:** September 2026  
**Environment / OS:** Windows / Python 3.11.9 / Node.js (Vite + React 18)  
**Database:** SQLite 3 (`data/processed/olistiq.db`)  
**Backend Framework:** FastAPI (Uvicorn ASGI)  
**AI / Agent Framework:** LangGraph (`StateGraph`) + Ollama / OpenAI LLM Fallback  
**ML Framework:** Scikit-Learn (Joblib Serialized Pipelines)  
**Frontend Framework:** React 18 + Vite + Lucide Icons + Recharts  
**Test Suite Status:** 65/65 Passed (100% Pass Rate)

---

## 1. EXECUTIVE SUMMARY & CODEBASE INVENTORY

OlistIQ is an enterprise-grade decision intelligence platform designed for Brazilian e-commerce data (Olist dataset). It integrates an automated dimensional ETL pipeline, analytical data warehouse, statistical/heuristic analytics service, five production machine learning pipelines, a deterministic and secure multi-node LangGraph AI Analyst with automated SQL generation and self-repair, an async FastAPI backend, and a modern responsive React/Vite dashboard.

### High-Level Inventory Statistics
- **Total Tracked Project Files:** 204 files across root, etl, database, backend, ml, ai_analyst, frontend, tests, scripts, and docs.
- **Python Source Files:** 58 `.py` files.
- **Frontend Source Files:** 22 `.jsx` / `.js` / `.css` / `.json` files.
- **ML Artifacts:** 5 serialized `.joblib` models + 2 `.json` metadata registries/anomaly reports.
- **Test Suite:** 11 test modules containing 65 automated tests (65 passing).
- **Documentation:** 24 technical markdown specifications in `docs/` + `README.md`.
- **Database Tables & Views:** 9 physical tables (5 dimensions, 4 facts) + 3 optimized analytical views containing 99,441 processed orders.

---

## 2. PROJECT DIRECTORY TREE

The actual repository directory structure is as follows:

```
c:\Users\Hariharan K\OneDrive\Desktop\IBM_INTERN_PROJECT\
│
├── .env
├── .env.example
├── .gitignore
├── OlistIQ_Analytics_and_AI.ipynb       # End-to-end presentation and submission notebook
├── README.md                            # Main project overview and setup instructions
├── requirements.txt                     # Core Python dependencies
├── test.db                              # Ephemeral test database
│
├── ai_analyst/                          # Phase 6: LangGraph Multi-Node AI Analyst
│   ├── __init__.py
│   ├── service.py                       # High-level AI Analyst execution service
│   ├── config/
│   │   └── ai_config.py                 # LLM, guardrails, and timeouts configuration
│   ├── graph/
│   │   ├── edges.py                     # Conditional routing functions (security, intent, validation)
│   │   ├── nodes.py                     # 11 StateGraph processing nodes
│   │   └── workflow.py                  # LangGraph StateGraph builder and compilation
│   ├── insights/
│   │   └── synthesizer.py               # Analytical insight generation and summarization
│   ├── metrics/
│   │   └── metric_catalog.py            # Predefined business metrics & formula store
│   ├── planning/
│   │   └── query_planner.py             # Plan generator for SQL vs ML dispatch
│   ├── routing/
│   │   └── hybrid_router.py             # Heuristic + LLM intent classification
│   ├── schema_retriever/
│   │   └── schema_store.py              # Semantic schema index and column definitions
│   ├── security/
│   │   └── guardrails.py                # SQL injection, table allowlists, AST validation
│   ├── sql/
│   │   ├── executor.py                  # Safe read-only SQLite execution engine
│   │   ├── generator.py                 # Prompt templates & SQL code generation
│   │   └── validator.py                 # Strict read-only SQL parser and AST validator
│   └── state/
│       └── agent_state.py               # TypedDict LangGraph AgentState definition
│
├── archive/                             # Raw Olist CSV Datasets
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
│
├── backend/                             # Phase 4 & 7: FastAPI Backend Application
│   ├── run.py                           # Backend launcher script
│   └── app/
│       ├── main.py                      # FastAPI application instance, CORS, middleware, lifecycle
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── ai.py                # AI Analyst query, health, and capabilities endpoints
│       │       ├── analytics.py         # Revenue, category, payments, and insight endpoints
│       │       ├── customers.py         # Segmentation, geographic, and paginated customer list
│       │       ├── dashboard.py         # Executive KPIs and high-level summary endpoints
│       │       ├── data_quality.py      # ETL validation and data quality audit endpoints
│       │       ├── logistics.py         # Delivery performance, lead times, state/seller stats
│       │       ├── ml.py                # ML registry, predictions, forecasts, anomalies
│       │       ├── products.py          # Product catalog and performance listing
│       │       ├── router.py            # V1 Master APIRouter aggregator
│       │       └── sellers.py           # Seller leaderboards and delivery scorecards
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py                # Backend application settings (Pydantic Settings)
│       │   ├── exceptions.py            # Custom exceptions and global HTTP exception handlers
│       │   └── logging.py               # Structured backend logging configuration
│       ├── db/
│       │   ├── __init__.py
│       │   └── session.py               # SQLAlchemy database engine and session dependency
│       ├── repositories/                # Direct database access & SQL execution
│       │   ├── __init__.py
│       │   ├── analytics_repository.py
│       │   ├── base_repository.py
│       │   ├── customer_repository.py
│       │   ├── dashboard_repository.py
│       │   ├── data_quality_repository.py
│       │   ├── logistics_repository.py
│       │   ├── product_repository.py
│       │   └── seller_repository.py
│       ├── schemas/                     # Pydantic Request & Response DTO Models
│       │   ├── __init__.py
│       │   ├── ai.py
│       │   ├── analytics.py
│       │   ├── common.py
│       │   ├── customers.py
│       │   ├── dashboard.py
│       │   ├── data_quality.py
│       │   ├── logistics.py
│       │   ├── ml.py
│       │   ├── products.py
│       │   └── sellers.py
│       └── services/                    # Business logic orchestration layer
│           ├── __init__.py
│           ├── analytics_service.py
│           ├── customer_service.py
│           ├── dashboard_service.py
│           ├── data_quality_service.py
│           ├── logistics_service.py
│           ├── product_service.py
│           └── seller_service.py
│
├── config/                              # Global Project Settings
│   ├── __init__.py
│   └── settings.py                      # Master paths, environment configurations, and constants
│
├── data/                                # Data Storage Directory
│   ├── processed/
│   │   └── olistiq.db                   # Production SQLite Star-Schema Data Warehouse (99,441 orders)
│   └── quarantine/                      # Quarantine for corrupted/failed raw records
│
├── database/                            # Phase 2: Schema DDL, Views & Database Connection
│   ├── __init__.py
│   ├── connection.py                    # SQLite connection factory & URI resolvers
│   ├── schema.py                        # SQLAlchemy Table & Metadata schema definitions
│   └── migrations/
│       ├── 001_initial_schema.sql       # DDL for 5 dimension tables and 4 fact tables
│       └── 002_analytical_views.sql     # DDL for 3 analytical aggregation views
│
├── docs/                                # Project Specifications & Architecture Documentation
│   ├── AI_ANALYST_API_CONTRACT.md
│   ├── AI_ANALYST_ARCHITECTURE.md
│   ├── AI_ANALYST_EVALUATION.md
│   ├── AI_ANALYST_SECURITY.md
│   ├── API_CONTRACT.md
│   ├── ARCHITECTURE.md
│   ├── BACKEND_ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   ├── DATASET_PROFILING_REPORT.md
│   ├── ETL_ARCHITECTURE.md
│   ├── ETL_DATA_QUALITY_REPORT.md
│   ├── METRIC_DEFINITIONS.md
│   ├── ML_API_CONTRACT.md
│   ├── ML_ARCHITECTURE.md
│   ├── ML_DATA_LEAKAGE.md
│   ├── ML_EVALUATION_REPORT.md
│   ├── ML_FEATURE_CATALOG.md
│   ├── ML_MODEL_CATALOG.md
│   ├── PHASE_5_COMPLETION_REPORT.md
│   ├── PHASE_6_COMPLETION_REPORT.md
│   ├── PHASE_7_COMPLETION_REPORT.md
│   ├── PHASE_8_COMPLETION_REPORT.md
│   ├── PHASE_9_COMPLETION_REPORT.md
│   └── PHASE_10_COMPLETION_REPORT.md
│
├── etl/                                 # Phase 3: Dimensional ETL Pipeline
│   ├── __main__.py                      # CLI entrypoint for `python -m etl`
│   ├── ingestion/
│   │   ├── __init__.py
│   └── csv_reader.py                # Safe CSV streaming reader with schema type casting
│   ├── loaders/
│   │   ├── __init__.py
│   │   └── db_loader.py                 # SQLite batch loader with foreign key verification
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── pipeline_runner.py           # Master ETL execution and timing coordinator
│   ├── transformations/
│   │   ├── __init__.py
│   │   ├── customer_transform.py        # Customer dimension & RFM metric builder
│   │   ├── date_transform.py            # Calendar dimension generation (2016–2019)
│   │   ├── geolocation_transform.py     # Deduplicated centroid zip code aggregator
│   │   ├── item_transform.py            # Fact order items & product freight enrichment
│   │   ├── order_transform.py           # Fact orders & delivery duration metrics
│   │   ├── payment_transform.py         # Fact payments & installment categorization
│   │   ├── product_transform.py         # Product dimension with category translation
│   │   ├── review_transform.py          # Fact reviews & sentiment categorization
│   │   └── seller_transform.py          # Seller dimension & performance aggregation
│   └── validation/
│       ├── __init__.py
│       └── quality_engine.py            # Data quality verification engine (PKs, FKs, nulls, ranges)
│
├── frontend/                            # Phase 8: Modern React 18 + Vite Dashboard
│   ├── .gitignore
│   ├── .oxlintrc.json
│   ├── index.html                       # HTML5 Root Entry
│   ├── package.json                     # Frontend dependencies & scripts
│   ├── package-lock.json
│   ├── README.md
│   ├── vite.config.js                   # Vite configuration & proxy settings
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   └── src/
│       ├── App.css                      # Global layout styling
│       ├── App.jsx                      # Navigation, tab switching, and page container
│       ├── index.css                    # Tailwind-compatible root CSS and custom variables
│       ├── main.jsx                     # React DOM root render
│       ├── api/
│       │   ├── client.js                # Fetch/Axios API wrapper with error interception
│       │   ├── coreApis.js              # Core dashboard & health API bindings
│       │   └── domainApis.js            # Analytics, ML, AI, and Logistics API bindings
│       ├── assets/
│       │   ├── hero.png
│       │   ├── react.svg
│       │   └── vite.svg
│       ├── components/
│       │   ├── charts/
│       │   │   └── ChartComponents.jsx  # Recharts wrappers: Line, Bar, Area, Donut, Heatmap
│       │   ├── common/
│       │   │   └── UIComponents.jsx     # Metric cards, status badges, loaders, modals
│       │   └── layout/
│       │       ├── Layout.jsx           # Main viewport shell, top navigation bar
│       │       └── Sidebar.jsx          # Collapsible navigation drawer
│       ├── pages/
│       │   ├── AIAnalystPage.jsx        # Conversational AI Analyst UI with SQL & Insight cards
│       │   ├── AnalyticsPage.jsx        # Revenue trends, Category breakdown, Payment analytics
│       │   ├── CustomersPage.jsx        # RFM customer segmentation and geo distribution
│       │   ├── DashboardPage.jsx        # Executive KPIs, revenue run rate, operational overview
│       │   ├── DataQualityPage.jsx      # ETL quality audit, schema compliance, missing value rates
│       │   ├── LogisticsPage.jsx        # Delivery lead times, carrier delay maps, state performance
│       │   ├── MLIntelligencePage.jsx   # Interactive inference for 5 ML models & anomalies
│       │   ├── SellersPage.jsx          # Seller leaderboard, fulfillment metrics, delay rates
│       │   └── SystemHealthPage.jsx     # Backend health, database connection, latency monitor
│       └── styles/
│           └── index.css                # Component-level stylesheets
│
├── ml/                                  # Phase 5: Machine Learning & Predictive Intelligence
│   ├── __init__.py
│   ├── config/
│   │   └── ml_config.py                 # Hyperparameters, random seeds, split dates, horizons
│   ├── data/
│   │   └── data_extractor.py            # Feature query extractor from SQLite warehouse
│   ├── evaluation/
│   │   └── evaluator.py                 # Accuracy, F1, ROC-AUC, PR-AUC, MAE, RMSE, MAPE metrics
│   ├── features/
│   │   └── definitions.py               # Feature schemas, target columns, leakage guard definitions
│   ├── inference/
│   │   └── ml_inference_service.py      # Model loader, predictor, and scoring service
│   ├── models/
│   │   ├── anomaly_detection/
│   │   │   └── business_anomalies.py    # Revenue & order spike/drop anomaly detector (IQR/Isolation)
│   │   ├── customer_segmentation/
│   │   │   └── rfm_clustering.py        # K-Means RFM segmentation (4 clusters)
│   │   ├── delivery_risk/
│   │   │   └── delay_classifier.py      # HistGradientBoosting delay classifier (Pre-dispatch)
│   │   ├── forecasting/
│   │   │   └── demand_forecaster.py     # Lag-Autoregressive GradientBoosting GMV & Order forecaster
│   │   └── satisfaction/
│   │       └── review_risk.py           # RandomForest 1-2 star review risk classifier
│   ├── pipelines/
│   │   ├── run_anomaly_detection.py     # Offline anomaly detection batch execution
│   │   ├── train_all_models.py          # Master orchestrator for training all 5 models
│   │   ├── train_customer_segmentation.py
│   │   ├── train_delivery_risk.py
│   │   ├── train_forecasting.py
│   │   └── train_satisfaction_model.py
│   ├── preprocessing/
│   │   └── transformers.py              # Log transformers, categorical encoders, standard scalers
│   └── registry/
│       ├── model_registry.py            # Model versioning, metadata logging, artifact persistence
│       └── artifacts/
│           ├── customer_segmentation_v1.0.joblib
│           ├── delivery_risk_v1.0.joblib
│           ├── detected_anomalies.json
│           ├── gmv_forecaster_v1.0.joblib
│           ├── model_registry.json      # Master metadata registry for all active models
│           ├── orders_forecaster_v1.0.joblib
│           └── satisfaction_risk_v1.0.joblib
│
├── scripts/                             # Utility & Automation Scripts
│   ├── generate_submission_notebook.py  # Builds comprehensive Jupyter Notebook
│   ├── run_etl.py                       # CLI script to trigger full ETL process
│   └── validate_e2e_integration.py      # End-to-end sanity verification test
│
└── tests/                               # Phase 9: Automated Pytest Suite (65 Tests)
    ├── __init__.py
    ├── test_ai_analyst.py               # 14 tests: Security, intent, SQL generation, graph execution
    ├── test_ai_api.py                   # 4 tests: AI endpoints, health, queries, injections
    ├── test_api_endpoints.py            # 17 tests: Dashboard, analytics, customer, logistics endpoints
    ├── test_api_refinement.py           # 5 tests: Error structures, CORS, headers, openapi
    ├── test_data_quality.py             # 3 tests: PK uniqueness, FK integrity, quality scoring
    ├── test_idempotency.py              # 2 tests: Re-run safety, table counts, view accessibility
    ├── test_ingestion.py                # 2 tests: CSV schema integrity and row presence
    ├── test_ml_api.py                   # 9 tests: ML registry, predictions, forecast, anomaly APIs
    ├── test_ml_models.py                # 6 tests: Leakage prevention, model training, accuracy checks
    └── test_transformations.py          # 3 tests: Geo centroids, translation maps, calendar spans
```

---

## 3. FILE-BY-FILE AUDIT OF IMPORTANT SOURCE FILES

### Configuration & Base Environment

#### File: `config/settings.py`
- **Purpose:** Central project configuration containing absolute file paths, SQLite paths, Ollama/OpenAI parameters, and logging thresholds.
- **Phase:** Phase 2 (Architecture) & Phase 4 (FastAPI).
- **Depends on:** `pydantic-settings`, `os`, `pathlib`.
- **Used by:** ETL pipelines, database connections, ML training, AI Analyst, Backend API.
- **Important symbols:** `Settings`, `get_settings()`, `BASE_DIR`, `SQLITE_DB_PATH`, `RAW_DATA_DIR`.
- **Status:** **COMPLETE**

#### File: `database/connection.py`
- **Purpose:** Manages SQLite database connection strings, SQLAlchemy engine creation, and thread-safe connection pooling for the data warehouse.
- **Phase:** Phase 2 (Database Design).
- **Depends on:** `sqlalchemy`, `config.settings`.
- **Used by:** `database.schema`, `etl.loaders.db_loader`, `backend.app.db.session`, `ai_analyst.sql.executor`.
- **Important symbols:** `get_engine()`, `get_db_connection()`, `check_db_connection()`.
- **Status:** **COMPLETE**

#### File: `database/schema.py`
- **Purpose:** SQLAlchemy Declarative / Table definitions for all 5 dimension tables and 4 fact tables.
- **Phase:** Phase 2 (Database Design) & Phase 3 (ETL).
- **Depends on:** `sqlalchemy`.
- **Used by:** ETL loader, backend repositories, validation engine.
- **Important symbols:** `dim_customer`, `dim_product`, `dim_seller`, `dim_geolocation`, `dim_date`, `fact_orders`, `fact_order_items`, `fact_payments`, `fact_reviews`.
- **Status:** **COMPLETE**

---

### ETL Pipeline (`etl/`)

#### File: `etl/ingestion/csv_reader.py`
- **Purpose:** Streams raw CSV files from `archive/` using pandas with strict UTF-8/ISO-8859-1 decoding fallback and basic type coercions.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`, `config.settings`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `CSVReader`, `read_raw_dataset()`, `read_all_raw_datasets()`.
- **Status:** **COMPLETE**

#### File: `etl/validation/quality_engine.py`
- **Purpose:** Validates raw and transformed datasets against primary key uniqueness, foreign key referential integrity, null thresholds, and valid numeric ranges.
- **Phase:** Phase 3 (ETL) & Phase 9 (Testing).
- **Depends on:** `pandas`, `numpy`.
- **Used by:** `etl.pipelines.pipeline_runner`, `backend.app.repositories.data_quality_repository`.
- **Important symbols:** `DataQualityEngine`, `validate_primary_keys()`, `validate_foreign_keys()`, `calculate_data_quality_score()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/customer_transform.py`
- **Purpose:** Cleans customer zip codes, standardizes city names, and computes customer-level Recency, Frequency, and Monetary (RFM) metrics.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`, `datetime`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_customers()`, `calculate_customer_rfm()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/geolocation_transform.py`
- **Purpose:** Solves the critical Olist geolocation row-multiplication bug by calculating mean centroid latitude and longitude grouped strictly by 5-digit zip code prefix and state.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_geolocation()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/product_transform.py`
- **Purpose:** Implements category translation from Portuguese to English using translation maps, fills missing categories with `'other'`, and computes product volume ($H \times W \times L$).
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`, `numpy`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_products()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/seller_transform.py`
- **Purpose:** Transforms seller records, standardizes states, and computes seller fulfillment history and lead time KPIs.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_sellers()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/date_transform.py`
- **Purpose:** Generates a complete date dimension table spanning 2016-01-01 through 2019-12-31 with day of week, quarter, month name, weekend indicator, and holiday flags.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`, `datetime`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `generate_date_dimension()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/order_transform.py`
- **Purpose:** Builds the central `fact_orders` table, calculating delivery duration (days), estimated delay vs actual (days), delivery status, and order timeline timestamps.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`, `numpy`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_orders()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/item_transform.py`
- **Purpose:** Builds `fact_order_items`, calculates item sequence numbers, price, freight ratios, and calculates Haversine distance between customer and seller zip codes.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`, `numpy`, `math`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_order_items()`, `calculate_haversine_distance()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/payment_transform.py`
- **Purpose:** Transforms payment rows into `fact_payments`, validates installments, payment types (credit card, boleto, voucher, debit card), and sequential indices.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_payments()`.
- **Status:** **COMPLETE**

#### File: `etl/transformations/review_transform.py`
- **Purpose:** Builds `fact_reviews`, categorizes star ratings (1-2: Negative, 3: Neutral, 4-5: Positive), calculates review answer response latency.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `pandas`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `transform_reviews()`.
- **Status:** **COMPLETE**

#### File: `etl/loaders/db_loader.py`
- **Purpose:** Executes SQL DDL migrations (`001_initial_schema.sql`, `002_analytical_views.sql`) and loads transformed DataFrames into SQLite with chunking and indexed foreign key verification.
- **Phase:** Phase 3 (ETL).
- **Depends on:** `sqlalchemy`, `sqlite3`, `pandas`.
- **Used by:** `etl.pipelines.pipeline_runner`.
- **Important symbols:** `DBLoader`, `create_tables()`, `load_dataframe()`, `create_views()`.
- **Status:** **COMPLETE**

#### File: `etl/pipelines/pipeline_runner.py`
- **Purpose:** Orchestrates the entire sequential ETL workflow: CSV reading -> Validation -> Transformations -> Database Loading -> Analytical Views -> Quality Report.
- **Phase:** Phase 3 (ETL).
- **Depends on:** All modules in `etl/`.
- **Used by:** `scripts/run_etl.py`, `etl/__main__.py`.
- **Important symbols:** `ETLPipelineRunner`, `run_full_pipeline()`.
- **Status:** **COMPLETE**

---

### Machine Learning Layer (`ml/`)

#### File: `ml/config/ml_config.py`
- **Purpose:** Defines ML hyperparameters, feature names, out-of-time train/test split dates (`2018-05-01`), random seed (`42`), and paths to model artifacts.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `config.settings`.
- **Used by:** All ML training scripts and inference services.
- **Important symbols:** `MLConfig`, `MODEL_ARTIFACTS_DIR`, `SPLIT_DATE`.
- **Status:** **COMPLETE**

#### File: `ml/data/data_extractor.py`
- **Purpose:** Extracts clean feature datasets directly from `olistiq.db` with SQL joins for each ML task, enforcing strict pre-dispatch time constraints to prevent target leakage.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `sqlite3`, `pandas`, `config.settings`.
- **Used by:** Training pipelines and inference services.
- **Important symbols:** `MLDataExtractor`, `get_customer_rfm_data()`, `get_delivery_risk_data()`, `get_satisfaction_risk_data()`, `get_daily_time_series()`.
- **Status:** **COMPLETE**

#### File: `ml/features/definitions.py`
- **Purpose:** Explicit schema definitions of input features, categorical variables, continuous variables, and disallowed target-leaking fields.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `dataclasses`.
- **Used by:** Data extractor, pipelines, inference services.
- **Important symbols:** `DELIVERY_RISK_FEATURES`, `SATISFACTION_RISK_FEATURES`, `FORECASTING_FEATURES`, `LEAKAGE_FORBIDDEN_COLUMNS`.
- **Status:** **COMPLETE**

#### File: `ml/models/customer_segmentation/rfm_clustering.py`
- **Purpose:** Implements Log-transformed, Standard-Scaled K-Means clustering ($k=4$) on Recency, Frequency, Monetary, and Category Diversity metrics, labeling clusters into 4 business segments.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `sklearn.cluster.KMeans`, `sklearn.preprocessing.StandardScaler`.
- **Used by:** `ml.pipelines.train_customer_segmentation`, `ml.inference.ml_inference_service`.
- **Important symbols:** `RFMCustomerSegmentation`, `fit()`, `predict()`, `get_segment_profiles()`.
- **Status:** **COMPLETE**

#### File: `ml/models/delivery_risk/delay_classifier.py`
- **Purpose:** Trains a `HistGradientBoostingClassifier` with balanced class weights using strictly pre-dispatch features to predict probability of delivery delay.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `sklearn.ensemble.HistGradientBoostingClassifier`, `sklearn.compose.ColumnTransformer`.
- **Used by:** `ml.pipelines.train_delivery_risk`, `ml.inference.ml_inference_service`.
- **Important symbols:** `DeliveryRiskClassifier`, `train()`, `predict_proba()`.
- **Status:** **COMPLETE**

#### File: `ml/models/satisfaction/review_risk.py`
- **Purpose:** Trains a `RandomForestClassifier` to identify orders at high risk of receiving 1-star or 2-star reviews based on fulfillment timeline and freight metrics.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `sklearn.ensemble.RandomForestClassifier`.
- **Used by:** `ml.pipelines.train_satisfaction_model`, `ml.inference.ml_inference_service`.
- **Important symbols:** `SatisfactionRiskModel`, `train()`, `predict_risk()`.
- **Status:** **COMPLETE**

#### File: `ml/models/forecasting/demand_forecaster.py`
- **Purpose:** Implements lag-autoregressive GradientBoosting regression (`lag_1`, `lag_7`, `lag_14`, `lag_28`, rolling means) to generate 30-day ahead forecasts for GMV and order counts with confidence intervals.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `sklearn.ensemble.GradientBoostingRegressor`, `pandas`, `numpy`.
- **Used by:** `ml.pipelines.train_forecasting`, `ml.inference.ml_inference_service`.
- **Important symbols:** `DemandForecaster`, `train()`, `forecast_next_days()`.
- **Status:** **COMPLETE**

#### File: `ml/models/anomaly_detection/business_anomalies.py`
- **Purpose:** Detects statistical revenue and volume anomalies using 30-day rolling Z-scores ($|Z| > 2.5$) and multi-feature Isolation Forest.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `sklearn.ensemble.IsolationForest`, `pandas`, `numpy`.
- **Used by:** `ml.pipelines.run_anomaly_detection`, `ml.inference.ml_inference_service`.
- **Important symbols:** `BusinessAnomalyDetector`, `detect_anomalies()`.
- **Status:** **COMPLETE**

#### File: `ml/registry/model_registry.py`
- **Purpose:** Model artifact persistence manager and metadata tracker (`model_registry.json`). Loads `.joblib` models into memory on backend startup.
- **Phase:** Phase 5 (ML Intelligence).
- **Depends on:** `joblib`, `json`, `os`.
- **Used by:** `ml.pipelines.*`, `ml.inference.ml_inference_service`.
- **Important symbols:** `ModelRegistry`, `register_model()`, `load_model()`, `get_active_model_metadata()`.
- **Status:** **COMPLETE**

#### File: `ml/inference/ml_inference_service.py`
- **Purpose:** Unified high-level inference facade serving predictions, batch scoring, customer lookup, forecasts, and anomaly reports to FastAPI routes.
- **Phase:** Phase 5 & Phase 7.
- **Depends on:** `ml.registry.model_registry`, `ml.data.data_extractor`.
- **Used by:** `backend.app.api.v1.ml`, `ai_analyst.graph.nodes`.
- **Important symbols:** `MLInferenceService`, `get_ml_service()`, `predict_delivery_risk()`, `predict_satisfaction_risk()`, `get_forecast()`, `get_anomalies()`.
- **Status:** **COMPLETE**

---

### AI Analyst / LangGraph Layer (`ai_analyst/`)

#### File: `ai_analyst/state/agent_state.py`
- **Purpose:** Defines the `AgentState` TypedDict tracking user question, security flags, intent classification, query plan, generated SQL, validation errors, retry count, SQL query results, and synthesized markdown insights.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `typing.TypedDict`, `typing.Annotated`.
- **Used by:** All LangGraph nodes, edges, and workflow.
- **Important symbols:** `AgentState`, `SQLQueryResult`, `QueryPlan`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/security/guardrails.py`
- **Purpose:** Enforces strict security guardrails on user input, filtering adversarial jailbreak attempts, system prompt exfiltration, and SQL injection patterns.
- **Phase:** Phase 6 (AI Analyst) & Phase 10.
- **Depends on:** `re`, `logging`.
- **Used by:** `ai_analyst.graph.nodes.check_security_node`.
- **Important symbols:** `enforce_guardrails()`, `contains_prompt_injection()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/routing/hybrid_router.py`
- **Purpose:** Hybrid intent classifier using high-speed deterministic keyword/regex heuristics and fallback LLM parsing to categorize questions into SQL analytics, ML prediction, or conversational queries.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `re`, `json`, `config.settings`.
- **Used by:** `ai_analyst.graph.nodes.classify_intent_node`.
- **Important symbols:** `route_query()`, `IntentCategory`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/schema_retriever/schema_store.py`
- **Purpose:** Semantic schema catalog providing exact DDL, table relationships, column types, and business descriptions for tables and views.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `json`, `database.schema`.
- **Used by:** `ai_analyst.graph.nodes.retrieve_schema_and_metrics_node`.
- **Important symbols:** `SchemaStore`, `get_schema_store()`, `get_relevant_schema()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/metrics/metric_catalog.py`
- **Purpose:** Catalog of standardized business metrics (e.g., GMV = `SUM(price)`, AOV = `GMV / COUNT(DISTINCT order_id)`, Delivery Lead Time = `julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)`).
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `dataclasses`.
- **Used by:** Query planner and SQL generator.
- **Important symbols:** `MetricCatalog`, `METRIC_CATALOG`, `get_metric_definition()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/planning/query_planner.py`
- **Purpose:** Analyzes user intent, identifies target tables, filters, time horizons, and dimensions, generating an execution plan before SQL code generation.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `ai_analyst.schema_retriever.schema_store`, `ai_analyst.metrics.metric_catalog`.
- **Used by:** `ai_analyst.graph.nodes.create_query_plan_node`.
- **Important symbols:** `QueryPlanner`, `create_query_plan()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/sql/generator.py`
- **Purpose:** Generates SQLite-compliant SQL queries using few-shot prompted LLMs (or deterministic fallback templates) based on query plans and verified schema DDLs.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `config.settings`, `ai_analyst.sql.validator`.
- **Used by:** `ai_analyst.graph.nodes.generate_sql_node`.
- **Important symbols:** `SQLGenerator`, `generate_sql_query()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/sql/validator.py`
- **Purpose:** Multi-stage SQL validator verifying that generated queries are strictly `SELECT` statements, reference only allowlisted tables/views, contain no destructive DDL/DML, and enforce maximum row limits (`LIMIT 100`).
- **Phase:** Phase 6 (AI Analyst) & Phase 10.
- **Depends on:** `sqlparse`, `re`.
- **Used by:** `ai_analyst.graph.nodes.validate_sql_node`.
- **Important symbols:** `validate_sql()`, `SQLValidationResult`, `ALLOWED_TABLES`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/sql/executor.py`
- **Purpose:** Executes verified SQL queries against SQLite in a read-only transaction with query timeout enforcement (5.0 seconds).
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `sqlite3`, `pandas`, `config.settings`.
- **Used by:** `ai_analyst.graph.nodes.execute_sql_node`.
- **Important symbols:** `SQLExecutor`, `execute_query()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/insights/synthesizer.py`
- **Purpose:** Transforms raw SQL tabular results and ML predictions into executive natural language insights with KPI callouts, percentage comparisons, and actionable recommendations.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `json`, `config.settings`.
- **Used by:** `ai_analyst.graph.nodes.generate_insights_node`.
- **Important symbols:** `InsightSynthesizer`, `synthesize_insights()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/graph/nodes.py`
- **Purpose:** Contains all 11 individual asynchronous execution nodes for the LangGraph state machine.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** All `ai_analyst` submodules.
- **Used by:** `ai_analyst.graph.workflow`.
- **Important symbols:** `check_security_node`, `classify_intent_node`, `route_ml_node`, `retrieve_schema_and_metrics_node`, `create_query_plan_node`, `generate_sql_node`, `validate_sql_node`, `execute_sql_node`, `repair_sql_node`, `generate_insights_node`, `format_response_node`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/graph/edges.py`
- **Purpose:** Conditional edge decision functions routing between security check, ML inference, SQL execution, self-repair loop, and final response formatting.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `ai_analyst.state.agent_state`.
- **Used by:** `ai_analyst.graph.workflow`.
- **Important symbols:** `check_security_edge()`, `route_intent_edge()`, `validate_sql_edge()`, `execute_sql_edge()`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/graph/workflow.py`
- **Purpose:** Assembles and compiles the full LangGraph `StateGraph` workflow into an executable agent instance.
- **Phase:** Phase 6 (AI Analyst).
- **Depends on:** `langgraph.graph.StateGraph`, `ai_analyst.graph.nodes`, `ai_analyst.graph.edges`.
- **Used by:** `ai_analyst.service.py`.
- **Important symbols:** `create_ai_analyst_graph()`, `ai_analyst_graph`.
- **Status:** **COMPLETE**

#### File: `ai_analyst/service.py`
- **Purpose:** High-level service facade providing asynchronous query execution (`query()`), health monitoring, and system capability introspection.
- **Phase:** Phase 6 & Phase 7.
- **Depends on:** `ai_analyst.graph.workflow`.
- **Used by:** `backend.app.api.v1.ai`.
- **Important symbols:** `AIAnalystService`, `get_ai_analyst_service()`.
- **Status:** **COMPLETE**

---

### Backend / FastAPI Layer (`backend/app/`)

#### File: `backend/app/main.py`
- **Purpose:** FastAPI entry point. Configures CORS middleware, request timing headers (`X-Process-Time`), global exception handlers, APIRouter mounting, and lifespan startup verification.
- **Phase:** Phase 4 (FastAPI) & Phase 7 (Backend Integration).
- **Depends on:** `fastapi`, `backend.app.api.v1.router`, `backend.app.core.*`.
- **Used by:** `backend/run.py`, Uvicorn ASGI server.
- **Important symbols:** `app`, `lifespan()`, `health_check()`.
- **Status:** **COMPLETE**

#### File: `backend/app/api/v1/router.py`
- **Purpose:** Master API router aggregating 9 feature sub-routers under `/api/v1`.
- **Phase:** Phase 4 & Phase 7.
- **Depends on:** `fastapi.APIRouter`, sub-routers in `backend.app.api.v1.*`.
- **Used by:** `backend.app.main.py`.
- **Important symbols:** `api_router`.
- **Status:** **COMPLETE**

#### File: `backend/app/repositories/analytics_repository.py`
- **Purpose:** Database repository executing analytical SQL queries for revenue time series, category sales, payment distributions, and KPI trends.
- **Phase:** Phase 4 (Analytics Engine).
- **Depends on:** `sqlalchemy`, `backend.app.db.session`.
- **Used by:** `backend.app.services.analytics_service`.
- **Important symbols:** `AnalyticsRepository`, `get_revenue_trends()`, `get_category_performance()`, `get_payment_distribution()`.
- **Status:** **COMPLETE**

#### File: `backend/app/repositories/dashboard_repository.py`
- **Purpose:** Fetches high-level executive dashboard numbers: total GMV (R$15.42M), total orders (99,441), total customers, AOV, on-time delivery rate, and average review score.
- **Phase:** Phase 4 (Analytics Engine).
- **Depends on:** `sqlalchemy`, `backend.app.db.session`.
- **Used by:** `backend.app.services.dashboard_service`.
- **Important symbols:** `DashboardRepository`, `get_executive_kpis()`.
- **Status:** **COMPLETE**

---

### Frontend Layer (`frontend/src/`)

#### File: `frontend/src/App.jsx`
- **Purpose:** Main React application container providing sidebar navigation, active page tab routing, global header with live system health status, and dark theme support.
- **Phase:** Phase 8 (React Frontend).
- **Depends on:** `react`, `lucide-react`, all page components in `frontend/src/pages/`.
- **Used by:** `frontend/src/main.jsx`.
- **Important symbols:** `App()`.
- **Status:** **COMPLETE**

#### File: `frontend/src/api/domainApis.js`
- **Purpose:** Frontend HTTP client mapping all backend endpoints for Dashboard KPIs, Analytics, Customers, Logistics, ML models, and AI Analyst queries.
- **Phase:** Phase 8 (React Frontend).
- **Depends on:** `frontend/src/api/client.js`.
- **Used by:** All page components.
- **Important symbols:** `dashboardApi`, `analyticsApi`, `customerApi`, `logisticsApi`, `mlApi`, `aiApi`.
- **Status:** **COMPLETE**

#### File: `frontend/src/pages/AIAnalystPage.jsx`
- **Purpose:** Interactive Natural Language to SQL AI Analyst interface. Includes prompt suggestions, query chat thread, rendered SQL code block with copy button, query execution metrics, and synthesized executive insight cards.
- **Phase:** Phase 8 (React Frontend).
- **Depends on:** `react`, `lucide-react`, `frontend/src/api/domainApis.js`.
- **Used by:** `frontend/src/App.jsx`.
- **Important symbols:** `AIAnalystPage()`.
- **Status:** **COMPLETE**

#### File: `frontend/src/pages/MLIntelligencePage.jsx`
- **Purpose:** Interactive machine learning dashboard supporting real-time delivery risk prediction, customer RFM cluster lookup, 30-day GMV/Order demand forecasting chart, and business anomaly timeline.
- **Phase:** Phase 8 (React Frontend).
- **Depends on:** `react`, `recharts`, `frontend/src/api/domainApis.js`.
- **Used by:** `frontend/src/App.jsx`.
- **Important symbols:** `MLIntelligencePage()`.
- **Status:** **COMPLETE**

---

## 4. PHASE-BY-PHASE IMPLEMENTATION MAP

| Phase | Objective | Main Files / Folders | Status | Verification Detail |
|---|---|---|---|---|
| **Phase 1** — Dataset Profiling | Ingest, profile, and audit 9 raw Olist CSVs; discover schema constraints, null rates, and distribution anomalies. | `archive/`, `docs/DATASET_PROFILING_REPORT.md` | **IMPLEMENTED** | All 9 CSVs audited and documented; geo duplication and category translation issues identified. |
| **Phase 2** — Architecture + DB Design | Design star schema dimensional data warehouse (5 dims, 4 facts), migration scripts, and analytical views. | `database/schema.py`, `database/migrations/*.sql`, `database/connection.py`, `docs/DATABASE_DESIGN.md` | **IMPLEMENTED** | Physical tables and views created; schema validated against SQLite constraints. |
| **Phase 3** — ETL + Analytical Database | Build modular, idempotent Python ETL pipeline with quality engine, custom transformations, and SQLite loader. | `etl/ingestion/`, `etl/transformations/`, `etl/validation/`, `etl/loaders/`, `etl/pipelines/`, `scripts/run_etl.py` | **IMPLEMENTED** | Complete ETL executed; 99,441 orders loaded into `data/processed/olistiq.db`. |
| **Phase 4** — Analytics Engine + FastAPI | Build core analytics repository, service layer, and initial FastAPI endpoints for KPIs, revenue, categories, and logistics. | `backend/app/main.py`, `backend/app/repositories/`, `backend/app/services/`, `backend/app/api/v1/` | **IMPLEMENTED** | Executive dashboard, revenue trends, seller leaderboards, and logistics endpoints active. |
| **Phase 5** — ML + Predictive Intelligence | Train, evaluate, and register 5 ML models (RFM K-Means, Delivery Risk, Satisfaction Risk, Demand Forecaster, Anomalies). | `ml/models/`, `ml/pipelines/`, `ml/registry/`, `ml/inference/`, `docs/ML_*.md` | **IMPLEMENTED** | 5 models trained, serialized to `.joblib`, registered in `model_registry.json`, leakage strictly prevented. |
| **Phase 6** — AI Analyst / LangGraph / NL-to-SQL | Construct 11-node LangGraph agent state machine for safe natural language to SQL conversion with self-repair and insights. | `ai_analyst/graph/`, `ai_analyst/sql/`, `ai_analyst/security/`, `ai_analyst/insights/`, `ai_analyst/service.py` | **IMPLEMENTED** | 11-node StateGraph compiled, security guardrails active, self-repair loop tested, hybrid router working. |
| **Phase 7** — Backend Integration + API Refinement | Integrate ML inference service and AI Analyst into FastAPI; implement standard error handling, CORS, and request timing. | `backend/app/api/v1/ml.py`, `backend/app/api/v1/ai.py`, `backend/app/core/exceptions.py`, `docs/API_CONTRACT.md` | **IMPLEMENTED** | 28 active REST endpoints with Pydantic request/response validation and standardized error payloads. |
| **Phase 8** — React Frontend | Build modern React 18 + Vite dashboard with 9 dedicated pages, responsive sidebar, Recharts, and interactive AI/ML controls. | `frontend/src/App.jsx`, `frontend/src/pages/`, `frontend/src/components/`, `frontend/package.json` | **IMPLEMENTED** | Full Vite+React app implemented with 9 pages (Dashboard, Analytics, Customers, Sellers, Logistics, Data Quality, ML, AI Analyst, System Health). |
| **Phase 9** — Testing + Evaluation | Implement automated pytest suite for ETL, database integrity, ML leakage/performance, AI security, and API endpoints. | `tests/test_*.py`, `scripts/validate_e2e_integration.py`, `docs/PHASE_9_COMPLETION_REPORT.md` | **IMPLEMENTED** | 65 automated tests written and verified passing (100% pass rate in ~54s). |
| **Phase 10** — Deployment & Delivery Packaging | Package standalone runnable backend, frontend build, automated run scripts, Docker documentation, and submission notebook. | `OlistIQ_Analytics_and_AI.ipynb`, `scripts/generate_submission_notebook.py`, `backend/run.py`, `docs/PHASE_10_COMPLETION_REPORT.md` | **IMPLEMENTED** | Single-command launch, executable Jupyter submission notebook, and self-contained database artifacts ready. |
| **Phase 11** — Documentation & Demo | Comprehensive project documentation, architectural diagrams, API contracts, and interview talking points. | `docs/*.md`, `README.md`, `docs/PROJECT_IMPLEMENTATION_MAP.md` | **IMPLEMENTED** | 25 detailed markdown guides and technical specifications created. |

---

## 5. DATABASE MAP & STAR SCHEMA ARCHITECTURE

**Database Technology:** SQLite 3  
**Database Path:** `data/processed/olistiq.db`  
**Schema Architecture:** Kimball Star Schema with Conformed Dimensions, Fact Tables, and One Big Table (OBT) Analytical Views.

### Database Objects Inventory

| Object Name | Type | Row Count | Primary Key | Purpose / Description | Source Transformation |
|---|---|---|---|---|---|
| `dim_customer` | Table | 96,096 | `customer_id` | Unique customer profiles, locations, and RFM scores. | `etl/transformations/customer_transform.py` |
| `dim_product` | Table | 32,951 | `product_id` | Product catalog with translated English categories and dimensions. | `etl/transformations/product_transform.py` |
| `dim_seller` | Table | 3,095 | `seller_id` | Merchant locations, order volume, and historical delay metrics. | `etl/transformations/seller_transform.py` |
| `dim_geolocation` | Table | 19,010 | `geolocation_zip_code_prefix` | Deduplicated geographic centroid coordinates (lat/lng). | `etl/transformations/geolocation_transform.py` |
| `dim_date` | Table | 1,461 | `date_key` | Conformed calendar dimension spanning 2016-01-01 to 2019-12-31. | `etl/transformations/date_transform.py` |
| `fact_orders` | Table (Fact) | 99,441 | `order_id` | **Central fact table** containing order lifecycle dates and lead times. | `etl/transformations/order_transform.py` |
| `fact_order_items` | Table (Fact) | 112,650 | `order_item_id`, `order_id` | Granular item-level prices, freight values, and distance. | `etl/transformations/item_transform.py` |
| `fact_payments` | Table (Fact) | 103,886 | `order_id`, `payment_sequential` | Payment transaction methods, installments, and values. | `etl/transformations/payment_transform.py` |
| `fact_reviews` | Table (Fact) | 99,224 | `review_id` | Customer review star ratings, comments, and response times. | `etl/transformations/review_transform.py` |
| `analytics_obt_orders` | View | 99,441 | `order_id` | Denormalized One Big Table joining orders, customers, items, reviews. | `database/migrations/002_analytical_views.sql` |
| `agg_daily_sales_ops` | View | 634 | `order_date` | Daily aggregated GMV, order volume, freight, and delay rates. | `database/migrations/002_analytical_views.sql` |
| `agg_monthly_category_perf` | View | 1,283 | `year_month`, `category` | Monthly category performance, item volume, and average rating. | `database/migrations/002_analytical_views.sql` |

### Key Column Definitions & Foreign Keys

1. **`fact_orders` (Central Fact):**
   - **Primary Key:** `order_id` (TEXT)
   - **Foreign Keys:** `customer_id` -> `dim_customer.customer_id`, `order_purchase_date_key` -> `dim_date.date_key`
   - **Important Columns:** `order_status`, `order_purchase_timestamp`, `order_delivered_customer_date`, `order_estimated_delivery_date`, `delivery_duration_days`, `delivery_delay_vs_estimated_days`, `is_delivered_late`.

2. **`fact_order_items` (Grain: 1 row per item in order):**
   - **Composite Key:** `order_id`, `order_item_id`
   - **Foreign Keys:** `order_id` -> `fact_orders.order_id`, `product_id` -> `dim_product.product_id`, `seller_id` -> `dim_seller.seller_id`
   - **Important Columns:** `price`, `freight_value`, `total_item_value`, `shipping_limit_date`, `haversine_distance_km`.

---

## 6. ETL PIPELINE ARCHITECTURE & DATA FLOW

```
Raw CSV Datasets (archive/)
        │
        ▼
CSV Ingestion & Schema Coercion (etl/ingestion/csv_reader.py)
        │
        ▼
Pre-Transformation Quality Audit (etl/validation/quality_engine.py)
        │
        ├─► Geolocation Centroid Deduplication (etl/transformations/geolocation_transform.py)
        ├─► Product Category Translation & Volume (etl/transformations/product_transform.py)
        ├─► Seller Metrics Standardization (etl/transformations/seller_transform.py)
        ├─► Customer Profiles & RFM Metrics (etl/transformations/customer_transform.py)
        ├─► Conformed Date Dimension Generation (etl/transformations/date_transform.py)
        ├─► Fact Orders & Delivery Duration (etl/transformations/order_transform.py)
        ├─► Fact Order Items & Haversine Distance (etl/transformations/item_transform.py)
        ├─► Fact Payments Transformation (etl/transformations/payment_transform.py)
        └─► Fact Reviews & Sentiment Categorization (etl/transformations/review_transform.py)
        │
        ▼
Post-Transformation Integrity Verification (PK uniqueness, FK integrity, Null checks)
        │
        ▼
SQLite Database Loader (etl/loaders/db_loader.py -> data/processed/olistiq.db)
        │
        ▼
Analytical Views Creation (analytics_obt_orders, agg_daily_sales_ops, agg_monthly_category_perf)
```

---

## 7. ANALYTICS ENGINE & IMPLEMENTED CAPABILITIES

All analytics are calculated directly from verified warehouse tables and views:

| Capability | Calculation / Metric Formula | Implementation File | API Endpoint | DB Source | Frontend Ready |
|---|---|---|---|---|---|
| **Executive KPIs** | Total GMV ($15.42M), Total Orders (99.4K), Total Customers (96.1K), AOV ($155.09), On-Time Rate (93.4%), Avg Rating (4.07) | `backend/app/repositories/dashboard_repository.py` | `GET /api/v1/dashboard/kpis` | `fact_orders`, `fact_order_items`, `fact_reviews` | **YES** |
| **Revenue Trends** | Daily/Monthly GMV, Order Volume, Freight Value, Rolling 7-day Average | `backend/app/repositories/analytics_repository.py` | `GET /api/v1/analytics/revenue` | `agg_daily_sales_ops` | **YES** |
| **Category Analytics** | GMV, item count, share %, average price, and review score grouped by category | `backend/app/repositories/analytics_repository.py` | `GET /api/v1/analytics/categories` | `agg_monthly_category_perf`, `dim_product` | **YES** |
| **Payment Analytics** | Payment volume, transaction share %, average installment count by payment type | `backend/app/repositories/analytics_repository.py` | `GET /api/v1/analytics/payments` | `fact_payments` | **YES** |
| **Customer RFM** | Recency (days), Frequency (orders), Monetary (BRL), RFM segment distributions | `backend/app/repositories/customer_repository.py` | `GET /api/v1/customers/segments` | `dim_customer` | **YES** |
| **Customer Geography** | Customer distribution, total spend, and order volume grouped by Brazilian state | `backend/app/repositories/customer_repository.py` | `GET /api/v1/customers/geo` | `dim_customer`, `fact_orders` | **YES** |
| **Logistics Lead Times** | Average delivery time (12.5 days), estimated vs actual lead time, late shipment rate (6.6%) | `backend/app/repositories/logistics_repository.py` | `GET /api/v1/logistics/overview` | `fact_orders` | **YES** |
| **State Logistics** | Delivery speed, late delivery %, and carrier performance broken down by destination state | `backend/app/repositories/logistics_repository.py` | `GET /api/v1/logistics/by-state` | `analytics_obt_orders` | **YES** |
| **Seller Leaderboard** | Top sellers ranked by GMV, order count, average review score, and fulfillment delay rate | `backend/app/repositories/seller_repository.py` | `GET /api/v1/sellers/leaderboard` | `dim_seller`, `fact_order_items` | **YES** |
| **Data Quality Audit** | Total records, duplicate keys, null rates %, referential integrity status, overall quality score | `backend/app/repositories/data_quality_repository.py` | `GET /api/v1/data-quality/overview` | All 9 tables | **YES** |

---

## 8. FASTAPI BACKEND & REST API ENDPOINTS

The FastAPI application is launched from `backend/run.py` (running `backend.app.main:app`). It mounts 28 endpoints with automated Swagger UI (`/docs`), OpenAPI specifications (`/openapi.json`), and Redoc (`/redoc`).

### Request Lifecycle Architecture
```
HTTP Client (Frontend / Curl)
        │
        ▼
FastAPI Middleware (CORS + ProcessTimeHeaderMiddleware)
        │
        ▼
APIRouter (backend/app/api/v1/router.py)
        │
        ▼
Pydantic Request Validation (backend/app/schemas/*)
        │
        ▼
Service Layer (backend/app/services/*)
        │
        ├─► Database Repository (backend/app/repositories/*) -> SQLite (olistiq.db)
        ├─► ML Inference Service (ml/inference/ml_inference_service.py) -> Scikit-Learn
        └─► AI Analyst Service (ai_analyst/service.py) -> LangGraph Workflow
        │
        ▼
Pydantic Response Serialization & Enriched Headers
        │
        ▼
HTTP JSON Response
```

### Complete API Endpoint Catalog

| Endpoint | Method | Purpose | Route Module | Service | Data/Engine Source |
|---|---|---|---|---|---|
| `/health` | GET | System health & DB connection status | `backend/app/main.py` | Core | SQLite Engine |
| `/api/v1/dashboard/kpis` | GET | Executive high-level KPI cards | `v1/dashboard.py` | `DashboardService` | `DashboardRepository` |
| `/api/v1/dashboard/summary` | GET | Executive overview with recent trends | `v1/dashboard.py` | `DashboardService` | `DashboardRepository` |
| `/api/v1/analytics/revenue` | GET | Daily & monthly revenue time series | `v1/analytics.py` | `AnalyticsService` | `AnalyticsRepository` |
| `/api/v1/analytics/categories` | GET | Product category sales & ratings | `v1/analytics.py` | `AnalyticsService` | `AnalyticsRepository` |
| `/api/v1/analytics/payments` | GET | Payment method breakdowns & installments | `v1/analytics.py` | `AnalyticsService` | `AnalyticsRepository` |
| `/api/v1/analytics/insights` | GET | Heuristic business insights & alerts | `v1/analytics.py` | `AnalyticsService` | `AnalyticsRepository` |
| `/api/v1/customers/segments` | GET | Customer RFM segment distributions | `v1/customers.py` | `CustomerService` | `CustomerRepository` |
| `/api/v1/customers/geo` | GET | Geographic customer concentration | `v1/customers.py` | `CustomerService` | `CustomerRepository` |
| `/api/v1/customers/list` | GET | Paginated customer directory | `v1/customers.py` | `CustomerService` | `CustomerRepository` |
| `/api/v1/products/list` | GET | Paginated product catalog | `v1/products.py` | `ProductService` | `ProductRepository` |
| `/api/v1/sellers/leaderboard` | GET | Top merchant rankings & ratings | `v1/sellers.py` | `SellerService` | `SellerRepository` |
| `/api/v1/logistics/overview` | GET | Delivery lead times & delay rates | `v1/logistics.py` | `LogisticsService` | `LogisticsRepository` |
| `/api/v1/logistics/by-state` | GET | Delivery metrics by customer state | `v1/logistics.py` | `LogisticsService` | `LogisticsRepository` |
| `/api/v1/logistics/by-seller` | GET | Seller shipping performance | `v1/logistics.py` | `LogisticsService` | `LogisticsRepository` |
| `/api/v1/data-quality/overview` | GET | Table record counts & quality scores | `v1/data_quality.py` | `DataQualityService` | `DataQualityRepository` |
| `/api/v1/ml/models` | GET | List registered ML models & status | `v1/ml.py` | `MLInferenceService` | `ModelRegistry` |
| `/api/v1/ml/models/{model_name}` | GET | Detailed hyperparameters & metrics | `v1/ml.py` | `MLInferenceService` | `ModelRegistry` |
| `/api/v1/ml/segments` | GET | K-Means RFM segment profiles | `v1/ml.py` | `MLInferenceService` | `RFMClustering` |
| `/api/v1/ml/customers/{id}/segment` | GET | Individual customer segment lookup | `v1/ml.py` | `MLInferenceService` | `RFMClustering` |
| `/api/v1/ml/delivery-risk/predict` | POST | Real-time custom delay probability | `v1/ml.py` | `MLInferenceService` | `HistGradientBoosting` |
| `/api/v1/ml/delivery-risk/{order_id}` | GET | Historical order delay risk score | `v1/ml.py` | `MLInferenceService` | `HistGradientBoosting` |
| `/api/v1/ml/satisfaction-risk/{order_id}` | GET | Low review score (1-2 star) risk | `v1/ml.py` | `MLInferenceService` | `RandomForestClassifier` |
| `/api/v1/ml/forecast` | GET | 30-day ahead GMV & order forecast | `v1/ml.py` | `MLInferenceService` | `GradientBoostingRegressor` |
| `/api/v1/ml/anomalies` | GET | Historical volume & revenue anomalies | `v1/ml.py` | `MLInferenceService` | `BusinessAnomalyDetector` |
| `/api/v1/ai/query` | POST | Natural language AI Analyst query | `v1/ai.py` | `AIAnalystService` | `LangGraph StateGraph` |
| `/api/v1/ai/health` | GET | AI Analyst status & LLM connectivity | `v1/ai.py` | `AIAnalystService` | `AIAnalystService` |
| `/api/v1/ai/capabilities` | GET | Introspection of supported queries | `v1/ai.py` | `AIAnalystService` | `MetricCatalog` |

---

## 9. MACHINE LEARNING ENGINE MAP

The ML layer consists of 5 production models trained with strict chronological out-of-time splits (`2018-05-01`), eliminating target and feature leakage. All artifacts are registered in `ml/registry/artifacts/model_registry.json`.

```
                 ┌────────────────────────────────────────────────────────┐
                 │                ML INTELLIGENCE ENGINE                  │
                 └──────────────────────────┬─────────────────────────────┘
                                            │
        ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
        ▼                   ▼                               ▼                   ▼
┌───────────────┐   ┌───────────────┐               ┌───────────────┐   ┌───────────────┐
│ Customer RFM  │   │ Delivery Delay│               │ Satisfaction  │   │ Demand / GMV  │
│  Clustering   │   │  Classifier   │               │ Risk Predictor│   │  Forecaster   │
│   (K-Means)   │   │ (HistGradBst) │               │ (RandomForest)│   │(GradBst + Lag)│
└───────────────┘   └───────────────┘               └───────────────┘   └───────────────┘
```

### Model 1: Customer Segmentation (`customer_segmentation`)
- **Business Problem:** Segment 96,000+ customers by purchasing behavior for targeted marketing and retention.
- **Algorithm:** K-Means Clustering ($k=4$) with Log1p and StandardScaler transforms.
- **Features Used:** `recency_days`, `frequency`, `monetary_value_brl`, `category_diversity`.
- **Artifact:** `ml/registry/artifacts/customer_segmentation_v1.0.joblib` (384 KB).
- **Cluster Profiles:**
  1. *Champions / High-Value Active* (0.42%): Recency ~286d, Monetary R$2,193.
  2. *Loyal Multi-Category* (1.20%): Recency ~112d, Frequency > 2, Monetary R$815.
  3. *Recent Active One-Time* (51.3%): Recency ~125d, Monetary R$136.
  4. *Hibernating One-Time* (47.0%): Recency ~375d, Monetary R$137.
- **Status:** **COMPLETE**

### Model 2: Fulfillment Delivery Delay Risk (`delivery_risk`)
- **Business Problem:** Predict which orders will miss their estimated delivery date at checkout/pre-dispatch time.
- **Algorithm:** `HistGradientBoostingClassifier` with balanced class weights.
- **Features (Pre-Dispatch Only):** `total_items_price_brl`, `total_freight_value_brl`, `freight_ratio_pct`, `total_item_count`, `unique_product_count`, `haversine_distance_km`, `estimated_delivery_duration_days`, `max_product_weight_g`, `total_product_volume_cm3`, `seller_historical_delay_rate`, `purchase_month`, `purchase_dayofweek`, `purchase_hour`, `customer_state`, `seller_state`, `is_interstate_shipment`, `top_category_name`, `primary_payment_type`.
- **Target Leakage Prevention:** Post-dispatch variables (`order_delivered_carrier_date`, actual transit duration) are strictly forbidden.
- **Evaluation Metrics (Out-of-Time Test Set: 25,352 orders):** Accuracy 84.26%, ROC-AUC 0.7287, PR-AUC 0.1295, Recall 34.60%.
- **Artifact:** `ml/registry/artifacts/delivery_risk_v1.0.joblib` (403 KB).
- **Status:** **COMPLETE**

### Model 3: Customer Satisfaction / Low Review Risk (`satisfaction_risk`)
- **Business Problem:** Predict customer dissatisfaction (1-star or 2-star reviews) based on fulfillment friction.
- **Algorithm:** `RandomForestClassifier` ($n=100, \text{max\_depth}=10$).
- **Features:** `total_delivery_duration_days`, `delivery_delay_vs_estimated_days`, `freight_ratio_pct`, `total_items_price_brl`, `total_freight_value_brl`, `total_item_count`, `haversine_distance_km`, `seller_historical_review_score`, `is_delivered_late`, `is_interstate_shipment`, `primary_payment_type`, `top_category_name`, `customer_state`.
- **Evaluation Metrics (Test Set: 25,242 reviews):** Accuracy 84.07%, ROC-AUC 0.6862, PR-AUC 0.3003, Recall 40.67%.
- **Artifact:** `ml/registry/artifacts/satisfaction_risk_v1.0.joblib` (5.16 MB).
- **Status:** **COMPLETE**

### Model 4: 30-Day Demand & GMV Forecaster (`gmv_forecaster` & `orders_forecaster`)
- **Business Problem:** Forecast daily e-commerce GMV and order volumes 30 days ahead with confidence bands.
- **Algorithm:** `GradientBoostingRegressor` with Autoregressive Lags (`lag_1`, `lag_7`, `lag_14`, `lag_28`, `rolling_mean_7`, `rolling_std_7`, `rolling_mean_30`, calendar day/month/weekend features).
- **Evaluation Metrics (Out-of-Time Test Period: June–August 2018):**
  - GMV Forecaster: MAE R$5,998.72 ($23.21\%$ improvement over moving-average baseline), $R^2 = 0.6314$.
  - Orders Forecaster: MAE 37.03 orders ($20.91\%$ improvement over baseline), $R^2 = 0.3682$.
- **Artifacts:** `gmv_forecaster_v1.0.joblib` (294 KB), `orders_forecaster_v1.0.joblib` (297 KB).
- **Status:** **COMPLETE**

### Model 5: Business Anomaly Detection (`anomaly_detector`)
- **Business Problem:** Detect revenue drops, transaction surges, and fulfillment bottlenecks across daily operations.
- **Algorithm:** 30-day Rolling Z-Score ($|Z| > 2.5$) and multi-dimensional `IsolationForest`.
- **Artifact:** `ml/registry/artifacts/detected_anomalies.json` (contains Black Friday 2017 surge and logistical drop events).
- **Status:** **COMPLETE**

---

## 10. AI ANALYST / LANGGRAPH MULTI-NODE ARCHITECTURE

The OlistIQ AI Analyst is built with LangGraph (`StateGraph`). It provides safe Natural Language to SQL generation, schema retrieval, deterministic security guardrails, self-repair loops, and analytical insight synthesis.

```
                             User Question
                                   │
                                   ▼
                         ┌───────────────────┐
                         │  check_security   │
                         └─────────┬─────────┘
                                   │
                     [Pass]        │        [Fail / Adversarial]
             ┌─────────────────────┴─────────────────────┐
             ▼                                           ▼
   ┌───────────────────┐                       ┌───────────────────┐
   │  classify_intent  │                       │  format_response  │◄── (Rejection)
   └─────────┬─────────┘                       └───────────────────┘
             │                                           ▲
     [SQL]   │   [ML Route]                              │
     ┌───────┴───────┐                                   │
     │               ▼                                   │
     │     ┌───────────────────┐                         │
     │     │     route_ml      ├─────────────────────────┤
     │     └───────────────────┘                         │
     ▼                                                   │
┌───────────────────────────────┐                        │
│ retrieve_schema_and_metrics   │                        │
└────────────┬──────────────────┘                        │
             ▼                                           │
┌───────────────────────────────┐                        │
│       create_query_plan       │                        │
└────────────┬──────────────────┘                        │
             ▼                                           │
┌───────────────────────────────┐                        │
│         generate_sql          │                        │
└────────────┬──────────────────┘                        │
             ▼                                           │
┌───────────────────────────────┐                        │
│         validate_sql          │                        │
└────────────┬──────────────────┘                        │
             │                                           │
    [Valid]  ├────────────► [Invalid / Retry < 3] ───────┤
             │                      │                    │
             ▼                      ▼                    │
┌───────────────────┐     ┌───────────────────┐          │
│    execute_sql    │     │    repair_sql     │          │
└────────────┬──────┘     └─────────┬─────────┘          │
             │                      │                    │
    [Success]├────────► [Error] ────┘                    │
             │                                           │
             ▼                                           │
┌───────────────────┐                                    │
│ generate_insights │────────────────────────────────────┘
└───────────────────┘
```

### LangGraph Component Inventory

| Component / Node | Exact Source File | Purpose | Status |
|---|---|---|---|
| `check_security` | `ai_analyst/graph/nodes.py` | Screens query for SQL injection, jailbreaks, and prompt exfiltration. | **IMPLEMENTED** |
| `classify_intent` | `ai_analyst/graph/nodes.py` | Categorizes query into SQL analytics, ML prediction, or general FAQ. | **IMPLEMENTED** |
| `route_ml` | `ai_analyst/graph/nodes.py` | Dispatches query directly to ML inference service if question is ML-specific. | **IMPLEMENTED** |
| `retrieve_schema_and_metrics` | `ai_analyst/graph/nodes.py` | Retrieves relevant table DDLs and standardized business metric formulas. | **IMPLEMENTED** |
| `create_query_plan` | `ai_analyst/graph/nodes.py` | Constructs execution plan (tables, filters, dimensions, aggregates). | **IMPLEMENTED** |
| `generate_sql` | `ai_analyst/graph/nodes.py` | Generates SQLite query using LLM or deterministic few-shot templates. | **IMPLEMENTED** |
| `validate_sql` | `ai_analyst/graph/nodes.py` | Validates read-only status, AST structure, and table allowlists. | **IMPLEMENTED** |
| `repair_sql` | `ai_analyst/graph/nodes.py` | Feeds validation/execution errors back to LLM to fix syntax (up to 3 retries). | **IMPLEMENTED** |
| `execute_sql` | `ai_analyst/graph/nodes.py` | Runs verified query against SQLite database with a 5-second timeout. | **IMPLEMENTED** |
| `generate_insights` | `ai_analyst/graph/nodes.py` | Synthesizes numerical results into business insights and KPI takeaways. | **IMPLEMENTED** |
| `format_response` | `ai_analyst/graph/nodes.py` | Formats final JSON payload matching `AIQueryResponse` schema. | **IMPLEMENTED** |

---

## 11. SECURITY & GUARDRAILS SPECIFICATION

| Security Mechanism | Implementation File | Enforcement Strategy | Status |
|---|---|---|---|
| **Read-Only SQLite Access** | `ai_analyst/sql/executor.py` | SQLite connection opened with read-only query semantics; transactions rolled back. | **IMPLEMENTED** |
| **SQL AST Parser & Allowlist** | `ai_analyst/sql/validator.py` | Uses `sqlparse` to reject any statement starting with `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `ATTACH`, `PRAGMA`. | **IMPLEMENTED** |
| **Table Name Allowlist** | `ai_analyst/sql/validator.py` | Queries can only reference the 9 approved warehouse tables and 3 approved views. | **IMPLEMENTED** |
| **Hard Query Row Limit** | `ai_analyst/sql/validator.py` | Automatically injects `LIMIT 100` if not present to prevent Denial of Service memory exhaustion. | **IMPLEMENTED** |
| **Query Execution Timeout** | `ai_analyst/sql/executor.py` | Hard timeout of 5.0 seconds per SQL execution. | **IMPLEMENTED** |
| **Prompt Injection Filter** | `ai_analyst/security/guardrails.py` | Regex patterns and heuristic filters reject jailbreak phrases ("ignore previous instructions", "system prompt", etc.). | **IMPLEMENTED** |
| **Pydantic Validation** | `backend/app/schemas/*` | All incoming parameters, types, and ranges validated with standard HTTP 422 errors. | **IMPLEMENTED** |
| **CORS Policy** | `backend/app/main.py` | Strict allowed origins, headers, and methods configured. | **IMPLEMENTED** |

---

## 12. TESTING & QUALITY VERIFICATION MAP

**Test Framework:** Pytest 9.1.1  
**Execution Command:** `pytest -v`  
**Execution Result:** **65 Passed, 0 Failed, 0 Skipped** (54.32 seconds)

| Test Module | Test Count | Scope & Focus | Status |
|---|---|---|---|
| `tests/test_ai_analyst.py` | 14 tests | Security guardrails, prompt injection rejection, AST SQL validation, hybrid intent routing, end-to-end analytical query execution, and ML routing. | **PASSED** |
| `tests/test_ai_api.py` | 4 tests | AI Analyst REST endpoints: `/health`, `/capabilities`, `/query`, and adversarial injection rejection via HTTP. | **PASSED** |
| `tests/test_api_endpoints.py` | 17 tests | Dashboard KPIs, revenue trends, category performance, customer geo/segments, product listing, seller leaderboard, logistics. | **PASSED** |
| `tests/test_api_refinement.py` | 5 tests | Global error response schemas, `X-Process-Time` header, CORS headers, 404 responses, and OpenAPI schema completeness. | **PASSED** |
| `tests/test_data_quality.py` | 3 tests | Primary key uniqueness, foreign key referential integrity, and data quality score calculation across all 9 tables. | **PASSED** |
| `tests/test_idempotency.py` | 2 tests | ETL pipeline re-run safety, table record presence, and analytical view query accessibility. | **PASSED** |
| `tests/test_ingestion.py` | 2 tests | Verification that all 9 raw CSVs exist and contain required schema columns. | **PASSED** |
| `tests/test_ml_api.py` | 9 tests | ML model listing, model details, RFM segments, customer lookup, delivery risk, satisfaction risk, forecasting, anomalies. | **PASSED** |
| `tests/test_ml_models.py` | 6 tests | Strict target leakage prevention, K-Means clustering, HistGradientBoosting classifier, RandomForest review risk, forecaster. | **PASSED** |
| `tests/test_transformations.py` | 3 tests | Geolocation centroid aggregation, category Portuguese-to-English translation mapping, and calendar date dimension span. | **PASSED** |

---

## 13. DOCUMENTATION MAP

| Documentation File | Location | Content & Purpose | Status |
|---|---|---|---|
| `README.md` | Root | Project overview, quick start commands, and architecture overview. | **CURRENT** |
| `docs/ARCHITECTURE.md` | `docs/` | Comprehensive end-to-end technical architecture & design. | **CURRENT** |
| `docs/DATABASE_DESIGN.md` | `docs/` | Star schema physical DDL, ER diagrams, primary/foreign key mappings. | **CURRENT** |
| `docs/DATASET_PROFILING_REPORT.md` | `docs/` | Exploratory data analysis, null distributions, and data anomalies. | **CURRENT** |
| `docs/ETL_ARCHITECTURE.md` | `docs/` | ETL pipeline design, transformations, and loading strategies. | **CURRENT** |
| `docs/ETL_DATA_QUALITY_REPORT.md` | `docs/` | Data quality verification rules and validation results. | **CURRENT** |
| `docs/METRIC_DEFINITIONS.md` | `docs/` | Standard enterprise formulas for GMV, AOV, Lead Time, RFM. | **CURRENT** |
| `docs/BACKEND_ARCHITECTURE.md` | `docs/` | FastAPI structure, repository pattern, service design, middleware. | **CURRENT** |
| `docs/API_CONTRACT.md` | `docs/` | Complete REST API OpenAPI contracts, request/response models. | **CURRENT** |
| `docs/ML_ARCHITECTURE.md` | `docs/` | Machine learning system design, training workflows, inference facade. | **CURRENT** |
| `docs/ML_MODEL_CATALOG.md` | `docs/` | Detailed hyperparameters, algorithms, and training datasets for 5 models. | **CURRENT** |
| `docs/ML_FEATURE_CATALOG.md` | `docs/` | Catalog of engineered features, types, and derivations. | **CURRENT** |
| `docs/ML_DATA_LEAKAGE.md` | `docs/` | Strict rules preventing post-dispatch leakage in delivery risk models. | **CURRENT** |
| `docs/ML_EVALUATION_REPORT.md` | `docs/` | Benchmark metrics (Accuracy, F1, ROC-AUC, MAE, MAPE, $R^2$). | **CURRENT** |
| `docs/ML_API_CONTRACT.md` | `docs/` | ML REST API schemas and request/response specifications. | **CURRENT** |
| `docs/AI_ANALYST_ARCHITECTURE.md` | `docs/` | LangGraph multi-node agent architecture and state machine diagrams. | **CURRENT** |
| `docs/AI_ANALYST_SECURITY.md` | `docs/` | SQL security, AST parsing, prompt injection filters, and sandboxing. | **CURRENT** |
| `docs/AI_ANALYST_EVALUATION.md` | `docs/` | Natural Language to SQL benchmark evaluation and accuracy metrics. | **CURRENT** |
| `docs/AI_ANALYST_API_CONTRACT.md` | `docs/` | AI Analyst endpoint schemas, payloads, and error codes. | **CURRENT** |
| `docs/PHASE_5_COMPLETION_REPORT.md` | `docs/` | Phase 5 completion sign-off and verification report. | **CURRENT** |
| `docs/PHASE_6_COMPLETION_REPORT.md` | `docs/` | Phase 6 completion sign-off and verification report. | **CURRENT** |
| `docs/PHASE_7_COMPLETION_REPORT.md` | `docs/` | Phase 7 completion sign-off and verification report. | **CURRENT** |
| `docs/PHASE_8_COMPLETION_REPORT.md` | `docs/` | Phase 8 completion sign-off and verification report. | **CURRENT** |
| `docs/PHASE_9_COMPLETION_REPORT.md` | `docs/` | Phase 9 completion sign-off and verification report. | **CURRENT** |
| `docs/PHASE_10_COMPLETION_REPORT.md` | `docs/` | Phase 10 completion sign-off and deployment documentation. | **CURRENT** |

---

## 14. CONFIGURATION & ENVIRONMENT VARIABLES

All configuration variables are managed via `.env` (with template provided in `.env.example`).

| Variable | Default / Expected Value | Purpose | Sensitive? |
|---|---|---|---|
| `PROJECT_NAME` | `OlistIQ` | Application name identifier | No |
| `ENVIRONMENT` | `development` / `production` | Active runtime environment | No |
| `LOG_LEVEL` | `INFO` | Logging threshold | No |
| `DATABASE_URL` | `sqlite:///data/processed/olistiq.db` | SQLAlchemy SQLite warehouse connection string | No |
| `RAW_DATA_PATH` | `archive` | Path to raw Olist CSV datasets | No |
| `PROCESSED_DB_PATH` | `data/processed/olistiq.db` | Path to physical SQLite database file | No |
| `ML_ARTIFACTS_PATH` | `ml/registry/artifacts` | Path to serialized `.joblib` models | No |
| `LLM_PROVIDER` | `ollama` / `openai` | Active AI Analyst LLM provider | No |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint | No |
| `OLLAMA_MODEL` | `llama3.2` / `mistral` | Local Ollama model name | No |
| `OPENAI_API_KEY` | `[SECRET PRESENT — NOT DISPLAYED]` | Fallback OpenAI API key | **YES** |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI fallback model | No |
| `API_PORT` | `8000` | FastAPI HTTP listening port | No |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed frontend cross-origin origins | No |

---

## 15. DEPENDENCY MAP

### Python Dependencies (`requirements.txt`)
- `fastapi` & `uvicorn` — Async backend web framework and ASGI server.
- `sqlalchemy` — SQL query generation, connection pooling, and ORM abstractions.
- `pydantic` & `pydantic-settings` — Data parsing, DTO schemas, and environment management.
- `pandas` & `numpy` — Tabular data transformations, aggregation, and ETL processing.
- `scikit-learn` & `joblib` — Machine learning model training, clustering, regression, and model persistence.
- `langgraph` & `langchain-core` — Agentic state graph orchestration and multi-node workflow execution.
- `sqlparse` — SQL lexical parsing, AST validation, and statement filtering.
- `pytest` & `httpx` — Automated test suite and asynchronous API client testing.

### Frontend Dependencies (`frontend/package.json`)
- `react` (v18.2.0) & `react-dom` — Core UI component library.
- `vite` (v5.x) — High-performance frontend bundler and development server.
- `lucide-react` — Modern UI icon set.
- `recharts` (v2.12.0) — Declarative charting library for time series, bar charts, and pies.

---

## 16. END-TO-END DATA FLOW DIAGRAM

```
+-------------------------------------------------------------------------+
|                              DATA INGESTION                             |
|  Raw Olist CSVs (Customers, Orders, Items, Payments, Products, Reviews) |
+------------------------------------+------------------------------------+
                                     |
                                     ▼
+-------------------------------------------------------------------------+
|                        DIMENSIONAL ETL PIPELINE                         |
|  Quality Engine -> Geo Centroids -> Category Maps -> Fact/Dim Tables    |
+------------------------------------+------------------------------------+
                                     |
                                     ▼
+-------------------------------------------------------------------------+
|                     ANALYTICAL DATA WAREHOUSE (SQLite)                  |
|  5 Dimensions (Customer, Product, Seller, Geo, Date)                    |
|  4 Facts (Orders, Order Items, Payments, Reviews)                       |
|  3 Analytical Views (OBT, Daily Aggregations, Monthly Category Perf)   |
+-------------------+-------------------+-------------------+-------------+
                    |                   |                   |
                    ▼                   ▼                   ▼
+-----------------------+ +-----------------------+ +---------------------+
|   ANALYTICS ENGINE    | |     ML INTELLIGENCE   | |  AI ANALYST AGENT   |
|   Repositories & SQL  | |  5 Trained Pipelines  | |  LangGraph NL-to-SQL|
|   KPIs, Trends, RFM   | |  Risk, Forecast, Anom | |  Guardrails & Repair|
+-----------+-----------+ +-----------+-----------+ +----------+----------+
            |                         |                        |
            └─────────────────────────┼────────────────────────┘
                                      ▼
+-------------------------------------------------------------------------+
|                        FASTAPI REST BACKEND                             |
|  28 Endpoints, Pydantic DTOs, CORS, Timings, Exception Handling         |
+------------------------------------+------------------------------------+
                                     |
                                     ▼
+-------------------------------------------------------------------------+
|                        REACT 18 VITE FRONTEND                           |
|  9 Interactive Pages, Real-time Charts, AI Chat, ML Predictor Form      |
+-------------------------------------------------------------------------+
```

---

## 17. "WHERE DO I FIND WHAT?" QUICK DEVELOPER GUIDE

| Developer Question | Exact File / Directory Path |
|---|---|
| Where is the SQLite database connection established? | `database/connection.py` |
| Where is the database schema DDL defined? | `database/migrations/001_initial_schema.sql` & `database/schema.py` |
| Where is the analytical One Big Table (OBT) view defined? | `database/migrations/002_analytical_views.sql` |
| Where is the ETL pipeline started? | `scripts/run_etl.py` or `etl/pipelines/pipeline_runner.py` |
| Where are raw CSV files loaded? | `etl/ingestion/csv_reader.py` |
| Where is data quality validation performed? | `etl/validation/quality_engine.py` |
| Where is the customer RFM transformation? | `etl/transformations/customer_transform.py` |
| Where is the geolocation centroid deduplication? | `etl/transformations/geolocation_transform.py` |
| Where is product category translation handled? | `etl/transformations/product_transform.py` |
| Where are Executive Dashboard KPIs calculated? | `backend/app/repositories/dashboard_repository.py` |
| Where is revenue time series aggregated? | `backend/app/repositories/analytics_repository.py` |
| Where are ML models trained? | `ml/pipelines/train_all_models.py` |
| Where are trained ML artifacts loaded? | `ml/registry/model_registry.py` & `ml/inference/ml_inference_service.py` |
| Where is the delivery delay risk model implemented? | `ml/models/delivery_risk/delay_classifier.py` |
| Where is demand forecasting implemented? | `ml/models/forecasting/demand_forecaster.py` |
| Where is the FastAPI application created? | `backend/app/main.py` |
| Where are the REST API route definitions? | `backend/app/api/v1/router.py` |
| Where is the LangGraph AI Analyst workflow defined? | `ai_analyst/graph/workflow.py` |
| Where are the AI Analyst execution nodes? | `ai_analyst/graph/nodes.py` |
| Where is SQL generated from natural language? | `ai_analyst/sql/generator.py` |
| Where is SQL validated and sanitized? | `ai_analyst/sql/validator.py` |
| Where are AI security guardrails & prompt filters? | `ai_analyst/security/guardrails.py` |
| Where are environment variables configured? | `config/settings.py` & `.env` |
| Where are automated tests located? | `tests/` |
| Where is the React frontend entry point? | `frontend/src/main.jsx` & `frontend/src/App.jsx` |
| Where are frontend API client functions? | `frontend/src/api/domainApis.js` |

---

## 18. RUN COMMANDS

### 1. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Execute Dimensional ETL Pipeline
```bash
# Run full ETL to build olistiq.db
python scripts/run_etl.py
```

### 3. Train Machine Learning Models
```bash
# Train all 5 ML models and output artifacts to ml/registry/artifacts/
python ml/pipelines/train_all_models.py
```

### 4. Run Pytest Suite
```bash
# Run all 65 automated tests
pytest -v
```

### 5. Launch FastAPI Backend Server
```bash
# Start backend on http://localhost:8000
python backend/run.py
```

### 6. Launch React Frontend
```bash
# Start Vite dev server on http://localhost:5173
cd frontend
npm run dev
```

### 7. End-to-End Sanity Validation
```bash
# Verify database, ML inference, and AI Analyst components
python scripts/validate_e2e_integration.py
```

---

## 19. PROJECT COMPLETENESS AUDIT

| Component | Expected Deliverables | Actually Present in Codebase | Status |
|---|---|---|---|
| **Raw Datasets** | 9 Olist CSVs with translations | 9 CSVs in `archive/` (all verified) | **100% COMPLETE** |
| **ETL Pipeline** | Ingestion, validation, 9 transforms, DB loader | Complete modular pipeline in `etl/` | **100% COMPLETE** |
| **Database** | Star schema, 5 dims, 4 facts, 3 views | SQLite DB `data/processed/olistiq.db` (99.4K orders) | **100% COMPLETE** |
| **Analytics Engine** | KPIs, Revenue, Category, Payments, Logistics | Repositories & Services in `backend/app/` | **100% COMPLETE** |
| **FastAPI Backend** | 28 REST endpoints, CORS, timings, schemas | Full backend app in `backend/app/` | **100% COMPLETE** |
| **ML Models** | 5 models (RFM, Delay, Review, Forecast, Anomaly) | 5 models trained, serialized in `ml/registry/artifacts/` | **100% COMPLETE** |
| **AI Analyst** | LangGraph StateGraph, NL-to-SQL, Self-Repair | 11-node graph in `ai_analyst/` | **100% COMPLETE** |
| **Security** | Read-only SQL, allowlist, prompt filters | Guardrails and AST parser in `ai_analyst/security/` | **100% COMPLETE** |
| **Test Suite** | Comprehensive unit & integration tests | 65 automated tests in `tests/` (100% passing) | **100% COMPLETE** |
| **React Frontend** | Modern multi-page UI with Recharts & AI Chat | 9 full pages in `frontend/src/pages/` | **100% COMPLETE** |
| **Documentation** | Architectural specs, API contracts, guides | 25 detailed markdown guides in `docs/` | **100% COMPLETE** |

---

## 20. REMAINING GAPS & FUTURE ROADMAP

While all 11 core phases of OlistIQ are fully implemented and verified, the following optional production enhancements represent the logical next steps:

### Critical Gaps
*None.* The core data warehouse, ETL, ML pipelines, AI analyst, backend APIs, and frontend are fully implemented, functional, and tested.

### Important Enhancements (Future Production Scalability)
1. **PostgreSQL / DuckDB Migration:** While SQLite is self-contained and fast for local execution, upgrading to DuckDB or PostgreSQL in a containerized Docker setup would enable parallel multi-threaded analytical queries.
2. **Streaming Ingestion:** Replace batch CSV ingestion with Kafka/RabbitMQ message ingestion for live order events.
3. **Advanced LLM Embeddings / Vector Store:** Enhance the Schema Store with ChromaDB / FAISS vector indexing for semantic table and column search across hundreds of tables.

### Optional Enhancements
1. **User Authentication & RBAC:** Add OAuth2 / JWT authentication to restrict administrative ML retraining endpoints.
2. **Automated Model Retraining Trigger:** Configure Airflow or cron-scheduled jobs to trigger `train_all_models.py` when data drift exceeds thresholds.

---

## 21. INTERVIEW & TECHNICAL DEMO TALKING POINTS

### 1. One-Line Project Pitch
> *"OlistIQ is an end-to-end, enterprise e-commerce decision intelligence platform that combines an analytical star-schema warehouse, five predictive machine learning models, a secure 11-node LangGraph AI Analyst with self-repairing SQL generation, and a modern React dashboard."*

### 2. Core Problem Solved
E-commerce executives struggle to extract fast, trustworthy insights from fragmented relational transaction data. Traditional BI dashboards are static, while raw LLMs frequently hallucinate SQL syntax, invent fake tables, or leak confidential data. OlistIQ solves this by unifying clean dimensional modeling, strict target-leakage-free predictive ML, and an autonomous AI agent constrained by deterministic security guardrails.

### 3. Key Technical Challenges & Engineering Solutions
- **The Geolocation Row Multiplication Bug:** Raw Olist geolocation data contained over 1 million repeated zip code rows. Directly joining this would cause catastrophic cartesian row explosion.  
  *Solution:* Built `geolocation_transform.py` to aggregate zip codes into distinct centroid coordinates using mean latitude and longitude grouped strictly by 5-digit zip code.
- **Machine Learning Data Leakage Prevention:** Delivery delay models often accidentally train on post-dispatch features (e.g., actual shipping date), resulting in artificially inflated test accuracy that fails in production.  
  *Solution:* Implemented `ml/features/definitions.py` with strict pre-dispatch temporal boundaries, evaluating models on chronological out-of-time test splits (`2018-05-01`).
- **Deterministic SQL Generation & Self-Repair:** Standard text-to-SQL agents fail when LLMs make syntax mistakes or touch restricted tables.  
  *Solution:* Designed an 11-node LangGraph state machine where SQL queries pass through an AST validator (`sqlparse`). If syntax or schema errors occur, the error is fed back to the `repair_sql` node in a closed loop (up to 3 attempts) before query execution.
- **Database Safety & Prompt Injection:** Preventing adversarial users from running destructive DDL/DML.  
  *Solution:* Read-only database connection pooling, table allowlists, hard row limits (`LIMIT 100`), 5-second query timeouts, and regex-based prompt injection filters.

---

## 22. MASTER ARCHITECTURE MAP

```
================================================================================
                                PROJECT: OLISTIQ
================================================================================
  │
  ├── 1. DATA LAYER
  │   ├── Raw CSVs: archive/ (9 datasets, 100K+ records)
  │   └── Status: COMPLETE
  │
  ├── 2. ETL LAYER
  │   ├── Code: etl/ingestion/, etl/transformations/, etl/validation/, etl/loaders/
  │   ├── Features: Geo centroid deduplication, category translations, RFM metrics
  │   └── Status: COMPLETE
  │
  ├── 3. DATABASE LAYER
  │   ├── Warehouse: data/processed/olistiq.db (SQLite)
  │   ├── Schema: 5 Dimension tables, 4 Fact tables, 3 Analytical Views
  │   └── Status: COMPLETE
  │
  ├── 4. ANALYTICS LAYER
  │   ├── Repositories: backend/app/repositories/
  │   ├── Metrics: Executive KPIs, Revenue trends, Category ratings, Lead times
  │   └── Status: COMPLETE
  │
  ├── 5. MACHINE LEARNING LAYER
  │   ├── Code: ml/models/, ml/pipelines/, ml/inference/, ml/registry/
  │   ├── Models: K-Means RFM, HistGradBoost Delay, RandomForest Review, GradBoost Forecast
  │   └── Status: COMPLETE
  │
  ├── 6. AI ANALYST LAYER
  │   ├── Code: ai_analyst/graph/, ai_analyst/sql/, ai_analyst/security/, ai_analyst/insights/
  │   ├── Architecture: 11-Node LangGraph StateGraph, AST Validator, Self-Repair
  │   └── Status: COMPLETE
  │
  ├── 7. API / BACKEND LAYER
  │   ├── Framework: FastAPI (backend/app/)
  │   ├── Routes: 28 REST endpoints across 9 domain routers
  │   └── Status: COMPLETE
  │
  ├── 8. FRONTEND LAYER
  │   ├── Framework: React 18 + Vite (frontend/src/)
  │   ├── Pages: 9 pages (Dashboard, Analytics, Customers, Sellers, Logistics, Quality, ML, AI, Health)
  │   └── Status: COMPLETE
  │
  └── 9. VERIFICATION & TESTING LAYER
      ├── Suite: tests/ (11 test files)
      ├── Results: 65/65 Tests Passed (100%)
      └── Status: COMPLETE
================================================================================
```
