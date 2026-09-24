# OlistIQ ML Feature Catalog

Comprehensive dictionary of input features, data types, sources, transformations, and leakage classifications.

---

## 1. Customer Segmentation Features

| Feature Name | Data Type | Source Entity | Transformation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `recency_days` | Integer | `dim_customer` | RobustScaler | Days elapsed between customer's latest order and dataset cutoff |
| `frequency_orders` | Integer | `dim_customer` | RobustScaler | Total count of distinct orders placed |
| `monetary_spend_brl` | Float | `dim_customer` | RobustScaler | Lifetime gross spend across all orders |
| `avg_order_value` | Float | Calculated | RobustScaler | Spend divided by order count |
| `avg_items_per_order` | Float | `fact_order_items` | RobustScaler | Total order items divided by distinct orders |
| `category_diversity` | Integer | `dim_product` | RobustScaler | Count of distinct product categories purchased |

---

## 2. Delivery Delay Risk Features

| Feature Name | Data Type | Source Entity | Availability Timing | Leakage Prevention Rule |
| :--- | :--- | :--- | :--- | :--- |
| `total_items_price_brl` | Float | `fact_orders` | Checkout | Validated pre-fulfillment |
| `total_freight_value_brl` | Float | `fact_orders` | Checkout | Validated pre-fulfillment |
| `freight_ratio_pct` | Float | Calculated | Checkout | Freight / Gross Value ratio |
| `total_item_count` | Integer | `fact_orders` | Checkout | Total items in basket |
| `unique_product_count` | Integer | `fact_orders` | Checkout | Count of unique SKUs |
| `haversine_distance_km` | Float | `fact_order_items` | Checkout | Geodesic distance between buyer and seller |
| `estimated_delivery_duration_days` | Float | `fact_orders` | Order Approval | Estimated delivery date minus purchase date |
| `max_product_weight_g` | Float | `dim_product` | Catalog | Heaviest item in order |
| `total_product_volume_cm3` | Float | `dim_product` | Catalog | Total cubic volume |
| `seller_historical_delay_rate` | Float | `dim_seller` | Historical Agg | Seller SLA breach percentage before order |
| `purchase_month` | Integer | `dim_date` | Order Approval | 1 to 12 |
| `purchase_dayofweek` | Integer | `dim_date` | Order Approval | 0 (Monday) to 6 (Sunday) |
| `purchase_hour` | Integer | `fact_orders` | Order Approval | 0 to 23 |
| `customer_state` | Categorical | `dim_customer` | Checkout | State code (SP, RJ, etc.) |
| `seller_state` | Categorical | `dim_seller` | Order Approval | Origin seller state |
| `is_interstate_shipment` | Binary | `fact_order_items` | Checkout | 1 if customer_state != seller_state |
| `top_category_name` | Categorical | `dim_product` | Checkout | Primary product category |
| `primary_payment_type` | Categorical | `fact_orders` | Checkout | Payment method |

---

## 3. Customer Satisfaction / Review Risk Features

| Feature Name | Data Type | Source Entity | Availability Timing | Description |
| :--- | :--- | :--- | :--- | :--- |
| `total_delivery_duration_days` | Float | `fact_orders` | Delivery Completion | Actual transit days to customer |
| `delivery_delay_vs_estimated_days` | Float | `fact_orders` | Delivery Completion | Actual delivery date minus estimated date |
| `freight_ratio_pct` | Float | `fact_orders` | Delivery Completion | Freight burden percentage |
| `total_items_price_brl` | Float | `fact_orders` | Delivery Completion | Merchandise value |
| `total_freight_value_brl` | Float | `fact_orders` | Delivery Completion | Shipping cost |
| `total_item_count` | Integer | `fact_orders` | Delivery Completion | Number of items |
| `haversine_distance_km` | Float | `fact_order_items` | Delivery Completion | Physical transit distance |
| `seller_historical_review_score` | Float | `dim_seller` | Merchant Profile | Historical average seller rating |
| `is_delivered_late` | Binary | `fact_orders` | Delivery Completion | 1 if arrived late, else 0 |
| `is_interstate_shipment` | Binary | `fact_order_items` | Delivery Completion | Cross-border logistics |
| `primary_payment_type` | Categorical | `fact_orders` | Delivery Completion | Payment instrument |
| `top_category_name` | Categorical | `dim_product` | Delivery Completion | Product classification |
| `customer_state` | Categorical | `dim_customer` | Delivery Completion | Destination state |
