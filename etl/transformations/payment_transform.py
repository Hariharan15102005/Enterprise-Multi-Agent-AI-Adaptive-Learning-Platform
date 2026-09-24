import pandas as pd
import numpy as np

def transform_payments(raw_payments_df: pd.DataFrame, raw_orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms payments dataset into fact_payments:
    1. Preserves sequence, tender type, installment count, and monetary value.
    2. Maps to date dimension key (order_date_key).
    """
    payments = raw_payments_df.copy()
    orders = raw_orders_df[['order_id', 'order_purchase_timestamp']].copy()
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'], errors='coerce')
    orders['order_date_key'] = orders['order_purchase_timestamp'].dt.strftime('%Y%m%d').fillna(20170101).astype(int)

    payments = pd.merge(payments, orders[['order_id', 'order_date_key']], on='order_id', how='left')
    payments['order_date_key'] = payments['order_date_key'].fillna(20170101).astype(int)

    # Impute missing or invalid payment types
    payments['payment_type'] = payments['payment_type'].fillna('not_defined')
    payments['payment_installments'] = payments['payment_installments'].fillna(1).astype(int)
    payments['payment_value_brl'] = payments['payment_value'].round(2)

    fact_payments = pd.DataFrame({
        'order_id': payments['order_id'],
        'payment_sequential': payments['payment_sequential'].astype(int),
        'payment_type': payments['payment_type'],
        'payment_installments': payments['payment_installments'],
        'payment_value_brl': payments['payment_value_brl'],
        'order_date_key': payments['order_date_key']
    })

    return fact_payments
