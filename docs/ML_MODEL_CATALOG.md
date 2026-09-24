# OlistIQ Machine Learning Model Catalog

Comprehensive catalog of implemented, validated, and registered machine learning models in OlistIQ.

---

## 1. Customer RFM Segmentation Engine

- **Model ID:** `customer_segmentation`
- **Version:** `v1.0`
- **Algorithm:** `K-Means Clustering` with `k-means++` initialization ($k=4$)
- **Primary Identifier:** `customer_unique_id` (enforces unique customer identity over transient `customer_id` tokens)
- **Features Used:**
  - `recency_days`: Days since latest purchase vs dataset reference date
  - `frequency_orders`: Lifetime completed order count
  - `monetary_spend_brl`: Total gross spend
  - `avg_order_value`: Mean spend per transaction
  - `avg_items_per_order`: Basket size depth
  - `category_diversity`: Count of distinct product categories purchased
- **Preprocessing:** `SimpleImputer(median)` + `RobustScaler` (resistant to extreme spend outliers)
- **Evaluation Performance:**
  - Silhouette Score: **0.5127**
  - Calinski-Harabasz Score: **89,804.37**
  - Training Population: **95,420 unique customers**
- **Discovered Segments & Profiles:**
  1. **Champions & High-Value (3.1%):** High frequency ($>1.5$), average spend $\text{R\$ } 620+$, category diversity 2.1.
  2. **High-Value At-Risk (17.7%):** Significant historical spend ($\text{R\$ } 275+$), high recency ($>280\text{ days}$).
  3. **Active & Promising (0.4%):** Large multi-item repeat buyers with recent orders.
  4. **Low-Engagement / Inactive (78.8%):** Single-order baseline buyers with low frequency ($1.03$) and modest basket size.

---

## 2. Delivery Delay Risk Classifier

- **Model ID:** `delivery_risk`
- **Version:** `v1.0`
- **Algorithm:** `HistGradientBoostingClassifier` with `class_weight="balanced"`
- **Target Variable:** `is_delivered_late` (1 if actual delivery date $>$ estimated delivery date, else 0)
- **Decision Timing:** Order Approval / Dispatch Planning Time (Pre-Fulfillment)
- **Validation Split:** Chronological Out-of-Time split ($<$ 2018-05-01 for training, $\ge$ 2018-05-01 for testing)
- **Sample Distribution:** 71,118 Train orders, 25,352 Out-of-Time Test orders
- **Evaluation Performance:**
  - Test ROC-AUC: **0.7287**
  - Test PR-AUC: **0.1295** (Baseline positive rate is 5.4%)
  - Test Recall: **34.60%**
  - Test F1 Score: **0.2145**
- **Primary Predictive Drivers:**
  - Haversine transit distance (km)
  - Historical seller SLA breach rate (%)
  - Interstate cross-border transit
  - Total freight cost ratio (%)
  - Estimated delivery duration window

---

## 3. Customer Satisfaction / Review Risk Model

- **Model ID:** `satisfaction_risk`
- **Version:** `v1.0`
- **Algorithm:** `RandomForestClassifier` with balanced class weights ($n=100$, $\text{max\_depth}=10$)
- **Target Variable:** `is_negative_review` (1 if `review_score <= 2`, else 0)
- **Decision Timing:** Post-fulfillment operational review
- **Leakage Prevention:** Review score, comments, title, sentiment scores, and review timestamps are strictly excluded from input features.
- **Validation Split:** Chronological Out-of-Time split ($<$ 2018-05-01 train, $\ge$ 2018-05-01 test)
- **Sample Distribution:** 70,582 Train orders, 25,242 Test orders
- **Evaluation Performance:**
  - Test ROC-AUC: **0.6862**
  - Test PR-AUC: **0.3003** (Baseline negative rate is 14.8%)
  - Test Recall: **40.67%**
  - Test F1 Score: **0.3382**
- **Primary Predictive Drivers:**
  - Delivery delay days vs estimated promise date
  - Total delivery duration (days)
  - Seller historical average rating
  - Freight value burden

---

## 4. Time-Series Demand & GMV Forecasters

- **Model ID:** `gmv_forecaster` & `orders_forecaster`
- **Version:** `v1.0`
- **Algorithm:** Autoregressive `GradientBoostingRegressor` with lag (t-1, t-7, t-14, t-28) and rolling 7/30-day window features
- **Horizon:** 30-day forward daily recursive forecast with 95% confidence bands
- **Validation Period:** Evaluated on holdout period (2018-06-01 to 2018-08-31, 92 days)
- **Evaluation Performance vs 7-Day Rolling Baseline:**
  - **Daily GMV Forecaster:**
    - Baseline 7-Day MAE: **R$ 7,812.04**
    - ML Forecaster MAE: **R$ 5,998.72**
    - **MAE Improvement: +23.2%**
    - Holdout $R^2$: **0.462**
  - **Daily Orders Forecaster:**
    - Baseline 7-Day MAE: **46.83 orders**
    - ML Forecaster MAE: **37.03 orders**
    - **MAE Improvement: +20.9%**
    - Holdout $R^2$: **0.489**

---

## 5. Business Anomaly Detection Engine

- **Model ID:** `business_anomalies`
- **Methodology:** 14-Day Rolling Window Statistical Z-Score ($\ge 2.5\sigma$) & Severity Tiering
- **Metrics Monitored:** `daily_gmv`, `daily_orders`, `daily_late_rate`, `avg_order_value`
- **Detections in Historical Dataset:** **25 significant operational anomalies** identified
- **Severity Categories:**
  - **Critical ($|Z| \ge 3.5$):** Black Friday revenue surges, major carrier strikes.
  - **High ($2.8 \le |Z| < 3.5$):** Regional logistics SLA breakdown spikes.
  - **Moderate ($2.5 \le |Z| < 2.8$):** Mid-week seasonal demand shifts.

---

## 6. Documented Rejected ML Ideas

1. **Item-Level Price Optimization (Elasticity Model):**
   - *Reason for Rejection:* Olist is a marketplace intermediary where sellers set prices independently across decentralized catalogs. Cross-sectional price elasticity without unit cost, wholesale margins, or competitor bids would lead to spurious pricing recommendations.
2. **Customer Churn Binary Classifier with Single-Order Horizon:**
   - *Reason for Rejection:* Over 96% of Olist customers are one-time buyers with an average observation window of 18 months. Modeling traditional subscription-style churn creates extreme class imbalance and false precision. RFM segmentation with recency scoring was implemented instead.
3. **Sentiment NLP Model on Review Text for Delay Prediction:**
   - *Reason for Rejection:* Serious data leakage. Review comments are created *after* delivery has succeeded or failed. Using sentiment to predict fulfillment risk violates chronological causality.
