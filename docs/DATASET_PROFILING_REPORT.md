# Enterprise Dataset Discovery & Technical Profiling Report
## AI-Powered E-Commerce Decision Intelligence Platform (Olist Dataset)

**Project:** Olist Brazilian E-Commerce Analytics & Decision Intelligence  
**Author:** Antigravity Data Intelligence & Architecture  
**Status:** Completed & Validated  
**Date:** September 2026  

---

## Executive Summary

This report delivers a technical profiling, referential integrity audit, and analytical evaluation of the **9 CSV datasets** comprising the Brazilian E-Commerce Public Dataset by Olist (located in `archive/`). 

The primary objective is to lay the empirical foundation for building an **Enterprise AI-Powered E-Commerce Decision Intelligence Platform**. No code, schema, or machine learning model is constructed on assumptions; every observation, statistic, join path, and constraint in this document is validated against the raw data.

### Global Dataset Metrics at a Glance

| Dataset | Row Count | Column Count | Primary Key / Grain | Missing Cells (%) | Duplicate Rows |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`olist_customers_dataset.csv`** | 99,441 | 5 | `customer_id` (Order-Customer token) | 0.00% | 0 |
| **`olist_geolocation_dataset.csv`** | 1,000,163 | 5 | Composite (`zip_code`, `lat`, `lng`) | 0.00% | 261,831 (26.18%) |
| **`olist_order_items_dataset.csv`** | 112,650 | 7 | Composite (`order_id`, `order_item_id`) | 0.00% | 0 |
| **`olist_order_payments_dataset.csv`** | 103,886 | 5 | Composite (`order_id`, `payment_sequential`) | 0.00% | 0 |
| **`olist_order_reviews_dataset.csv`** | 99,224 | 7 | `review_id` (approximate grain) | 21.01% (text cols) | 0 |
| **`olist_orders_dataset.csv`** | 99,441 | 8 | `order_id` | 0.62% (timestamps) | 0 |
| **`olist_products_dataset.csv`** | 32,951 | 9 | `product_id` | 1.85% (attributes) | 0 |
| **`olist_sellers_dataset.csv`** | 3,095 | 4 | `seller_id` | 0.00% | 0 |
| **`product_category_name_translation.csv`** | 71 | 2 | `product_category_name` | 0.00% | 0 |

---

## Section 1: Detailed Table-by-Table Technical Profiling

---

### 1. `olist_customers_dataset.csv`

- **Purpose:** Maps order-level customer instances to real unique consumer entities and geographic locations.
- **Total Records:** 99,441 rows | 5 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Potential Primary Key:** `customer_id` (Unique Count: 99,441 — 100% unique per order).
- **Core Entity Key:** `customer_unique_id` (Unique Count: 96,096).
  - Repeat customers: 2,997 consumers placed > 1 order (Max orders by a single customer: 17).

#### Column Specifications & Profiling

| Column Name | Data Type | Missing Count (%) | Unique Values | Distribution / Top Values |
| :--- | :--- | :--- | :--- | :--- |
| `customer_id` | string | 0 (0.0%) | 99,441 | 100% unique alphanumeric UUID tokens |
| `customer_unique_id` | string | 0 (0.0%) | 96,096 | Top: `8d50f5...` (17), `3e43e6...` (9), `1b6c75...` (7) |
| `customer_zip_code_prefix` | integer | 0 (0.0%) | 14,994 | Range: [1003 to 99990], Mean: 35,137, Median: 24,416 |
| `customer_city` | string | 0 (0.0%) | 4,119 | Sao Paulo (15,540), Rio de Janeiro (6,882), Belo Horizonte (2,773) |
| `customer_state` | string | 0 (0.0%) | 27 | SP (41.98%), RJ (12.92%), MG (11.70%), RS (5.50%), PR (5.07%) |

---

### 2. `olist_orders_dataset.csv`

- **Purpose:** Central transaction backbone capturing order status lifecycles and milestone timestamps.
- **Total Records:** 99,441 rows | 8 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Primary Key:** `order_id` (100% unique).
- **Foreign Key:** `customer_id` (1:1 referential match with `olist_customers_dataset.csv`).

#### Column Specifications & Profiling

