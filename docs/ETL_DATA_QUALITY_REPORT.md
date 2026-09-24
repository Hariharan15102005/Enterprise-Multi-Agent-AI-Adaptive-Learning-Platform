# OlistIQ — ETL Data Quality & Validation Audit Report

**Pipeline Execution Status:** SUCCESS  
**Overall Data Quality Score:** **100.0 / 100.0**  
**Execution Timestamp:** September 2026  
**Pipeline Run Duration:** ~128.6 seconds  
**Target Database:** `data/processed/olistiq.db` (PostgreSQL DDL Ready)  

---

## 1. Raw Ingestion vs. Final Loaded Row Counts Reconciliation

| Table / Entity | Raw Source CSV | Raw Row Count | Final Database Table | Final Loaded Rows | Reconciliation Status | Notes & Filtering Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Geolocation** | `olist_geolocation_dataset.csv` | 1,000,163 | `dim_geolocation` | **19,010** | **Reconciled (Aggregated)** | 261,831 duplicate rows and coordinate outliers outside Brazil boundary box were cleaned; aggregated to 1 row per unique postal code prefix. |
| **Customers** | `olist_customers_dataset.csv` | 99,441 | `dim_customer` | **96,096** | **Reconciled (Deduplicated Entity)** | 99,441 order tokens resolved into 96,096 unique physical consumer entities with RFM scores. |
| **Products** | `olist_products_dataset.csv` | 32,951 | `dim_product` | **32,951** | **100% Exact Match** | All 32,951 products mapped to English categories, physical volume, and size tiers. |
| **Sellers** | `olist_sellers_dataset.csv` | 3,095 | `dim_seller` | **3,095** | **100% Exact Match** | All 3,095 sellers geocoded and assigned performance tiers. |
| **Calendar** | Generated Programmatically | N/A | `dim_date` | **1,461** | **Generated (100% Valid)** | Continuous calendar from 2016-01-01 to 2019-12-31 with Brazilian holidays. |
| **Orders** | `olist_orders_dataset.csv` | 99,441 | `fact_orders` | **99,441** | **100% Exact Match** | Header grain with parsed timestamps, basket financials, and review scores. |
| **Order Items** | `olist_order_items_dataset.csv` | 112,650 | `fact_order_items` | **112,650** | **100% Exact Match** | Line-item grain with Haversine transit distance (km) and delivery SLA flags. |
| **Payments** | `olist_order_payments_dataset.csv` | 103,886 | `fact_payments` | **103,886** | **100% Exact Match** | Payment sequence, tender type, and installment counts. |
| **Reviews** | `olist_order_reviews_dataset.csv` | 99,224 | `fact_reviews` | **99,224** | **100% Exact Match** | Review score, sentiment classification, and response latency. |

---

## 2. Automated Validation Assertions Results

| Check Rule | Target Dataset / Table | Severity | Affected Rows | Status | Message |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Key Uniqueness** | `orders.order_id` | CRITICAL | 0 (0.00%) | **PASSED** | PK uniqueness verified; 0 duplicate instances. |
| **Primary Key Uniqueness** | `products.product_id` | CRITICAL | 0 (0.00%) | **PASSED** | PK uniqueness verified; 0 duplicate instances. |
| **Primary Key Uniqueness** | `sellers.seller_id` | CRITICAL | 0 (0.00%) | **PASSED** | PK uniqueness verified; 0 duplicate instances. |
| **Referential Integrity** | `orders.customer_id` $\rightarrow$ `customers.customer_id` | ERROR | 0 (0.00%) | **PASSED** | 100% referential integrity match (0 orphans). |
| **Referential Integrity** | `order_items.product_id` $\rightarrow$ `products.product_id` | ERROR | 0 (0.00%) | **PASSED** | 100% referential integrity match (0 orphans). |
| **Numeric Range Constraint** | `order_items.price` $\ge 0.0$ | WARNING | 0 (0.00%) | **PASSED** | All item prices within valid bounds [0.0, 100000.0]. |
| **Numeric Range Constraint** | `order_reviews.review_score` $\in [1, 5]$ | WARNING | 0 (0.00%) | **PASSED** | All review scores within valid integer range [1, 5]. |

---

## 3. Data Cleansing & Normalization Summary

1. **Category Mapping Coverage:** 100% of product categories successfully normalized to English (including `gaming_pc` and `small_kitchen_appliances`).
2. **Geospatial Outlier Handling:** 100% of invalid coordinate samples outside Brazil boundary box were safely filtered prior to centroid calculation.
3. **Customer Identity Resolution:** Customer profiles cleanly unified under `customer_unique_id` with repeat buyer flags and RFM quartiles.
4. **Analytical Views Verification:** `analytics_obt_orders`, `agg_daily_sales_ops`, and `agg_monthly_category_perf` instantiated and queryable.
