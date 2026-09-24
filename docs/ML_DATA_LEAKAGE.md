# OlistIQ Data Leakage Prevention & Validation Report

## 1. Overview & Threat Vectors

In e-commerce machine learning systems, data leakage occurs when information from after the target event is inadvertently included in the feature set during training or evaluation. This causes artificially inflated offline performance that degrades completely in production.

OlistIQ enforces strict data leakage prevention protocols across all supervised models.

---

## 2. Leakage Prevention by Model

### A. Delivery Delay Risk Model

- **Decision Timestamp:** `order_approved_at` / Pre-dispatch checkout
- **Objective:** Predict whether `order_delivered_customer_date > order_estimated_delivery_date`
- **Strictly Prohibited & Excluded Features:**
  - `delivered_carrier_timestamp` (carrier handover time is unknown at order creation)
  - `delivered_customer_timestamp` (actual delivery time)
  - `carrier_transit_days` (post-dispatch metric)
  - `actual_delivery_duration_days` (target proxy)
  - `total_delivery_days` (target proxy)
  - `delivery_delay_days` (direct target leak)
  - `review_score` / `fact_reviews` (reviews occur post-delivery)
- **Allowed Features:**
  - Buyer/Seller zip codes & geodesic distance (`haversine_distance_km`)
  - Promised SLA window (`estimated_delivery_timestamp - purchase_timestamp`)
  - Order basket metrics (item count, price, freight ratio, product weight/volume)
  - Historical seller SLA breach rate before the transaction

### B. Customer Satisfaction / Review Risk Model

- **Decision Timestamp:** `delivered_customer_timestamp` (Post-fulfillment completion)
- **Objective:** Predict whether customer will leave a $\le 2$-star review (`is_negative_review`)
- **Strictly Prohibited & Excluded Features:**
  - `review_score` (target definition)
  - `review_comment_title` & `review_comment_message` (post-review text)
  - `review_creation_date` & `review_answer_timestamp` (review event metadata)
  - `sentiment_score` & `sentiment_label` (derived from review text)
- **Allowed Features:**
  - Delivery SLA breach flag and delay in days
  - Total transit duration
  - Product category, order value, and freight ratio
  - Historical merchant rating

### C. Time Series Demand Forecasting

- **Leakage Prevention:**
  - Autoregressive lag features are constructed strictly with $t-1, t-7, t-14, t-28$ shifts.
  - Rolling windows use `shift(1)` to ensure current day data is never in the rolling mean.
  - Evaluation uses forward out-of-sample chronological splits, not random k-fold cross-validation.

---

## 3. Automated Leakage Validation Tests

Automated regression tests in `tests/test_ml_models.py::test_data_leakage_strict_prevention` verify that prohibited leakage columns are completely absent from `DELIVERY_RISK_FEATURES` and `SATISFACTION_FEATURES`.