| Column Name | Data Type | Missing Count (%) | Unique Values | Summary Statistics / Date Ranges |
| :--- | :--- | :--- | :--- | :--- |
| `order_id` | string | 0 (0.0%) | 99,441 | 100% unique transaction UUIDs |
| `customer_id` | string | 0 (0.0%) | 99,441 | Exact 1:1 foreign key match to customers |
| `order_status` | string | 0 (0.0%) | 8 | delivered: 96,478 (97.02%), shipped: 1,107, canceled: 625, unavailable: 609, invoiced: 314, processing: 301, created: 5, approved: 2 |
| `order_purchase_timestamp` | datetime | 0 (0.0%) | 98,875 | Min: `2016-09-04 21:15:19`, Max: `2018-10-17 17:30:18` |
| `order_approved_at` | datetime | 160 (0.16%) | 90,733 | Min: `2016-09-15 12:16:38`, Max: `2018-09-03 17:40:06` |
| `order_delivered_carrier_date` | datetime | 1,783 (1.79%) | 81,018 | Min: `2016-10-08 10:34:01`, Max: `2018-09-11 19:48:28` |
| `order_delivered_customer_date` | datetime | 2,965 (2.98%) | 95,664 | Min: `2016-10-11 13:46:32`, Max: `2018-10-17 13:22:46` |
| `order_estimated_delivery_date` | datetime | 0 (0.0%) | 459 | Min: `2016-09-30 00:00:00`, Max: `2018-11-12 00:00:00` |

---

### 3. `olist_order_items_dataset.csv`

- **Purpose:** Line-item level details associating ordered products, fulfilling sellers, pricing, and freight.
- **Total Records:** 112,650 rows | 7 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Primary Key:** Composite (`order_id`, `order_item_id`).
- **Foreign Keys:**
  - `order_id` $\rightarrow$ `olist_orders_dataset.order_id` (98,666 distinct orders; 775 orders without items due to cancellation/unavailability).
  - `product_id` $\rightarrow$ `olist_products_dataset.product_id` (32,951 distinct products, 100% matched).
  - `seller_id` $\rightarrow$ `olist_sellers_dataset.seller_id` (3,095 distinct sellers, 100% matched).

#### Column Specifications & Numerical Profiling

