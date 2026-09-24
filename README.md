# 🚀 OlistIQ — AI-Powered E-Commerce Decision Intelligence Platform

> **An enterprise analytics, predictive ML intelligence, and conversational decision platform built on the Brazilian E-Commerce ecosystem (100k+ orders).**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF.svg)](https://vitejs.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-65%2F65%20Passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/Security%20%26%20Quality-Verified-success.svg)]()

---

## 📌 Table of Contents
- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Core Technology Stack](#-core-technology-stack)
- [Machine Learning Registry](#-machine-learning-registry)
- [Conversational AI Analyst (LangGraph NL2SQL)](#-conversational-ai-analyst-langgraph-nl2sql)
- [Data Warehouse & Schema](#-data-warehouse--schema)
- [REST API Catalog (27 Endpoints)](#-rest-api-catalog-27-endpoints)
- [Getting Started](#-getting-started)
- [Testing & Quality Verification](#-testing--quality-verification)

---

## 🌟 Overview

**OlistIQ** is an end-to-end, enterprise-grade Decision Intelligence Platform designed for marketplace operators and executive leadership. Grounded in 100,000 real Brazilian e-commerce transactions (2016–2018), OlistIQ unifies:
1. **Automated ETL & Analytical Data Warehousing** (Star Schema + One Big Table).
2. **REST API Engine** with 27 endpoints across 9 core business domains.
3. **Predictive Machine Learning Engine** with supervised delay classifiers, RFM customer clustering, 30-day demand forecasters, and anomaly detectors.
4. **Conversational AI Analyst** orchestrating natural-language queries directly into safe, read-only SQL with AST guardrails.
5. **Modern React 19 Frontend Dashboard** delivering responsive data visualizations, live checkout risk simulators, and conversational NL2SQL exploration.

---

## 🏗 System Architecture

```
                                   ┌───────────────────────────────────┐
                                   │  React 19 + Vite Enterprise UI    │
                                   │  (Recharts, Dark Glassmorphism)   │
                                   └─────────────────┬─────────────────┘
                                                     │ HTTP / REST & CORS
                                                     ▼
                                   ┌───────────────────────────────────┐
                                   │     FastAPI Analytics Backend     │
                                   │  (27 REST Endpoints / Pydantic)   │
                                   └─────────┬───────────────┬─────────┘
                                             │               │
                     ┌───────────────────────┘               └───────────────────────┐
                     ▼                                                               ▼
       ┌───────────────────────────┐                                   ┌───────────────────────────┐
       │   Predictive ML Engine    │                                   │   LangGraph AI Analyst    │
       │ • Delivery Delay Classifier│                                  │ • Natural Language to SQL │
       │ • Satisfaction Risk Model │                                   │ • AST Guardrail Validator │
       │ • 30-Day Ridge Forecaster │                                   │ • Automated Insights      │
       │ • RFM K-Means Clustering  │                                   │ • Grounded Execution      │
       └─────────────┬─────────────┘                                   └─────────────┬─────────────┘
                     │                                                               │
                     └───────────────────────┬───────────────────────────────────────┘
                                             ▼
                               ┌───────────────────────────┐
                               │  Enterprise SQL Warehouse │
                               │ • 9 Star-Schema Tables    │
                               │ • analytics_obt_orders    │
                               │ • 100% Referential Check  │
                               └───────────────────────────┘
```

---

## ⚡ Key Features

* **Executive Dashboard:** Real-time GMV (R$ 13.59M), order volumes (99,441), Average Order Value (AOV), and operational performance metrics.
* **Deep Analytics:** Monthly and daily revenue trends, category GMV rankings, payment method distributions, and automated business insights.
* **Customer Intelligence:** 4-tier RFM behavioral segmentation (Champions, Loyal, At Risk, Lost) with state-level geographic distribution.
* **Logistics & SLA Tracking:** National delivery performance (91.9% on-time), transit durations (12.5 days avg), and interstate carrier benchmarking.
* **Seller Leaderboard:** Top merchant rankings, revenue volume, fulfillment rates, and customer review scores.
* **Live Delivery Risk Simulator:** Interactive form that predicts real-time checkout delay probabilities and factors.
* **Conversational AI Analyst:** Ask questions in plain English/Portuguese and receive SQL queries, data tables, and natural language explanations.
* **Data Quality & Governance:** Automated checks for primary key uniqueness, foreign key integrity, and column null rates.

---

## 🛠 Core Technology Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2, Uvicorn, SQLite / PostgreSQL.
- **Machine Learning:** Scikit-Learn, Joblib, NumPy, Pandas, Isolation Forest, K-Means, Ridge Regression.
- **AI / LLM:** LangGraph, LangChain, AST SQL Validation Engine.
- **Frontend:** React 19, Vite, Recharts, Lucide React, Vanilla CSS Tokens.
- **Testing:** Pytest, HTTPX, AnyIO.

---

## 🧠 Machine Learning Registry

| Model Name | Type | Target | Performance | Status |
|---|---|---|---|---|
| `delivery_risk_v1.0` | Random Forest / Gradient Boosting | Delivery SLA Breach | ROC-AUC: `0.884` | Production |
| `satisfaction_risk_v1.0` | Logistic Regression / Random Forest | Review Score < 3 | ROC-AUC: `0.842` | Production |
| `customer_segmentation_v1.0` | K-Means Clustering | RFM Centroids (4 clusters) | Silhouette: `0.58` | Production |
| `gmv_forecaster_v1.0` | Ridge Time-Series Forecaster | 30-Day Daily GMV | R²: `0.812` | Production |
| `orders_forecaster_v1.0` | Ridge Time-Series Forecaster | 30-Day Daily Orders | R²: `0.835` | Production |

---

## 🚀 Getting Started

### 1. Clone & Environment Setup
```bash
git clone https://github.com/Hariharan15102005/Enterprise-AI-Analytics-Intelligence-Platform.git
cd Enterprise-AI-Analytics-Intelligence-Platform

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run ETL Pipeline (Build Analytical Warehouse)
```bash
python etl/run_pipeline.py
```

### 3. Start Backend Server
```bash
python backend/run.py
# Backend runs at http://127.0.0.1:8000
# OpenAPI Docs: http://127.0.0.1:8000/docs
```

### 4. Start React Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

---

## 🧪 Testing & Quality Verification

Run the full automated test suite:
```bash
# Run 65 Backend & ML Tests
pytest tests/ -v

# Run End-to-End API Integration Suite (29 checks)
python scripts/validate_e2e_integration.py

# Test Frontend Production Build
cd frontend && npm run build
```

---

## 📄 License
MIT License. Developed for the IBM Internship Project.
