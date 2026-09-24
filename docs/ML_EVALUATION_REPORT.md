# OlistIQ ML Evaluation & Benchmark Report

Empirical evaluation results from actual training and out-of-time test validation runs.

---

## 1. Summary of Model Performance

| Model Name | Model Type | Task | Key Metric 1 | Key Metric 2 | Benchmark Baseline | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_segmentation` | K-Means ($k=4$) | Unsupervised | **Silhouette: 0.5127** | **CH Score: 89,804** | Silhouette > 0.40 | **Active (v1.0)** |
| `delivery_risk` | HistGradientBoosting | Classification | **ROC-AUC: 0.7287** | **Recall: 34.60%** | Random/Prior (0.50) | **Active (v1.0)** |
| `satisfaction_risk` | RandomForest | Classification | **ROC-AUC: 0.6862** | **Recall: 40.67%** | Random/Prior (0.50) | **Active (v1.0)** |
| `gmv_forecaster` | GradientBoosting (Lag) | Time Series | **MAE: R$ 5,998.72** | **$R^2$: 0.462** | Baseline MAE: R$ 7,812.04 | **Active (v1.0)** |
| `orders_forecaster` | GradientBoosting (Lag) | Time Series | **MAE: 37.03 orders**| **$R^2$: 0.489** | Baseline MAE: 46.83 orders | **Active (v1.0)** |
| `business_anomalies` | Rolling Z-Score ($2.5\sigma$) | Anomaly | **25 Detected** | **100% Explained** | Static Thresholds | **Active (v1.0)** |

---

## 2. Customer Segmentation Evaluation

- **Evaluation Dataset:** 95,420 unique customer records
- **Preprocessing:** Median Imputation + RobustScaler
- **Silhouette Coefficient:** **0.5127** (indicates strong cluster separation with minimal overlap)
- **Cluster Breakdown:**
  - Cluster 0 (16,870 users / 17.68%): Average spend R$ 274.79, avg recency 287.6 days (*High-Value At-Risk*)
  - Cluster 1 (75,224 users / 78.83%): Average spend R$ 104.30, avg recency 286.7 days (*Low-Engagement / Inactive*)
  - Cluster 2 (2,924 users / 3.06%): Average spend R$ 621.40, avg frequency 1.54, diversity 2.1 (*Champions & High-Value*)
  - Cluster 3 (402 users / 0.42%): Average items per order 4.8 (*Active & Promising Basket Buyers*)

---

## 3. Delivery Risk Classifier Evaluation

- **Train Set (Prior to 2018-05-01):** 71,118 orders
- **Out-of-Time Test Set ($\ge$ 2018-05-01):** 25,352 orders
- **Positive Class (Late Deliveries):** 1,370 orders in test set (5.40%)
- **Test Metrics:**
  - **ROC-AUC:** `0.7287`
  - **PR-AUC (Average Precision):** `0.1295` (2.4x higher than random chance of 0.054)
  - **F1 Score:** `0.2145`
  - **Recall:** `0.3460` (successfully intercepts 34.6% of all late deliveries before carrier dispatch)
  - **Precision:** `0.1558`
  - **Confusion Matrix:**
    - True Negatives: 21,414
    - False Positives: 2,568
    - False Negatives: 896
    - True Positives: 474

---

## 4. Customer Satisfaction / Review Risk Evaluation

- **Train Set:** 70,582 orders
- **Out-of-Time Test Set:** 25,242 orders
- **Positive Class (Negative Review $\le$ 2 stars):** 3,745 orders in test set (14.83%)
- **Test Metrics:**
  - **ROC-AUC:** `0.6862`
  - **PR-AUC:** `0.3003` (2.0x higher than random chance of 0.148)
  - **Recall:** `0.4067`
  - **Precision:** `0.2902`
  - **F1 Score:** `0.3382`

---

## 5. Forecasting Evaluation vs Baseline

- **Holdout Period:** 2018-06-01 to 2018-08-31 (92 consecutive days)
- **Baseline Model:** 7-Day Rolling Moving Average

### GMV Forecaster
- **Baseline 7-Day MAE:** R$ 7,812.04
- **ML GradientBoosting MAE:** R$ 5,998.72
- **Relative MAE Reduction:** **-23.2%**
- **RMSE:** R$ 7,450.31

### Order Volume Forecaster
- **Baseline 7-Day MAE:** 46.83 orders/day
- **ML GradientBoosting MAE:** 37.03 orders/day
- **Relative MAE Reduction:** **-20.9%**
- **RMSE:** 48.12 orders/day
