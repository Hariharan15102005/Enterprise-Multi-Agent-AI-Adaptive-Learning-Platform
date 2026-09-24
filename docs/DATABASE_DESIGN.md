# OlistIQ — Analytical Database Design Specification

**Project:** OlistIQ AI-Powered E-Commerce Decision Intelligence Platform  
**Target Database Engine:** PostgreSQL 15+ / TimescaleDB Compatible  
**Modeling Paradigm:** Dimensional Star Schema + Aggregated Analytical Marts + One Big Table (OBT)  
**Status:** Architecture Design Approved  

---

## 1. Dimensional Modeling Strategy & Design Rationale

The raw Olist dataset contains 9 normalized tables with operational complexities (e.g. order-level customer tokens, duplicate review records, coordinates multi-mapping per zip code, and missing category translations). 

To ensure sub-second analytical aggregations, clean referential joins, and reliable LLM-driven NL2SQL query execution, the database is architected around a **Star Schema** with high-performance indexes, constraints, and an aggregated **One Big Table (OBT)** view/materialized table for accelerated AI queries.

```
                           +---------------------------+
                           |       dim_customer        |
                           | (customer_unique_id PK)   |
                           +-------------+-------------+
                                         |
+----------------------------+           |           +----------------------------+
|        dim_product         |           |           |         dim_seller         |
| (product_id PK, EN category|           |           | (seller_id PK, city,       |
|  dimensions, weight)       |           |           |  state, lat, lng)          |
+-------------+--------------+           |           +-------------+--------------+
              |                          |                         |
              |            +-------------+-------------+           |
              +----------->|     fact_order_items      |<----------+
                           | (Grain: 1 row/order item) |
              +----------->| Price, Freight, Margins,  |<----------+
              |            | Fulfillment Lead Times    |           |
+-------------+--------------+-----+-------------+-----+-----------+--------------+
|          dim_date          |     |             |     |    dim_payment_summary   |
| (date_key PK, YYYY-MM-DD,  |     |             |     | (order_id PK, total_val, |
|  Quarter, Holiday flags)   |     |             |     |  credit_card_val, etc.)  |
+----------------------------+     |             |     +--------------------------+
                                   |             |
                                   |   +---------+----------+
                                   |   |    fact_reviews    |
                                   |   | (Grain: 1 review)  |
                                   |   +--------------------+
                                   |
                      +------------+------------+
                      |       fact_orders       |
                      | (Grain: 1 order summary)|
                      +-------------------------+
```

---

## 2. Customer Identity Architecture: `customer_id` vs `customer_unique_id`

### The Critical Distinction (Validated by Profiling)
- `customer_id` (99,441 unique values): A transient token generated per purchase transaction. It maps 1:1 with an order record in `orders`.
- `customer_unique_id` (96,096 unique values): The real physical consumer identity across multiple purchases. Exactly 2,997 consumers placed repeat orders (up to 17 orders by a single user).

### Database Implementation Strategy
1. `dim_customer` uses `customer_unique_id` as the primary key.
2. An internal bridge table `bridge_customer_orders` (or dimension attribute) maps all transient `customer_id` tokens to their respective `customer_unique_id`.
3. All customer intelligence queries (RFM segmentation, retention rate, customer lifetime value (LTV), cohort analysis, and churn risk) **must group by `customer_unique_id`**.
4. Order transaction lookups map `orders.customer_id` $\rightarrow$ `dim_customer.customer_unique_id`.

---

## 3. Geolocation Aggregation Architecture: Mitigating Cartesian Explosion

### The Issue
`olist_geolocation_dataset.csv` contains 1,000,163 rows with 261,831 exact duplicate entries and thousands of coordinate points per 5-digit zip code. Direct relational joins create a catastrophic Cartesian product.

### The Solution: `dim_geolocation`
During ETL, raw coordinate points are filtered to valid Brazilian geospatial boundaries (Latitude: $[-33.75, +5.27]$, Longitude: $[-73.98, -34.79]$). Coordinates are grouped by `zip_code_prefix` to produce a clean, 1-row-per-prefix dimension with arithmetic mean coordinates and statistical mode for city/state.

---

## 4. Category Translation & Normalization Strategy

`product_category_name_translation.csv` contains 71 Portuguese-to-English mappings. Profiling revealed that 2 active product categories in `olist_products_dataset.csv` are absent:
1. `pc_gamer` $\rightarrow$ Mapped to `pc_gamer` (English label: "Gaming PC")
2. `portateis_cozinha_e_preparadores_de_alimentos` $\rightarrow$ Mapped to `portable_kitchen_food_preparers` (English label: "Small Kitchen & Food Prep Appliances")

