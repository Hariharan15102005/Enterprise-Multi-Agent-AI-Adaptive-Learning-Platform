# OlistIQ — Centralized Business Metric Definitions Dictionary

**Project:** OlistIQ AI-Powered E-Commerce Decision Intelligence Platform  
**Version:** 1.0 (Enterprise Standard)  
**Status:** Approved for Analytics, Backend APIs, and AI Analyst Grounding  

---

## Metric Governance & Calculation Standards

This document establishes unambiguous, mathematically standardized definitions for all core metrics used across **OlistIQ**. These exact formulas are implemented in the database transformation layer, exposed via FastAPI endpoints, and enforced as grounding rules for the AI Analyst.

---

## 1. Executive & Financial Metrics

### 1.1 Gross Merchandise Value (GMV)
- **Business Meaning:** Total gross value of goods sold across the marketplace, excluding shipping fees and voucher discounts.
- **Formula:** 
  $$\text{GMV} = \sum \text{fact\_order\_items.item\_price\_brl}$$
- **Source Table & Column:** `fact_order_items.item_price_brl` (or `fact_orders.total_items_price_brl`)
- **Default Filters:** `order_status NOT IN ('canceled', 'unavailable')`
- **Granularity:** Line-item additive / Order additive

### 1.2 Gross Order Value (GOV)
- **Business Meaning:** Total invoiced customer basket value including product prices and freight charges.
- **Formula:** 
  $$\text{GOV} = \sum (\text{fact\_order\_items.item\_price\_brl} + \text{fact\_order\_items.freight\_value\_brl})$$
- **Source Table & Column:** `fact_orders.gross_order_value_brl`

### 1.3 Net Captured Payment Revenue
- **Business Meaning:** Total monetary settlement captured via payment gateways across all payment methods.
- **Formula:** 
  $$\text{Net Revenue} = \sum \text{fact\_payments.payment\_value\_brl}$$
- **Source Table & Column:** `fact_payments.payment_value_brl`
- **Discrepancy Note:** May slightly vary from GOV on ~0.39% of orders due to post-basket vouchers and rounding.

### 1.4 Average Order Value (AOV)
- **Business Meaning:** Average gross merchandise spend generated per distinct customer order.
- **Formula:** 
  $$\text{AOV} = \frac{\text{GMV}}{\text{Count of Unique Orders}} = \frac{\sum \text{fact\_orders.total\_items\_price\_brl}}{\text{COUNT}(\text{fact\_orders.order\_id})}$$
- **Source Table:** `fact_orders`

### 1.5 Total Freight Spend & Freight-to-GMV Ratio
- **Business Meaning:** Total logistics fees collected and freight cost burden relative to item price.
- **Formula:** 
  $$\text{Freight Ratio (\%)} = \left( \frac{\sum \text{fact\_order\_items.freight\_value\_brl}}{\sum \text{fact\_order\_items.item\_price\_brl}} \right) \times 100$$
- **Source Table:** `fact_order_items`

---

## 2. Fulfillment & Logistics Metrics

### 2.1 Carrier Transit Time (Days)
- **Business Meaning:** Elapsed time taken by logistics carriers from physical parcel pickup to doorstep delivery.
- **Formula:** 
  $$\text{Carrier Transit Days} = \frac{\text{delivered\_customer\_timestamp} - \text{delivered\_carrier\_timestamp}}{86400 \text{ seconds}}$$
- **Source Table & Column:** `fact_orders.total_delivery_duration_days` / `fact_order_items.carrier_transit_days`
- **Filter:** `delivered_customer_timestamp IS NOT NULL AND delivered_carrier_timestamp IS NOT NULL`

### 2.2 Seller Dispatch Lead Time (Hours)
- **Business Meaning:** Elapsed hours taken by a merchant from payment approval to carrier handoff.
- **Formula:** 
  $$\text{Dispatch Lead Hours} = \frac{\text{delivered\_carrier\_timestamp} - \text{approved\_timestamp}}{3600 \text{ seconds}}$$
- **Source Table & Column:** `fact_order_items.dispatch_lead_time_hours`

### 2.3 On-Time Delivery Rate (%)
- **Business Meaning:** Percentage of delivered customer orders that arrived on or before the estimated delivery SLA.
- **Formula:** 
  $$\text{On-Time Delivery Rate} = \left( \frac{\text{COUNT}(\text{Orders with } \text{is\_delivered\_late} = \text{FALSE})}{\text{COUNT}(\text{Delivered Orders})} \right) \times 100$$
- **Source Table & Column:** `fact_orders.is_delivered_late`

### 2.4 Average Delivery Delay (Days)
- **Business Meaning:** Average number of days late for orders that breached their estimated delivery SLA.
- **Formula:** 
  $$\text{Avg Delay Days} = \text{AVG}(\text{delivery\_delay\_vs\_estimated\_days}) \quad \text{WHERE } \text{is\_delivered\_late} = \text{TRUE}$$
