import pandas as pd
import numpy as np

def transform_orders(
    raw_orders_df: pd.DataFrame,
    raw_customers_df: pd.DataFrame,
    raw_items_df: pd.DataFrame,
    raw_payments_df: pd.DataFrame,
    raw_reviews_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms orders into consolidated fact_orders:
    1. Parses all lifecycle timestamps safely (retains NULLs for in-flight/cancelled orders).
    2. Maps customer_id to customer_unique_id.
    3. Aggregates item-level basket financials and payment methods.
    4. Calculates delivery lead times, delays, and integrates review scores.
    """
    orders = raw_orders_df.copy()
    cust = raw_customers_df[['customer_id', 'customer_unique_id']].copy()
    items = raw_items_df.copy()
    payments = raw_payments_df.copy()
    reviews = raw_reviews_df.copy()

    # 1. Map customer_unique_id
    orders = pd.merge(orders, cust, on='customer_id', how='left')

    # 2. Parse timestamps
    ts_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in ts_cols:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # Date key (YYYYMMDD)
    orders['order_date_key'] = orders['order_purchase_timestamp'].dt.strftime('%Y%m%d').astype(int)

    # 3. Aggregate Item financials
    item_agg = items.groupby('order_id').agg(
        total_item_count=('order_item_id', 'count'),
        unique_product_count=('product_id', 'nunique'),
        unique_seller_count=('seller_id', 'nunique'),
        total_items_price_brl=('price', 'sum'),
        total_freight_value_brl=('freight_value', 'sum')
    ).reset_index()
    item_agg['gross_order_value_brl'] = (item_agg['total_items_price_brl'] + item_agg['total_freight_value_brl']).round(2)
    orders = pd.merge(orders, item_agg, on='order_id', how='left')
    orders['total_item_count'] = orders['total_item_count'].fillna(0).astype(int)
    orders['unique_product_count'] = orders['unique_product_count'].fillna(0).astype(int)
    orders['unique_seller_count'] = orders['unique_seller_count'].fillna(0).astype(int)
    orders['total_items_price_brl'] = orders['total_items_price_brl'].fillna(0.0).round(2)
    orders['total_freight_value_brl'] = orders['total_freight_value_brl'].fillna(0.0).round(2)
    orders['gross_order_value_brl'] = orders['gross_order_value_brl'].fillna(0.0).round(2)

    # 4. Aggregate Payments
    # Primary payment type = most frequent or highest value
    pay_agg = payments.groupby('order_id').agg(
        total_payment_value_brl=('payment_value', 'sum'),
        primary_payment_type=('payment_type', lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]),
        max_payment_installments=('payment_installments', 'max'),
        payment_sequential_count=('payment_sequential', 'max')
    ).reset_index()
    pay_agg['total_payment_value_brl'] = pay_agg['total_payment_value_brl'].round(2)
    orders = pd.merge(orders, pay_agg, on='order_id', how='left')
    orders['total_payment_value_brl'] = orders['total_payment_value_brl'].fillna(0.0)
    orders['primary_payment_type'] = orders['primary_payment_type'].fillna('not_defined')
    orders['max_payment_installments'] = orders['max_payment_installments'].fillna(1).astype(int)
    orders['payment_sequential_count'] = orders['payment_sequential_count'].fillna(1).astype(int)
    orders['payment_value_discrepancy_brl'] = (orders['gross_order_value_brl'] - orders['total_payment_value_brl']).abs().round(2)

    # 5. Delivery Performance Calculations
    delivered = orders['order_delivered_customer_date']
    purchase = orders['order_purchase_timestamp']
    estimated = orders['order_estimated_delivery_date']

    orders['total_delivery_duration_days'] = np.where(
        delivered.notna() & purchase.notna(),
        (delivered - purchase).dt.total_seconds() / 86400.0,
        np.nan
    )
    orders['total_delivery_duration_days'] = orders['total_delivery_duration_days'].round(2)

    orders['delivery_delay_vs_estimated_days'] = np.where(
        delivered.notna() & estimated.notna(),
        (delivered - estimated).dt.total_seconds() / 86400.0,
        np.nan
    )
    orders['delivery_delay_vs_estimated_days'] = orders['delivery_delay_vs_estimated_days'].round(2)

    orders['is_delivered_late'] = np.where(
        delivered.notna() & estimated.notna(),
        delivered > estimated,
        False
    )

    # 6. Reviews Integration (Deduplicate to latest review per order)
    rev_sorted = reviews.sort_values(by=['order_id', 'review_answer_timestamp'], ascending=[True, False])
    rev_unique = rev_sorted.drop_duplicates(subset=['order_id']).copy()
    rev_unique['review_creation_timestamp'] = pd.to_datetime(rev_unique['review_creation_date'], errors='coerce')
    rev_unique['review_answer_timestamp'] = pd.to_datetime(rev_unique['review_answer_timestamp'], errors='coerce')
    
    rev_merge = rev_unique[['order_id', 'review_score', 'review_creation_timestamp', 'review_answer_timestamp']].copy()
    orders = pd.merge(orders, rev_merge, on='order_id', how='left')
    orders['has_review'] = orders['review_score'].notna()

    fact_orders = pd.DataFrame({
        'order_id': orders['order_id'],
        'customer_id': orders['customer_id'],
        'customer_unique_id': orders['customer_unique_id'],
        'order_status': orders['order_status'],
        'order_date_key': orders['order_date_key'],
        'purchase_timestamp': orders['order_purchase_timestamp'],
        'approved_timestamp': orders['order_approved_at'],
        'delivered_carrier_timestamp': orders['order_delivered_carrier_date'],
        'delivered_customer_timestamp': orders['order_delivered_customer_date'],
        'estimated_delivery_timestamp': orders['order_estimated_delivery_date'],
        'total_item_count': orders['total_item_count'],
        'unique_product_count': orders['unique_product_count'],
        'unique_seller_count': orders['unique_seller_count'],
        'total_items_price_brl': orders['total_items_price_brl'],
        'total_freight_value_brl': orders['total_freight_value_brl'],
        'gross_order_value_brl': orders['gross_order_value_brl'],
        'total_payment_value_brl': orders['total_payment_value_brl'],
        'payment_value_discrepancy_brl': orders['payment_value_discrepancy_brl'],
        'primary_payment_type': orders['primary_payment_type'],
        'max_payment_installments': orders['max_payment_installments'],
        'payment_sequential_count': orders['payment_sequential_count'],
        'total_delivery_duration_days': orders['total_delivery_duration_days'],
        'delivery_delay_vs_estimated_days': orders['delivery_delay_vs_estimated_days'],
        'is_delivered_late': orders['is_delivered_late'],
        'review_score': orders['review_score'],
        'has_review': orders['has_review'],
        'review_creation_timestamp': orders['review_creation_timestamp'],
        'review_answer_timestamp': orders['review_answer_timestamp']
    })

    return fact_orders