Additionally, 610 products with `NULL` category are mapped to `unknown_category` ("Uncategorized").

---

## 5. Detailed Table Specifications & Schemas

---

### Dimension Tables

#### 1. `dim_customer`
- **Purpose:** Represents unique individual customers across their entire shopping history.
- **Grain:** One row per unique consumer (`customer_unique_id`).

```sql
CREATE TABLE dim_customer (
    customer_unique_id VARCHAR(32) PRIMARY KEY,
    first_zip_code_prefix INTEGER NOT NULL,
    current_city VARCHAR(100) NOT NULL,
    current_state VARCHAR(2) NOT NULL,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    first_order_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    latest_order_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    lifetime_order_count INTEGER NOT NULL DEFAULT 1,
    lifetime_spend_brl NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    is_repeat_customer BOOLEAN NOT NULL DEFAULT FALSE,
    rfm_recency_days INTEGER,
    rfm_frequency_score INTEGER,
    rfm_monetary_score INTEGER,
    rfm_segment VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_cust_state ON dim_customer(current_state);
CREATE INDEX idx_dim_cust_segment ON dim_customer(rfm_segment);
CREATE INDEX idx_dim_cust_zip ON dim_customer(first_zip_code_prefix);
```

---

#### 2. `dim_product`
- **Purpose:** Consolidated product catalog with standardized English categories and physical volumetric metrics.
- **Grain:** One row per product SKU (`product_id`).

```sql
CREATE TABLE dim_product (
    product_id VARCHAR(32) PRIMARY KEY,
    category_name_pt VARCHAR(100) NOT NULL DEFAULT 'nao_informado',
    category_name_en VARCHAR(100) NOT NULL DEFAULT 'uncategorized',
    name_length_chars INTEGER,
    description_length_chars INTEGER,
    photos_qty INTEGER DEFAULT 0,
    weight_g NUMERIC(10, 2) DEFAULT 0.00,
    length_cm NUMERIC(10, 2) DEFAULT 0.00,
    height_cm NUMERIC(10, 2) DEFAULT 0.00,
    width_cm NUMERIC(10, 2) DEFAULT 0.00,
    volume_cm3 NUMERIC(12, 2) GENERATED ALWAYS AS (length_cm * height_cm * width_cm) STORED,
    density_g_cm3 NUMERIC(10, 4),
    size_tier VARCHAR(20) NOT NULL DEFAULT 'Standard', -- 'Small', 'Standard', 'Bulky', 'Heavy'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_prod_cat_en ON dim_product(category_name_en);
CREATE INDEX idx_dim_prod_size ON dim_product(size_tier);
```

---

#### 3. `dim_seller`
- **Purpose:** Seller profile, operational location, and lifetime fulfillment quality scores.
- **Grain:** One row per marketplace merchant (`seller_id`).

```sql
CREATE TABLE dim_seller (
    seller_id VARCHAR(32) PRIMARY KEY,
    seller_zip_code_prefix INTEGER NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state VARCHAR(2) NOT NULL,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    first_active_date TIMESTAMP WITH TIME ZONE,
    total_orders_fulfilled INTEGER DEFAULT 0,
    total_sales_value_brl NUMERIC(12, 2) DEFAULT 0.00,
    avg_dispatch_time_hours NUMERIC(8, 2),
    sla_breach_rate_pct NUMERIC(5, 2),
    avg_review_score NUMERIC(3, 2),
    seller_tier VARCHAR(30) DEFAULT 'Standard', -- 'Power Seller', 'Standard', 'At Risk'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_seller_state ON dim_seller(seller_state);
CREATE INDEX idx_dim_seller_tier ON dim_seller(seller_tier);
```

---

#### 4. `dim_geolocation`
- **Purpose:** Deduplicated, boundary-validated geospatial coordinates per postal prefix.
- **Grain:** One row per postal code prefix (`zip_code_prefix`).

```sql
CREATE TABLE dim_geolocation (
    zip_code_prefix INTEGER PRIMARY KEY,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    city_canonical VARCHAR(100) NOT NULL,
    state_code VARCHAR(2) NOT NULL,
    brazil_macro_region VARCHAR(20) NOT NULL, -- 'Southeast', 'South', 'Northeast', 'Central-West', 'North'
    sample_points_count INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_dim_geo_state ON dim_geolocation(state_code);
CREATE INDEX idx_dim_geo_region ON dim_geolocation(brazil_macro_region);
```

---