| Column Name | Data Type | Missing Count | Min | 25% | Median | Mean | 75% | Max | IQR Outliers (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | string | 0 (0.0%) | - | - | - | - | - | - | - |
| `order_item_id` | integer | 0 (0.0%) | 1 | 1 | 1 | 1.20 | 1 | 21 | 13,984 (12.41%) |
| `product_id` | string | 0 (0.0%) | - | - | - | - | - | - | - |
| `seller_id` | string | 0 (0.0%) | - | - | - | - | - | - | - |
| `shipping_limit_date` | datetime | 0 (0.0%) | `2016-09-19` | - | - | - | - | `2020-04-09` | Outlier date 2020 |
| `price` (BRL) | float | 0 (0.0%) | R$ 0.85 | R$ 39.90 | R$ 74.99 | R$ 120.65 | R$ 134.90 | R$ 6,735.00 | 8,427 (7.48%) |
| `freight_value` (BRL) | float | 0 (0.0%) | R$ 0.00 | R$ 13.08 | R$ 16.26 | R$ 19.99 | R$ 21.15 | R$ 409.68 | 12,134 (10.77%) |

---

### 4. `olist_order_payments_dataset.csv`

- **Purpose:** Financial transactions, payment methods, installments, and monetary settlements per order.
- **Total Records:** 103,886 rows | 5 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Primary Key:** Composite (`order_id`, `payment_sequential`).
- **Foreign Key:** `order_id` $\rightarrow$ `olist_orders_dataset.order_id` (99,440 distinct orders; exactly 1 order in orders has zero payment record).

#### Column Specifications & Numerical Profiling

| Column Name | Data Type | Missing Count | Min | 25% | Median | Mean | 75% | Max | IQR Outliers (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | string | 0 (0.0%) | - | - | - | - | - | - | - |
| `payment_sequential` | integer | 0 (0.0%) | 1 | 1 | 1 | 1.09 | 1 | 29 | 4,526 (4.36%) |
| `payment_type` | string | 0 (0.0%) | Categorical: `credit_card` (73.92%), `boleto` (19.04%), `voucher` (5.56%), `debit_card` (1.47%), `not_defined` (3 rows) |
| `payment_installments`| integer | 0 (0.0%) | 0 | 1 | 1 | 2.85 | 4 | 24 | 6,313 (6.08%) |
| `payment_value` (BRL) | float | 0 (0.0%) | R$ 0.00 | R$ 56.79 | R$ 100.00 | R$ 154.10 | R$ 171.84 | R$ 13,664.08 | 7,981 (7.68%) |

---

### 5. `olist_order_reviews_dataset.csv`

- **Purpose:** Customer feedback, satisfaction scores (1–5), survey timestamps, and text reviews.
- **Total Records:** 99,224 rows | 7 columns
- **Duplicate Records:** 0 full duplicates, but **814 non-unique `review_id` instances** (shared across multiple orders or re-submitted).
- **Foreign Key:** `order_id` $\rightarrow$ `olist_orders_dataset.order_id` (98,673 unique orders; 547 orders have multiple review entries).

#### Column Specifications & Profiling

| Column Name | Data Type | Missing Count (%) | Unique Values | Distribution / Metrics |
| :--- | :--- | :--- | :--- | :--- |
| `review_id` | string | 0 (0.0%) | 98,410 | Top IDs repeat up to 3 times |
| `order_id` | string | 0 (0.0%) | 98,673 | 547 orders with $\ge 2$ reviews |
| `review_score` | integer | 0 (0.0%) | 5 | **5★:** 57,328 (57.78%), **4★:** 19,142 (19.29%), **1★:** 11,424 (11.51%), **3★:** 8,179 (8.24%), **2★:** 3,151 (3.18%). Mean: 4.09★ |
| `review_comment_title` | string | 87,656 (88.34%) | 4,527 | Top: `Recomendo` (423), `Bom` (293), `super recomendo` (270) |
| `review_comment_message`| string | 58,247 (58.70%) | 36,159 | Top: `Muito bom` (230), `Bom` (189), `muito bom` (122) |
| `review_creation_date` | datetime | 0 (0.0%) | 636 | Min: `2016-10-02`, Max: `2018-08-31` |
| `review_answer_timestamp`| datetime| 0 (0.0%) | 98,248 | Min: `2016-10-07 18:32:28`, Max: `2018-10-29 12:27:35` |

---

### 6. `olist_products_dataset.csv`

- **Purpose:** Product catalog metadata including physical dimensions, weights, and category taxonomies.
- **Total Records:** 32,951 rows | 9 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Primary Key:** `product_id` (32,951 unique — 100% uniqueness).

#### Column Specifications & Profiling

| Column Name | Data Type | Missing Count (%) | Min | Median | Mean | Max | Outliers (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | string | 0 (0.0%) | - | - | - | - | - |
| `product_category_name` | string | 610 (1.85%) | 73 distinct categories (Top: cama_mesa_banho: 3029, esporte_lazer: 2867) |
| `product_name_lenght` | float | 610 (1.85%) | 5 | 51 | 48.48 | 76 | 290 (0.90%) |
| `product_description_lenght`| float| 610 (1.85%) | 4 | 595 | 771.50 | 3,992 | 2,078 (6.43%) |
| `product_photos_qty` | float | 610 (1.85%) | 1 | 1 | 2.19 | 20 | 849 (2.63%) |
| `product_weight_g` | float | 2 (0.01%) | 0 g | 700 g | 2,276.47 g | 40,425 g | 4,551 (13.81%) |
| `product_length_cm` | float | 2 (0.01%) | 7 cm | 25 cm | 30.82 cm | 105 cm | 1,380 (4.19%) |
| `product_height_cm` | float | 2 (0.01%) | 2 cm | 13 cm | 16.94 cm | 105 cm | 1,892 (5.74%) |
| `product_width_cm` | float | 2 (0.01%) | 6 cm | 20 cm | 23.20 cm | 118 cm | 912 (2.77%) |

---

### 7. `olist_sellers_dataset.csv`

- **Purpose:** Merchant directory and fulfillment hub locations.
- **Total Records:** 3,095 rows | 4 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Primary Key:** `seller_id` (3,095 unique — 100% uniqueness).

#### Column Specifications & Profiling

| Column Name | Data Type | Missing Count (%) | Unique Values | Distribution / Top Values |
| :--- | :--- | :--- | :--- | :--- |
| `seller_id` | string | 0 (0.0%) | 3,095 | 100% unique merchant UUIDs |
| `seller_zip_code_prefix` | integer | 0 (0.0%) | 2,246 | Range: [1001 to 99730], Mean: 32,291, Median: 14,940 |
| `seller_city` | string | 0 (0.0%) | 611 | Sao Paulo (694), Curitiba (127), Rio de Janeiro (96), Belo Horizonte (68) |
| `seller_state` | string | 0 (0.0%) | 23 | SP (59.74%), PR (11.28%), MG (7.88%), SC (6.14%), RJ (5.53%) |

---

### 8. `olist_geolocation_dataset.csv`

- **Purpose:** Geospatial coordinate mapping (latitude, longitude, municipality) for 5-digit Brazilian postal code prefixes.
- **Total Records:** 1,000,163 rows | 5 columns
- **Duplicate Records:** **261,831 rows (26.18%) are exact duplicates**.
- **Unique Zip Code Prefixes:** 19,015.

#### Column Specifications & Profiling

| Column Name | Data Type | Missing Count | Min | Median | Mean | Max | Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `geolocation_zip_code_prefix` | integer | 0 (0.0%) | 1001 | 26530 | 36574.17 | 99990 | 19,015 unique postal prefixes |
| `geolocation_lat` | float | 0 (0.0%) | -36.61 | -22.92 | -21.18 | +45.07 | Outliers outside Brazil bounds (Lat > +5.27) |
| `geolocation_lng` | float | 0 (0.0%) | -101.47 | -46.64 | -46.39 | +121.11 | Outliers outside Brazil bounds (Lng > -34.79 or < -73.98) |
| `geolocation_city` | string | 0 (0.0%) | - | - | - | - | 8,011 variations (contains accent discrepancies) |
| `geolocation_state` | string | 0 (0.0%) | - | - | - | - | 27 Federative Units of Brazil |

---

### 9. `product_category_name_translation.csv`

- **Purpose:** Cross-reference dictionary mapping Portuguese product category slugs to English labels.
- **Total Records:** 71 rows | 2 columns
- **Duplicate Records:** 0 rows (0.00%)
- **Primary Key:** `product_category_name` (71 unique).

---

## Section 2: Entity-Relationship & Validated Join Paths

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : "places (1:1 per order instance)"
    ORDERS ||--|{ ORDER_ITEMS : "contains (1:N)"
    ORDERS ||--|{ ORDER_PAYMENTS : "paid via (1:N)"
    ORDERS ||--o{ ORDER_REVIEWS : "reviewed by (1:N)"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in (1:N)"
    SELLERS ||--o{ ORDER_ITEMS : "fulfilled by (1:N)"
    PRODUCTS }o--o| CATEGORY_TRANSLATION : "translates to (N:1)"
    CUSTOMERS }o--o| GEOLOCATION : "located at zip prefix (N:1)"
    SELLERS }o--o| GEOLOCATION : "located at zip prefix (N:1)"

    CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        int customer_zip_code_prefix FK
        string customer_city
        string customer_state
    }

    ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        datetime order_purchase_timestamp
        datetime order_approved_at
        datetime order_delivered_carrier_date
        datetime order_delivered_customer_date
        datetime order_estimated_delivery_date
    }

    ORDER_ITEMS {
        string order_id PK_FK
        int order_item_id PK
        string product_id FK
        string seller_id FK
        datetime shipping_limit_date
        float price
        float freight_value
    }

    ORDER_PAYMENTS {
        string order_id PK_FK
        int payment_sequential PK
        string payment_type
        int payment_installments
        float payment_value
    }

    ORDER_REVIEWS {
        string review_id PK
        string order_id FK
        int review_score
        string review_comment_title
        string review_comment_message
        datetime review_creation_date
        datetime review_answer_timestamp
    }

    PRODUCTS {
        string product_id PK
        string product_category_name FK
        int product_name_lenght
        int product_description_lenght
        int product_photos_qty
        float product_weight_g
        float product_length_cm
        float product_height_cm
        float product_width_cm
    }

    SELLERS {
        string seller_id PK
        int seller_zip_code_prefix FK
        string seller_city
        string seller_state
    }

    CATEGORY_TRANSLATION {
        string product_category_name PK
        string product_category_name_english
    }

    GEOLOCATION {
        int geolocation_zip_code_prefix PK
        float geolocation_lat
        float geolocation_lng
        string geolocation_city
        string geolocation_state
    }
```

### Validated Join Paths and Referential Integrity Audit

| Join Path | Key Condition | Cardinality | Integrity Status & Verification |
| :--- | :--- | :--- | :--- |
| `orders` $\rightarrow$ `customers` | `orders.customer_id = customers.customer_id` | **1 : 1** | **100% Matched** (0 unmatched orders). Note: To track true repeat behavior, group by `customers.customer_unique_id`. |
| `orders` $\rightarrow$ `order_items` | `orders.order_id = order_items.order_id` | **1 : N** | **98,666 matched orders**. Exactly **775 orders** in `orders` have 0 items (these represent canceled or unavailable orders before item allocation). |
| `order_items` $\rightarrow$ `products`| `order_items.product_id = products.product_id`| **N : 1** | **100% Matched** (32,951 distinct products in items are all present in products table). |
| `order_items` $\rightarrow$ `sellers` | `order_items.seller_id = sellers.seller_id` | **N : 1** | **100% Matched** (3,095 distinct sellers in items are all present in sellers table). |
| `orders` $\rightarrow$ `order_payments`| `orders.order_id = order_payments.order_id` | **1 : N** | **99,440 matched orders**. Exactly **1 order** (`bfbd0f9bdef84302105ad712db648a6c`) has no payment record. |
| `orders` $\rightarrow$ `order_reviews` | `orders.order_id = order_reviews.order_id` | **1 : N** | **98,673 matched orders**. 768 orders have no review. 547 orders have multiple reviews. |
| `products` $\rightarrow$ `translation` | `products.product_category_name = translation.product_category_name` | **N : 1** | **Missing 2 categories** in translation table: `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`. |
| `customers` $\rightarrow$ `geolocation` | `customers.customer_zip_code_prefix = geo.geolocation_zip_code_prefix` | **N : 1** (Aggregated) | **157 customer zip prefixes** do not exist in the geolocation dataset. Geolocation must be deduplicated and averaged per prefix before joining. |
| `sellers` $\rightarrow$ `geolocation` | `sellers.seller_zip_code_prefix = geo.geolocation_zip_code_prefix` | **N : 1** (Aggregated) | **7 seller zip prefixes** do not exist in the geolocation dataset. |

---

## Section 3: Data Quality, Anomaly & Integrity Report

### 1. The Geolocation Multi-Record Explosion Risk
- **Issue:** `olist_geolocation_dataset.csv` contains 1,000,163 rows with 261,831 exact duplicate rows and multiple lat/lng measurements for the exact same `geolocation_zip_code_prefix` (19,015 distinct prefixes).
- **Impact:** A direct relational join between `customers`/`sellers` and raw `geolocation` on `zip_code_prefix` will cause a severe Cartesian product explosion, multiplying order counts and GMV metrics by hundreds of times.
- **Solution:** Clean coordinates to Brazil bounds (Lat: $[-33.75, +5.27]$, Lng: $[-73.98, -34.79]$) and create an aggregated dimension `dim_geolocation` grouped by `zip_code_prefix` with `AVG(lat)`, `AVG(lng)`, and modal city/state.

### 2. Category Translation Gaps
- **Issue:** Two valid product categories in `olist_products_dataset.csv` are omitted in `product_category_name_translation.csv`:
  1. `pc_gamer` $\rightarrow$ English: `pc_gamer` (Gaming PC)
  2. `portateis_cozinha_e_preparadores_de_alimentos` $\rightarrow$ English: `portable_kitchen_food_preparers` (Small Kitchen Appliances)
- **Solution:** Explicitly append these 2 translations in ETL transformation layer to prevent `NULL` English category values.

### 3. Payment Total vs. Items + Freight Discrepancy
- **Validation:** Grouped sum of `order_items (price + freight_value)` was compared against grouped sum of `order_payments (payment_value)`.
- **Finding:**
  - 98,285 orders (99.61%) match within R$ 0.01.
  - 380 orders have discrepancy $\ge$ R$ 0.01.
  - 249 orders have discrepancy $>$ R$ 1.00 (Max difference: R$ 182.81).
- **Cause:** Voucher discounts applied post-itemization, rounding issues, or multi-seller voucher adjustments.
- **Solution:** Maintain distinct metrics: `Gross Merchandise Value (Sum of Items Price)`, `Total Freight Value`, and `Net Captured Payment Value`.

### 4. Duplicate Review IDs & Multi-Order Reviews
- **Issue:** 814 `review_id` values appear 2 or 3 times in `olist_order_reviews_dataset.csv`. Additionally, 547 orders have multiple review entries submitted at different dates.
- **Solution:** Use composite key (`review_id`, `order_id`) or select the latest review per order (`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) = 1`).

### 5. Extreme Physical & Price Outliers
- `product_weight_g = 0`: 4 products have weight recorded as 0 grams.
- `payment_installments = 0`: 2 payment records have 0 installments with a positive payment value.
- Maximum shipping limit date is recorded as `2020-04-09` despite all purchase timestamps ending in `2018-10`.

---

## Section 4: Enterprise Decision Intelligence Evaluation

---

### A. Business KPIs Realistically Computable

| Domain | Key Performance Indicator (KPI) | Formula / Source Columns |
| :--- | :--- | :--- |
| **Financial / Revenue** | **Gross Merchandise Value (GMV)** | $\sum \text{order\_items.price}$ |
| | **Average Order Value (AOV)** | $\frac{\text{GMV}}{\text{Count of Unique Orders}}$ |
| | **Freight-to-GMV Ratio (%)** | $\frac{\sum \text{freight\_value}}{\text{GMV}} \times 100$ |
| | **Payment Split by Tender Type** | $\sum \text{payment\_value}$ grouped by `payment_type` |
| **Fulfillment & Logistics** | **Carrier Transit Time (Days)** | $\text{order\_delivered\_customer\_date} - \text{order\_delivered\_carrier\_date}$ |
| | **Seller Dispatch Lead Time (Days)**| $\text{order\_delivered\_carrier\_date} - \text{order\_approved\_at}$ |
| | **On-Time Delivery Rate (%)** | $\frac{\text{Orders delivered} \le \text{order\_estimated\_delivery\_date}}{\text{Total Delivered Orders}} \times 100$ |
| | **Average Delivery Delay (Days)** | $\text{order\_delivered\_customer\_date} - \text{order\_estimated\_delivery\_date}$ (for late orders) |
| | **Seller SLA Breach Rate (%)** | $\frac{\text{Orders with carrier\_date} > \text{shipping\_limit\_date}}{\text{Total Dispatched Orders}} \times 100$ |
| **Customer Experience** | **Customer Satisfaction Score (CSAT)**| $\text{Average}(\text{review\_score}) \text{ on a 1.0 to 5.0 scale}$ |
| | **Net Promoter Score Proxy (NPS)** | $\frac{\text{Count}(5\star) - \text{Count}(1\star + 2\star)}{\text{Total Reviews}} \times 100$ |
| | **Review Response Lead Time (Hours)**| $\text{review\_answer\_timestamp} - \text{review\_creation\_date}$ |
| **Customer Retention** | **Repeat Customer Rate (%)** | $\frac{\text{Customers with } > 1 \text{ orders}}{\text{Total Unique Customers}} \times 100$ (approx. 3.12%) |
| | **Customer Lifetime Value (LTV Proxy)**| $\sum \text{GMV per } \text{customer\_unique\_id}$ |

---

### B. Analytical Dimensions

1. **Temporal Dimensions:** Purchase Year, Quarter, Month, Week of Year, Day of Week, Hour of Day, Holiday Indicator (e.g. Black Friday 2017 spikes).
2. **Geographical Dimensions:** Customer State, Customer Metro/Interior, Seller State, Interstate vs. Intrastate Route, Haversine Distance (km between Seller and Customer Zip).
3. **Product Taxonomy:** Category (English), Product Dimension Volumetric Class (Small, Medium, Heavy/Bulk).
4. **Seller Tiers:** Fast Dispatchers ($< 24\text{h}$), High GMV Power Sellers, Chronic Delay Sellers.
5. **Customer Cohorts:** Acquisition Month Cohort (e.g., 2017-01 Cohort), Order Frequency Bucket, Value Tier (Bronze/Silver/Gold).
6. **Order Lifecycle & Status:** Delivered, Canceled, Unavailable, Invoiced, Shipped.

---

### C. Machine Learning Prediction Targets

1. **Estimated Delivery Date Delay Prediction (Regression & Binary Classification):**
   - *Target:* `is_delivery_late` (Binary: $1$ if `delivered_customer_date > estimated_delivery_date`, $0$ otherwise) or `actual_transit_days` (Continuous).
   - *Features:* Distance between seller & customer, product weight/dimensions, seller historical dispatch latency, origin/destination state pairs, seasonal week.
2. **Review Score / Low Satisfaction Risk Prediction (Multi-class / Binary):**
   - *Target:* `review_score` or `is_negative_review` ($1\text{ or }2\star$).
   - *Features:* Delivery delay vs estimate, freight cost ratio, payment installments, category, seller historical rating.
3. **Order Cancellation Propensity:**
   - *Target:* `order_status == 'canceled'`.
   - *Features:* Payment approval delay, item availability, payment method (e.g., unpaid boleto expiration).
4. **Customer Churn / Repeat Purchase Propensity:**
   - *Target:* Will `customer_unique_id` make a 2nd purchase within 90/180 days.

---

### D. Clustering & Segmentation Opportunities

1. **Customer RFM Segmentation:**
   - **R (Recency):** Days since last purchase timestamp.
   - **F (Frequency):** Total lifetime orders.
   - **M (Monetary):** Total lifetime spend.
   - *Clusters:* Champions, High-Value One-Timers, At-Risk Customers, Lost Customers.
2. **Seller Performance & Reliability Clustering:**
   - Dimensions: Avg fulfillment speed, SLA compliance rate, avg review score, cancellation rate, product catalog diversity.
3. **Logistics Corridor / Regional Route Clustering:**
   - Clusters high-friction freight routes with abnormal freight cost and high transit variance (e.g. Southeast to North/Northeast routes).

---

### E. Anomaly Detection Opportunities

1. **Logistics Bottleneck & Carrier Delay Anomalies:** Real-time z-score / isolation forest detection on carrier transit time per origin-destination pair.
2. **Seller SLA Breaches & Ghost Stocking:** Sellers accepting orders but failing to hand over to carrier before `shipping_limit_date`.
3. **Pricing & Freight Value Spikes:** Products with freight cost significantly exceeding item price ($> 200\%$).
4. **Review Sentiment & Score Mismatch:** High rating with negative text or 1-star rating with positive text.

---

### F. Time-Series Forecasting Opportunities

1. **Platform GMV & Order Volume Demand Forecasting:** Daily and weekly Prophet / ARIMA / LightGBM forecasts with holiday seasonality.
2. **Category-Level Sales Velocity Forecasting:** Inventory replenishment projections per category.
3. **Regional Freight Volume Forecasting:** Inflow and outflow freight load prediction per state for logistics capacity planning.

---

### G. AI-Agent & Natural Language $\rightarrow$ SQL (NL2SQL) Capabilities

1. **Executive Decision Intelligence Copilot:**
   - Answers business questions: *"What was our GMV in SP vs RJ last quarter?"*, *"Which seller category had the worst on-time delivery rate in Q2 2018?"*
2. **Logistics Escalation & Root-Cause Agent:**
   - Autonomous query agent that diagnoses late orders: *"Why did orders to Bahia experience a 40% satisfaction drop in March 2018?"*
3. **Merchant Health & Compliance Auditor Agent:**
   - Scans seller metrics and generates automated performance warnings or merchant scorecards.

---

## Section 5: Recommended Analytical Data Architecture

To support fast sub-second OLAP queries, BI dashboards, and AI agents, the data should be transformed from 3NF raw tables into a **Dimensional Star Schema** and an **Aggregated One Big Table (OBT)**.

```
                  +--------------------------+
                  |      dim_customers       |
                  | (customer_unique_id,     |
                  |  city, state, lat, lng)  |
                  +-------------+------------+
                                |
+----------------------+        |        +----------------------+
|     dim_products     |        |        |     dim_sellers      |
| (product_id, en_cat, |        |        | (seller_id, city,    |
|  weight, dimensions) |        |        |  state, lat, lng)    |
+----------+-----------+        |        +-----------+----------+
           |                    |                    |
           |          +---------+----------+         |
           +--------->|  fct_order_items   |<--------+
                      | (Order Line Grain: |
           +--------->|  item_price,       |<--------+
           |          |  freight_value,    |         |
           |          |  carrier_delay)    |         |
+----------+-----------+--+-----+-----+----+-----+---+----------+
|       dim_dates         |     |     |     dim_payment_summary  |
| (date_key, year, month, |     |     | (order_id, payment_types,|
|  quarter, day_of_week)  |     |     |  total_installments)     |
+-------------------------+     |     +--------------------------+
                                |
                      +---------+----------+
                      |     dim_reviews    |
                      | (order_id, score,  |
                      |  sentiment, length)|
                      +--------------------+
```

### Proposed Data Model Components

1. **`fct_order_items` (Fact Grain: 1 row per order_item):**
   - Keys: `order_id`, `order_item_id`, `customer_key`, `product_key`, `seller_key`, `order_date_key`.
   - Measures: `price`, `freight_value`, `total_item_value`, `dispatch_duration_hours`, `carrier_duration_hours`, `delivery_delay_days`, `is_late`.
2. **`dim_customers`:** Consolidated unique customer profile with lifetime stats and verified geo coordinates.
3. **`dim_products`:** English translated category, size tier, weight bucket.
4. **`dim_sellers`:** Merchant location, tier, historical performance badges.
5. **`dim_dates`:** Comprehensive fiscal calendar with Brazilian national holidays.
6. **`analytics_obt_orders` (One Big Table for Agent / Fast SQL):**
   - Denormalized wide table (1 row per order or order item) pre-joined with all customer, seller, product, payment, review, and logistics metrics.

---

## Section 6: Recommended Feature Engineering Pipeline

1. **Geospatial Features:**
   - `haversine_distance_km`: Calculated great-circle distance between customer and seller lat/lng.
   - `is_interstate_order`: Boolean flag ($1$ if `customer_state != seller_state`).
2. **Logistics & SLA Features:**
   - `estimated_delivery_duration_days`: `order_estimated_delivery_date - order_purchase_timestamp`.
   - `seller_dispatch_delta_hours`: Time difference between `order_approved_at` and `order_delivered_carrier_date`.
   - `shipping_limit_buffer_days`: Time difference between `shipping_limit_date` and carrier pickup.
3. **Product Physical Density:**
   - `product_volume_cm3`: $\text{length} \times \text{height} \times \text{width}$.
   - `product_density_g_per_cm3`: $\frac{\text{weight\_g}}{\text{volume\_cm3}}$.
4. **Customer Behavioral History (Point-in-Time Leakage Safe):**
   - `customer_prior_order_count`, `customer_lifetime_spend_prior`.
5. **NLP Text Sentiment Features:**
   - `review_char_length`, `review_word_count`, `has_comment_title_flag`, `sentiment_polarity` (Portuguese sentiment score).

---

## Section 7: Recommended Dashboard & Decision Intelligence Modules

1. **Executive Overview & Financial Intelligence:**
   - GMV, Net Revenue, AOV, Order Volume, Payment Breakdown, Top Product Categories.
2. **Logistics & Supply Chain Command Center:**
   - SLA Compliance Map, Delay Bottleneck Analyzer, Route Distance vs. Freight Cost Scatter, On-Time Delivery Gauge.
3. **Customer Experience & Voice-of-Customer (VoC):**
   - CSAT / NPS Distribution, Review Score vs. Delivery Latency Correlation, Low-Rating Root Cause Decomposition.
4. **Seller Performance & Marketplace Health:**
   - Seller Scorecards, Dispatch Speed Matrix, Top Merchants vs. At-Risk Merchants.
5. **AI Decision Studio & Scenario Simulation:**
   - Dynamic Freight Cost Simulator, Delay Risk Estimator for In-Flight Orders, Natural Language SQL Query Bar.

---

## Section 8: Dataset Risks, Biases & Technical Limitations

1. **Low Repeat Purchase Signal:**
   - Only 3.12% of consumers in this dataset placed more than one order. Standard retention and LTV models will face severe class imbalance. Models must be framed around customer journey and basket value rather than long-term subscription churn.
2. **Missing In-Flight Orders:**
   - The dataset represents a historical snapshot (2016–2018). Live API tracking must be simulated for real-time decision intelligence workflows.
3. **Text Missingness:**
   - 88.34% of review titles and 58.70% of review comments are null (customers left numeric star ratings without comments).
4. **Postal Prefix Aggregation:**
   - Only 5-digit zip code prefixes are provided (not complete 8-digit Brazilian CEPs), meaning coordinates represent municipal centroid approximations rather than doorstep precision.

---

## Summary & Next Steps

This concludes the complete profiling, referential integrity verification, and data modeling design for the Olist E-Commerce dataset.

All 9 CSV datasets in `archive/` have been audited without data corruption or premature schema mutation. The project is fully positioned to proceed with clean data pipeline engineering, dimensional modeling, and decision intelligence system development.
