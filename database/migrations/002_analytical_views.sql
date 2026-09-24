-- ==============================================================================
-- OlistIQ Analytical Database — Migration 002: Analytical Views & One Big Table
-- ==============================================================================

-- 1. One Big Table (OBT) Analytical View for Sub-Second Aggregations & AI Queries
CREATE VIEW IF NOT EXISTS analytics_obt_orders AS
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
LEFT JOIN dim_customer dc ON fo.customer_unique_id = dc.customer_unique_id
LEFT JOIN dim_date dd ON fo.order_date_key = dd.date_key;

-- 2. Daily Sales & Operations Aggregation View
CREATE VIEW IF NOT EXISTS agg_daily_sales_ops AS
SELECT 
    dd.full_date AS order_date,
    dd.year,
    dd.month,
    dd.quarter,
    dd.is_weekend,
    dd.is_holiday_br,
    COUNT(fo.order_id) AS total_orders,
    COUNT(DISTINCT fo.customer_unique_id) AS unique_customers,
    SUM(fo.total_items_price_brl) AS gmv_brl,
    SUM(fo.total_freight_value_brl) AS total_freight_brl,
    SUM(fo.total_payment_value_brl) AS net_revenue_brl,
    AVG(fo.gross_order_value_brl) AS aov_brl,
    AVG(fo.total_delivery_duration_days) AS avg_delivery_days,
    SUM(CASE WHEN fo.is_delivered_late THEN 1 ELSE 0 END) AS late_orders_count,
    AVG(fo.review_score) AS avg_daily_review_score
FROM fact_orders fo
JOIN dim_date dd ON fo.order_date_key = dd.date_key
GROUP BY dd.full_date, dd.year, dd.month, dd.quarter, dd.is_weekend, dd.is_holiday_br;

-- 3. Monthly Category Performance View
CREATE VIEW IF NOT EXISTS agg_monthly_category_perf AS
SELECT 
    dd.year,
    dd.month,
    dp.category_name_en,
    COUNT(foi.order_id) AS total_items_sold,
    COUNT(DISTINCT foi.order_id) AS total_orders,
    SUM(foi.item_price_brl) AS total_sales_brl,
    SUM(foi.freight_value_brl) AS total_freight_brl,
    AVG(foi.item_price_brl) AS avg_item_price_brl,
    AVG(foi.carrier_transit_days) AS avg_transit_days,
    SUM(CASE WHEN foi.is_delayed THEN 1 ELSE 0 END) * 100.0 / COUNT(foi.order_id) AS late_rate_pct
FROM fact_order_items foi
JOIN dim_product dp ON foi.product_id = dp.product_id
JOIN dim_date dd ON foi.order_date_key = dd.date_key
GROUP BY dd.year, dd.month, dp.category_name_en;

-- 4. State Level Logistics Matrix View
CREATE VIEW IF NOT EXISTS agg_state_logistics_matrix AS
SELECT 
    dc.current_state AS customer_state,
    ds.seller_state AS seller_state,
    foi.is_interstate_shipment,
    COUNT(foi.order_id) AS shipment_count,
    AVG(foi.haversine_distance_km) AS avg_distance_km,
    AVG(foi.carrier_transit_days) AS avg_transit_days,
    AVG(foi.freight_value_brl) AS avg_freight_brl,
    SUM(CASE WHEN foi.is_delayed THEN 1 ELSE 0 END) * 100.0 / COUNT(foi.order_id) AS late_rate_pct
FROM fact_order_items foi
JOIN dim_customer dc ON foi.customer_unique_id = dc.customer_unique_id
JOIN dim_seller ds ON foi.seller_id = ds.seller_id
GROUP BY dc.current_state, ds.seller_state, foi.is_interstate_shipment;