#### 5. `dim_date`
- **Purpose:** Calendar dimension for temporal slicing, seasonality, and Brazilian national holidays.
- **Grain:** One row per calendar day.

```sql
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY, -- Format: YYYYMMDD (e.g. 20171124)
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday_br BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_name VARCHAR(100)
);

CREATE INDEX idx_dim_date_year_month ON dim_date(year, month);
```

---

### Fact Tables

#### 1. `fact_order_items` (Core Transaction Fact)
- **Purpose:** Primary line-item sales, freight, seller attribution, and item-level delivery SLA.
- **Grain:** One row per order line item (`order_id` + `order_item_id`).

```sql
CREATE TABLE fact_order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INTEGER NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL REFERENCES dim_customer(customer_unique_id),
    product_id VARCHAR(32) NOT NULL REFERENCES dim_product(product_id),
    seller_id VARCHAR(32) NOT NULL REFERENCES dim_seller(seller_id),
    order_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    
    -- Timestamps
    purchase_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    approved_timestamp TIMESTAMP WITH TIME ZONE,
    shipping_limit_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    delivered_carrier_timestamp TIMESTAMP WITH TIME ZONE,
    delivered_customer_timestamp TIMESTAMP WITH TIME ZONE,
    estimated_delivery_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Financial Measures
    item_price_brl NUMERIC(10, 2) NOT NULL,
    freight_value_brl NUMERIC(10, 2) NOT NULL,
    total_item_cost_brl NUMERIC(10, 2) GENERATED ALWAYS AS (item_price_brl + freight_value_brl) STORED,
    freight_ratio_pct NUMERIC(6, 2) GENERATED ALWAYS AS (
        CASE WHEN item_price_brl > 0 THEN (freight_value_brl / item_price_brl) * 100 ELSE 0 END
    ) STORED,
    
    -- Fulfillment & Logistics Measures
    dispatch_lead_time_hours NUMERIC(10, 2),
    carrier_transit_days NUMERIC(10, 2),
    total_delivery_days NUMERIC(10, 2),
    estimated_delivery_days NUMERIC(10, 2),
    delivery_delta_days NUMERIC(10, 2), -- (delivered_customer - estimated_delivery)
    is_delayed BOOLEAN NOT NULL DEFAULT FALSE,
    is_seller_sla_breach BOOLEAN NOT NULL DEFAULT FALSE,
    haversine_distance_km NUMERIC(10, 2),
    is_interstate_shipment BOOLEAN NOT NULL DEFAULT FALSE,
    
    order_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (order_id, order_item_id)
);

CREATE INDEX idx_fct_items_order ON fact_order_items(order_id);
CREATE INDEX idx_fct_items_cust ON fact_order_items(customer_unique_id);
CREATE INDEX idx_fct_items_prod ON fact_order_items(product_id);
CREATE INDEX idx_fct_items_seller ON fact_order_items(seller_id);
CREATE INDEX idx_fct_items_date ON fact_order_items(order_date_key);
CREATE INDEX idx_fct_items_delayed ON fact_order_items(is_delayed);
```

---

#### 2. `fact_orders` (Order Lifecycle Summary Fact)
- **Purpose:** Tracks overall order header status, full basket value, review integration, and fulfillment SLA.
- **Grain:** One row per customer order (`order_id`).

```sql
CREATE TABLE fact_orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32) NOT NULL REFERENCES dim_customer(customer_unique_id),
    order_status VARCHAR(20) NOT NULL,
    order_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    purchase_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    approved_timestamp TIMESTAMP WITH TIME ZONE,
    delivered_carrier_timestamp TIMESTAMP WITH TIME ZONE,
    delivered_customer_timestamp TIMESTAMP WITH TIME ZONE,
    estimated_delivery_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Basket Aggregations
    total_item_count INTEGER NOT NULL DEFAULT 1,
    unique_product_count INTEGER NOT NULL DEFAULT 1,
    unique_seller_count INTEGER NOT NULL DEFAULT 1,
    total_items_price_brl NUMERIC(12, 2) NOT NULL,
    total_freight_value_brl NUMERIC(12, 2) NOT NULL,
    gross_order_value_brl NUMERIC(12, 2) NOT NULL,
    total_payment_value_brl NUMERIC(12, 2) NOT NULL,
    payment_value_discrepancy_brl NUMERIC(8, 2) DEFAULT 0.00,
    
    -- Payment Details
    primary_payment_type VARCHAR(20),
    max_payment_installments INTEGER DEFAULT 1,
    payment_sequential_count INTEGER DEFAULT 1,
    
    -- Delivery Performance
    total_delivery_duration_days NUMERIC(8, 2),
    delivery_delay_vs_estimated_days NUMERIC(8, 2),
    is_delivered_late BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Review Integration
    review_score INTEGER,
    has_review BOOLEAN NOT NULL DEFAULT FALSE,
    review_creation_timestamp TIMESTAMP WITH TIME ZONE,
    review_answer_timestamp TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_fct_orders_cust ON fact_orders(customer_unique_id);
CREATE INDEX idx_fct_orders_status ON fact_orders(order_status);
CREATE INDEX idx_fct_orders_date ON fact_orders(order_date_key);
CREATE INDEX idx_fct_orders_late ON fact_orders(is_delivered_late);
```

