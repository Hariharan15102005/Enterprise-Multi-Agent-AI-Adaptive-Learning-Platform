-- ==============================================================================
-- OlistIQ Analytical Database — Migration 001: Initial Star Schema
-- PostgreSQL 15+ Compatible
-- ==============================================================================

-- 1. Dimension: Geolocation
CREATE TABLE IF NOT EXISTS dim_geolocation (
    zip_code_prefix INTEGER PRIMARY KEY,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    city_canonical VARCHAR(100) NOT NULL,
    state_code VARCHAR(2) NOT NULL,
    brazil_macro_region VARCHAR(20) NOT NULL,
    sample_points_count INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_dim_geo_state ON dim_geolocation(state_code);
CREATE INDEX IF NOT EXISTS idx_dim_geo_region ON dim_geolocation(brazil_macro_region);

-- 2. Dimension: Customer (Grain: Unique Individual Consumer)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_unique_id VARCHAR(32) PRIMARY KEY,
    first_zip_code_prefix INTEGER,
    current_city VARCHAR(100) NOT NULL,
    current_state VARCHAR(2) NOT NULL,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    first_order_timestamp TIMESTAMP WITH TIME ZONE,
    latest_order_timestamp TIMESTAMP WITH TIME ZONE,
    lifetime_order_count INTEGER NOT NULL DEFAULT 1,
    lifetime_spend_brl NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    is_repeat_customer BOOLEAN NOT NULL DEFAULT FALSE,
    rfm_recency_days INTEGER,
    rfm_frequency_score INTEGER,
    rfm_monetary_score INTEGER,
    rfm_segment VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_dim_cust_state ON dim_customer(current_state);
CREATE INDEX IF NOT EXISTS idx_dim_cust_segment ON dim_customer(rfm_segment);

-- 3. Dimension: Product
CREATE TABLE IF NOT EXISTS dim_product (
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
    volume_cm3 NUMERIC(12, 2),
    density_g_cm3 NUMERIC(10, 4),
    size_tier VARCHAR(20) NOT NULL DEFAULT 'Standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_dim_prod_cat_en ON dim_product(category_name_en);
CREATE INDEX IF NOT EXISTS idx_dim_prod_size ON dim_product(size_tier);

-- 4. Dimension: Seller
CREATE TABLE IF NOT EXISTS dim_seller (
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
    seller_tier VARCHAR(30) DEFAULT 'Standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_dim_seller_state ON dim_seller(seller_state);
CREATE INDEX IF NOT EXISTS idx_dim_seller_tier ON dim_seller(seller_tier);

-- 5. Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
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
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month ON dim_date(year, month);

-- 6. Fact: Orders (Header Summary Grain)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_date_key INTEGER NOT NULL,
    purchase_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    approved_timestamp TIMESTAMP WITH TIME ZONE,
    delivered_carrier_timestamp TIMESTAMP WITH TIME ZONE,
    delivered_customer_timestamp TIMESTAMP WITH TIME ZONE,
    estimated_delivery_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_item_count INTEGER NOT NULL DEFAULT 1,
    unique_product_count INTEGER NOT NULL DEFAULT 1,
    unique_seller_count INTEGER NOT NULL DEFAULT 1,
    total_items_price_brl NUMERIC(12, 2) NOT NULL,
    total_freight_value_brl NUMERIC(12, 2) NOT NULL,
    gross_order_value_brl NUMERIC(12, 2) NOT NULL,
    total_payment_value_brl NUMERIC(12, 2) NOT NULL,
    payment_value_discrepancy_brl NUMERIC(8, 2) DEFAULT 0.00,
    primary_payment_type VARCHAR(20),
    max_payment_installments INTEGER DEFAULT 1,
    payment_sequential_count INTEGER DEFAULT 1,
    total_delivery_duration_days NUMERIC(8, 2),
    delivery_delay_vs_estimated_days NUMERIC(8, 2),
    is_delivered_late BOOLEAN NOT NULL DEFAULT FALSE,
    review_score INTEGER,
    has_review BOOLEAN NOT NULL DEFAULT FALSE,
    review_creation_timestamp TIMESTAMP WITH TIME ZONE,
    review_answer_timestamp TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_fct_orders_cust ON fact_orders(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_fct_orders_status ON fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_fct_orders_date ON fact_orders(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fct_orders_late ON fact_orders(is_delivered_late);

-- 7. Fact: Order Items (Line Item Grain)
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INTEGER NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    order_date_key INTEGER NOT NULL,
    purchase_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    approved_timestamp TIMESTAMP WITH TIME ZONE,
    shipping_limit_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    delivered_carrier_timestamp TIMESTAMP WITH TIME ZONE,
    delivered_customer_timestamp TIMESTAMP WITH TIME ZONE,
    estimated_delivery_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    item_price_brl NUMERIC(10, 2) NOT NULL,
    freight_value_brl NUMERIC(10, 2) NOT NULL,
    total_item_cost_brl NUMERIC(10, 2) NOT NULL,
    freight_ratio_pct NUMERIC(6, 2) NOT NULL,
    dispatch_lead_time_hours NUMERIC(10, 2),
    carrier_transit_days NUMERIC(10, 2),
    total_delivery_days NUMERIC(10, 2),
    estimated_delivery_days NUMERIC(10, 2),
    delivery_delay_days NUMERIC(10, 2),
    is_delayed BOOLEAN NOT NULL DEFAULT FALSE,
    is_seller_sla_breach BOOLEAN NOT NULL DEFAULT FALSE,
    haversine_distance_km NUMERIC(10, 2),
    is_interstate_shipment BOOLEAN NOT NULL DEFAULT FALSE,
    order_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id, order_item_id)
);
CREATE INDEX IF NOT EXISTS idx_fct_items_order ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_fct_items_cust ON fact_order_items(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_fct_items_prod ON fact_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_fct_items_seller ON fact_order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_fct_items_date ON fact_order_items(order_date_key);

-- 8. Fact: Payments
CREATE TABLE IF NOT EXISTS fact_payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INTEGER NOT NULL,
    payment_type VARCHAR(20) NOT NULL,
    payment_installments INTEGER NOT NULL DEFAULT 1,
    payment_value_brl NUMERIC(10, 2) NOT NULL,
    order_date_key INTEGER NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);
CREATE INDEX IF NOT EXISTS idx_fct_pay_order ON fact_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_fct_pay_type ON fact_payments(payment_type);

-- 9. Fact: Reviews
CREATE TABLE IF NOT EXISTS fact_reviews (
    review_id VARCHAR(32) NOT NULL,
    order_id VARCHAR(32) NOT NULL,
    review_score INTEGER NOT NULL,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    has_comment_text BOOLEAN NOT NULL DEFAULT FALSE,
    comment_length_chars INTEGER DEFAULT 0,
    sentiment_label VARCHAR(20),
    sentiment_score NUMERIC(5, 4),
    review_creation_date DATE NOT NULL,
    review_answer_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    response_delay_hours NUMERIC(8, 2),
    PRIMARY KEY (review_id, order_id)
);
CREATE INDEX IF NOT EXISTS idx_fct_rev_order ON fact_reviews(order_id);
CREATE INDEX IF NOT EXISTS idx_fct_rev_score ON fact_reviews(review_score);
