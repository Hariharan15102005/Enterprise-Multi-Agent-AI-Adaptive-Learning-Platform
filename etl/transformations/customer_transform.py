import pandas as pd
import numpy as np
from datetime import datetime

def transform_customers(
    raw_customers_df: pd.DataFrame,
    dim_geo_df: pd.DataFrame,
    raw_orders_df: pd.DataFrame = None,
    raw_items_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Transforms customers dataset:
    1. Aggregates from order-level customer_id to unique customer entity (customer_unique_id).
    2. Geocodes locations via dim_geolocation.
    3. Calculates RFM Recency, Frequency, Monetary metrics and customer segments.
    """
    cust = raw_customers_df.copy()

    # Deduplicate customer profile to 1 row per customer_unique_id
    # Take first known location details
    cust_unique = cust.groupby('customer_unique_id').agg(
        first_zip_code_prefix=('customer_zip_code_prefix', 'first'),
        current_city=('customer_city', 'first'),
        current_state=('customer_state', 'first')
    ).reset_index()

    # Merge geolocation coordinates
    geo_lookup = dim_geo_df[['zip_code_prefix', 'latitude', 'longitude']].drop_duplicates(subset=['zip_code_prefix'])
    cust_unique = pd.merge(cust_unique, geo_lookup, left_on='first_zip_code_prefix', right_on='zip_code_prefix', how='left')

    # Compute order aggregates if orders data provided
    if raw_orders_df is not None and raw_items_df is not None:
        orders = raw_orders_df.copy()
        items = raw_items_df.copy()

        # Merge orders with customers
        orders_merged = pd.merge(orders, cust[['customer_id', 'customer_unique_id']], on='customer_id', how='inner')
        orders_merged['order_purchase_timestamp'] = pd.to_datetime(orders_merged['order_purchase_timestamp'], errors='coerce')
        
        # Order items monetary total
        items_total = items.groupby('order_id')['price'].sum().reset_index()
        orders_with_spend = pd.merge(orders_merged, items_total, on='order_id', how='left')
        orders_with_spend['price'] = orders_with_spend['price'].fillna(0.0)

        # Customer level metrics
        snapshot_date = orders_merged['order_purchase_timestamp'].max()
        if pd.isna(snapshot_date):
            snapshot_date = datetime(2018, 10, 18)

        cust_metrics = orders_with_spend.groupby('customer_unique_id').agg(
            first_order_timestamp=('order_purchase_timestamp', 'min'),
            latest_order_timestamp=('order_purchase_timestamp', 'max'),
            lifetime_order_count=('order_id', 'nunique'),
            lifetime_spend_brl=('price', 'sum')
        ).reset_index()

        cust_metrics['lifetime_spend_brl'] = cust_metrics['lifetime_spend_brl'].round(2)
        cust_metrics['is_repeat_customer'] = cust_metrics['lifetime_order_count'] > 1
        cust_metrics['rfm_recency_days'] = (snapshot_date - cust_metrics['latest_order_timestamp']).dt.days.fillna(0).astype(int)

        # RFM Score calculations
        # R Score: lower recency days = higher score
        try:
            cust_metrics['r_score'] = pd.qcut(cust_metrics['rfm_recency_days'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
        except Exception:
            cust_metrics['r_score'] = 3

        # F Score: higher frequency = higher score
        cust_metrics['f_score'] = np.where(cust_metrics['lifetime_order_count'] >= 3, 5,
                                  np.where(cust_metrics['lifetime_order_count'] == 2, 4, 1))

        # M Score: higher spend = higher score
        try:
            cust_metrics['m_score'] = pd.qcut(cust_metrics['lifetime_spend_brl'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        except Exception:
            cust_metrics['m_score'] = 3

        # RFM Segment Assignment
        def assign_segment(row):
            r, f, m = row['r_score'], row['f_score'], row['m_score']
            if r >= 4 and f >= 4:
                return 'Champions / Loyalists'
            elif r >= 4 and m >= 4:
                return 'Recent High Spenders'
            elif r >= 3 and f == 1:
                return 'Standard Active Shoppers'
            elif r <= 2 and m >= 4:
                return 'At-Risk High Value'
            elif r <= 2 and f <= 2:
                return 'Hibernating / Lost'
            return 'General Shoppers'

        cust_metrics['rfm_segment'] = cust_metrics.apply(assign_segment, axis=1)

        cust_unique = pd.merge(cust_unique, cust_metrics, on='customer_unique_id', how='left')
    else:
        cust_unique['first_order_timestamp'] = None
        cust_unique['latest_order_timestamp'] = None
        cust_unique['lifetime_order_count'] = 1
        cust_unique['lifetime_spend_brl'] = 0.0
        cust_unique['is_repeat_customer'] = False
        cust_unique['rfm_recency_days'] = None
        cust_unique['r_score'] = None
        cust_unique['f_score'] = None
        cust_unique['m_score'] = None
        cust_unique['rfm_segment'] = 'Standard'

    dim_customer = pd.DataFrame({
        'customer_unique_id': cust_unique['customer_unique_id'],
        'first_zip_code_prefix': cust_unique['first_zip_code_prefix'],
        'current_city': cust_unique['current_city'],
        'current_state': cust_unique['current_state'],
        'latitude': cust_unique['latitude'].round(7),
        'longitude': cust_unique['longitude'].round(7),
        'first_order_timestamp': cust_unique['first_order_timestamp'],
        'latest_order_timestamp': cust_unique['latest_order_timestamp'],
        'lifetime_order_count': cust_unique['lifetime_order_count'].fillna(1).astype(int),
        'lifetime_spend_brl': cust_unique['lifetime_spend_brl'].fillna(0.0).round(2),
        'is_repeat_customer': cust_unique['is_repeat_customer'].fillna(False),
        'rfm_recency_days': cust_unique['rfm_recency_days'],
        'rfm_frequency_score': cust_unique['f_score'],
        'rfm_monetary_score': cust_unique['m_score'],
        'rfm_segment': cust_unique['rfm_segment'],
        'created_at': datetime.utcnow()
    })

    return dim_customer