---

#### 3. `fact_payments`
- **Purpose:** Granular breakdown of individual payment installments, payment vouchers, and tenders.
- **Grain:** One row per payment transaction (`order_id` + `payment_sequential`).

```sql
CREATE TABLE fact_payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INTEGER NOT NULL,
    payment_type VARCHAR(20) NOT NULL, -- 'credit_card', 'boleto', 'voucher', 'debit_card'
    payment_installments INTEGER NOT NULL DEFAULT 1,
    payment_value_brl NUMERIC(10, 2) NOT NULL,
    order_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE INDEX idx_fct_pay_order ON fact_payments(order_id);
CREATE INDEX idx_fct_pay_type ON fact_payments(payment_type);
```

---

#### 4. `fact_reviews`
- **Purpose:** Customer satisfaction ratings, comment sentiment, and response latency.
- **Grain:** One row per submitted review (`review_id` + `order_id`).

```sql
CREATE TABLE fact_reviews (
    review_id VARCHAR(32) NOT NULL,
    order_id VARCHAR(32) NOT NULL,
    review_score INTEGER NOT NULL CHECK (review_score BETWEEN 1 AND 5),
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    has_comment_text BOOLEAN NOT NULL DEFAULT FALSE,
    comment_length_chars INTEGER DEFAULT 0,
    sentiment_label VARCHAR(20), -- 'Positive', 'Neutral', 'Negative'
    sentiment_score NUMERIC(5, 4),
    review_creation_date DATE NOT NULL,
    review_answer_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    response_delay_hours NUMERIC(8, 2),
    PRIMARY KEY (review_id, order_id)
);

CREATE INDEX idx_fct_rev_order ON fact_reviews(order_id);
CREATE INDEX idx_fct_rev_score ON fact_reviews(review_score);
CREATE INDEX idx_fct_rev_sentiment ON fact_reviews(sentiment_label);
```

---

## 6. Aggregated Materialized Views & One Big Table (OBT)

To enable zero-latency dashboards and prevent LLM SQL generation from performing expensive 7-table joins, the database exposes a pre-joined **One Big Table** view/table:

```sql
CREATE MATERIALIZED VIEW analytics_obt_orders AS
SELECT 
    fo.order_id,
    fo.customer_unique_id,
    dc.current_city AS customer_city,
    dc.current_state AS customer_state,
    dc.rfm_segment AS customer_rfm_segment,
    fo.order_status,
    fo.purchase_timestamp,
    dd.year AS purchase_year,
    dd.month AS purchase_month,
    dd.month_name AS purchase_month_name,
    dd.quarter AS purchase_quarter,
    dd.day_name AS purchase_day_name,
    dd.is_holiday_br,
    fo.gross_order_value_brl,
    fo.total_items_price_brl,
    fo.total_freight_value_brl,
    fo.total_item_count,
    fo.primary_payment_type,
    fo.max_payment_installments,
    fo.total_delivery_duration_days,
    fo.delivery_delay_vs_estimated_days,
    fo.is_delivered_late,
    fo.review_score,
    fo.has_review
FROM fact_orders fo
JOIN dim_customer dc ON fo.customer_unique_id = dc.customer_unique_id
JOIN dim_date dd ON fo.order_date_key = dd.date_key;

CREATE INDEX idx_obt_purchase_date ON analytics_obt_orders(purchase_timestamp);
CREATE INDEX idx_obt_state ON analytics_obt_orders(customer_state);
CREATE INDEX idx_obt_score ON analytics_obt_orders(review_score);
```

---

## 7. Data Integrity & Constraint Summary

1. **Foreign Key Integrity:** 100% of order items reference valid `product_id`, `seller_id`, and `customer_unique_id`.
2. **Missing Value Isolation:** Nullable operational timestamps (`order_delivered_customer_date`) are safely decoupled from core financial facts.
3. **Auditability:** Every fact and dimension table maintains metadata tracking row insertion and transformation batches.