- **Source Table & Column:** `fact_orders.delivery_delay_vs_estimated_days`

### 2.5 Seller SLA Breach Rate (%)
- **Business Meaning:** Percentage of order items where carrier handoff occurred after the assigned shipping limit deadline.
- **Formula:** 
  $$\text{Seller SLA Breach Rate} = \left( \frac{\text{COUNT}(\text{Items with } \text{delivered\_carrier\_timestamp} > \text{shipping\_limit\_timestamp})}{\text{COUNT}(\text{Total Dispatched Items})} \right) \times 100$$
- **Source Table & Column:** `fact_order_items.is_seller_sla_breach`

---

## 3. Customer Intelligence & Retention Metrics

### 3.1 Total Unique Consumers
- **Business Meaning:** Distinct physical human customers who have placed at least one order.
- **Formula:** 
  $$\text{Unique Customers} = \text{COUNT}(\text{DISTINCT } \text{dim\_customer.customer\_unique\_id})$$
- **Source Table:** `dim_customer`

### 3.2 Repeat Customer Rate (%)
- **Business Meaning:** Proportion of total consumers who have placed $\ge 2$ distinct orders across their lifetime.
- **Formula:** 
  $$\text{Repeat Customer Rate} = \left( \frac{\text{COUNT}(\text{Customers with } \text{lifetime\_order\_count} > 1)}{\text{COUNT}(\text{Total Unique Customers})} \right) \times 100$$
- **Source Table & Column:** `dim_customer.is_repeat_customer` (~3.12% in baseline dataset).

### 3.3 Customer Lifetime Value (LTV Proxy)
- **Business Meaning:** Cumulative gross monetary spend generated by a unique consumer.
- **Formula:** 
  $$\text{Customer LTV} = \text{dim\_customer.lifetime\_spend\_brl} = \sum \text{price across all historical orders}$$
- **Source Table & Column:** `dim_customer.lifetime_spend_brl`

### 3.4 RFM Recency (Days)
- **Business Meaning:** Days elapsed between the consumer's most recent order timestamp and the dataset snapshot date (2018-10-18).
- **Formula:** 
  $$\text{Recency Days} = \text{Date}(\text{Snapshot}) - \text{Date}(\text{latest\_order\_timestamp})$$
- **Source Table & Column:** `dim_customer.rfm_recency_days`

---

## 4. Customer Satisfaction & Review Metrics

### 4.1 Customer Satisfaction Score (CSAT / Avg Review Score)
- **Business Meaning:** Arithmetic mean of customer survey review scores on a 1.0 to 5.0 star scale.
- **Formula:** 
  $$\text{CSAT} = \text{AVG}(\text{fact\_reviews.review\_score})$$
- **Source Table & Column:** `fact_reviews.review_score` (Baseline: 4.09★)

### 4.2 Net Promoter Score Proxy (NPS Proxy)
- **Business Meaning:** Customer advocacy index computed as the difference between Promoters (5★) and Detractors (1★ and 2★).
- **Formula:** 
  $$\text{NPS Proxy} = \left( \frac{\text{Count}(5\star) - \text{Count}(1\star + 2\star)}{\text{Total Reviews}} \right) \times 100$$
- **Source Table:** `fact_reviews`

---

## 5. Metric Summary Quick Reference Matrix

| Metric ID | Standard Name | Primary Table | Grain | Aggregation Function | Expected Format |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MET-FIN-01` | Gross Merchandise Value (GMV) | `fact_order_items` | Item | `SUM(item_price_brl)` | Currency (BRL R$) |
| `MET-FIN-02` | Average Order Value (AOV) | `fact_orders` | Order | `AVG(gross_order_value_brl)` | Currency (BRL R$) |
| `MET-FIN-03` | Net Captured Payment | `fact_payments` | Payment | `SUM(payment_value_brl)` | Currency (BRL R$) |
| `MET-LOG-01` | On-Time Delivery Rate | `fact_orders` | Order | `100.0 * AVG(NOT is_delivered_late)` | Percentage (0–100%) |
| `MET-LOG-02` | Carrier Transit Days | `fact_orders` | Order | `AVG(total_delivery_duration_days)` | Continuous (Days) |
| `MET-LOG-03` | Seller SLA Breach Rate | `fact_order_items` | Item | `100.0 * AVG(is_seller_sla_breach)` | Percentage (0–100%) |
| `MET-CUST-01`| Total Unique Customers | `dim_customer` | Customer | `COUNT(customer_unique_id)` | Integer Count |
| `MET-CUST-02`| Repeat Purchase Rate | `dim_customer` | Customer | `100.0 * AVG(is_repeat_customer)` | Percentage (0–100%) |
| `MET-CSAT-01`| Average Review Score | `fact_reviews` | Review | `AVG(review_score)` | Rating (1.00–5.00★) |
