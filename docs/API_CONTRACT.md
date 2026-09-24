# OlistIQ — REST API Specification & Contract

**Project:** OlistIQ AI-Powered E-Commerce Decision Intelligence Platform  
**Backend Framework:** FastAPI (Python 3.11+)  
**Frontend Client:** React 18+ (TypeScript)  
**Protocol:** HTTP/1.1 REST + JSON  
**Base URL:** `/api/v1`  
**Status:** Implemented & Verified  

---

## 1. Global API Standards & Envelopes

### Standard Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "metadata": null
}
```

### Paginated Response Envelope
```json
{
  "success": true,
  "data": [ ... ],
  "metadata": {
    "page": 1,
    "page_size": 20,
    "total_records": 96096,
    "total_pages": 4805
  }
}
```

### Standard Error Response Schema
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters or payload.",
    "details": { ... }
  }
}
```

---

## 2. Implemented Endpoints Reference

---

### System Health
- **`GET /health`**
  - **Purpose:** Service health status.
  - **Response `200 OK`:** `{"status": "healthy", "service": "OlistIQ Decision Intelligence API", "version": "1.0.0", "environment": "development"}`

---

### Module 1: Executive Dashboard
- **`GET /api/v1/dashboard/kpis`**
  - **Query Params:** `start_date` (ISO string), `end_date` (ISO string), `state` (2-letter state code)
  - **Response `200 OK`:** Returns `gross_merchandise_value`, `total_orders`, `total_customers`, `total_sellers`, `total_products`, `average_order_value`, `average_review_score`, `on_time_delivery_rate`, `late_delivery_rate`, `repeat_customer_rate`, `total_freight_value`.
- **`GET /api/v1/dashboard/summary`**
  - **Response `200 OK`:** Returns executive KPIs, `top_selling_category`, `top_revenue_state`, and `active_sellers_count`.

---

### Module 2: Business Analytics
- **`GET /api/v1/analytics/revenue`**
  - **Query Params:** `interval` (`month` | `day`), `start_date`, `end_date`
  - **Response `200 OK`:** Array of time-series objects containing `period`, `year`, `month`, `gmv`, `freight_value`, `order_count`, `aov`, `avg_review_score`, `late_orders_count`.
- **`GET /api/v1/analytics/categories`**
  - **Query Params:** `limit` (default 20), `sort_by` (`gmv` | `orders` | `late_rate`), `start_date`, `end_date`
  - **Response `200 OK`:** Array of category metrics (`category_name_en`, `total_orders`, `total_items_sold`, `total_gmv`, `total_freight`, `avg_price`, `late_rate_pct`).
- **`GET /api/v1/analytics/payments`**
  - **Response `200 OK`:** Array of payment methods (`payment_type`, `total_transactions`, `total_payment_value`, `avg_payment_value`, `avg_installments`, `share_pct`).
- **`GET /api/v1/analytics/insights`**
  - **Response `200 OK`:** Array of computed operational insights (`id`, `type`, `title`, `description`, `severity`, `metric_value`, `suggested_action`).

---

### Module 3: Customer Intelligence & RFM
- **`GET /api/v1/customers/segments`**
  - **Response `200 OK`:** Array of RFM clusters (`segment_name`, `customer_count`, `share_pct`, `total_spend_brl`, `avg_recency_days`, `avg_frequency`, `avg_monetary_spend`).
- **`GET /api/v1/customers/geo`**
  - **Response `200 OK`:** Array of state customer distributions with coordinates (`state_code`, `customer_count`, `total_spend_brl`, `avg_spend_per_customer`, `repeat_customer_rate`, `latitude`, `longitude`).
- **`GET /api/v1/customers/list`**
  - **Query Params:** `page` (default 1), `page_size` (default 20, max 100), `segment`, `state`
  - **Response `200 OK`:** Paginated customer summaries with RFM scores.

---

### Module 4: Product Intelligence
- **`GET /api/v1/products/list`**
  - **Query Params:** `page` (default 1), `page_size` (default 20, max 100), `category`, `sort_by` (`items_sold` | `gmv`)
  - **Response `200 OK`:** Paginated product catalog items with volume, density, weight, GMV, and size tier.

---

### Module 5: Seller Intelligence
- **`GET /api/v1/sellers/leaderboard`**
  - **Query Params:** `page` (default 1), `page_size` (default 20, max 100), `tier`, `state`
  - **Response `200 OK`:** Paginated merchant performance metrics (`seller_id`, `seller_city`, `seller_state`, `seller_tier`, `orders_fulfilled`, `total_sales_value_brl`, `avg_order_value_brl`).

---

### Module 6: Logistics & Supply Chain
- **`GET /api/v1/logistics/overview`**
  - **Response `200 OK`:** High-level logistics SLA summary (`avg_delivery_days`, `median_delivery_days`, `on_time_delivery_rate`, `late_delivery_rate`, `avg_delay_days_for_late_orders`, `avg_seller_dispatch_hours`, `avg_carrier_transit_days`, `interstate_orders_pct`).
- **`GET /api/v1/logistics/by-state`**
  - **Response `200 OK`:** Delivery lead times and late rates broken down by destination state.
- **`GET /api/v1/logistics/by-seller`**
  - **Query Params:** `limit` (default 20)
  - **Response `200 OK`:** Merchant dispatch lead time (hours) and SLA breach rate.

---

### Module 7: Data Quality Center
- **`GET /api/v1/data-quality/overview`**
  - **Response `200 OK`:** Live dataset health scorecard (`overall_quality_score`: 100.0, `status`: "HEALTHY", `tables_monitored`: 9, `total_rows_monitored`: 1,545,667, `checks`: [...]).
