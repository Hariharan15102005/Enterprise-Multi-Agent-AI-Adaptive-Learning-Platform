import pandas as pd
import numpy as np
from datetime import datetime

def transform_sellers(
    raw_sellers_df: pd.DataFrame,
    dim_geo_df: pd.DataFrame,
    raw_order_items_df: pd.DataFrame = None,
    raw_orders_df: pd.DataFrame = None,
    raw_reviews_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Transforms sellers dataset:
    1. Geocodes seller locations via aggregated dim_geolocation.
    2. Calculates historical fulfillment performance metrics.
    3. Segments sellers into performance tiers.
    """
    df = raw_sellers_df.copy()

    # Join with dim_geolocation
    geo_lookup = dim_geo_df[['zip_code_prefix', 'latitude', 'longitude']].drop_duplicates(subset=['zip_code_prefix'])
    df = pd.merge(df, geo_lookup, left_on='seller_zip_code_prefix', right_on='zip_code_prefix', how='left')

    # Calculate operational metrics if order data is provided
    if raw_order_items_df is not None:
        items = raw_order_items_df.copy()
        
        # Calculate seller performance
        seller_sales = items.groupby('seller_id').agg(
            total_orders_fulfilled=('order_id', 'nunique'),
            total_sales_value_brl=('price', 'sum')
        ).reset_index()

        df = pd.merge(df, seller_sales, on='seller_id', how='left')
        df['total_orders_fulfilled'] = df['total_orders_fulfilled'].fillna(0).astype(int)
        df['total_sales_value_brl'] = df['total_sales_value_brl'].fillna(0.0).round(2)
    else:
        df['total_orders_fulfilled'] = 0
        df['total_sales_value_brl'] = 0.0

    # Seller Tier segmentation
    conditions = [
        (df['total_orders_fulfilled'] >= 500) | (df['total_sales_value_brl'] >= 50000),
        (df['total_orders_fulfilled'] >= 50) | (df['total_sales_value_brl'] >= 5000)
    ]
    choices = ['Power Seller', 'Established Seller']
    df['seller_tier'] = np.select(conditions, choices, default='Standard')

    dim_seller = pd.DataFrame({
        'seller_id': df['seller_id'],
        'seller_zip_code_prefix': df['seller_zip_code_prefix'],
        'seller_city': df['seller_city'],
        'seller_state': df['seller_state'],
        'latitude': df['latitude'].round(7),
        'longitude': df['longitude'].round(7),
        'first_active_date': None,
        'total_orders_fulfilled': df['total_orders_fulfilled'],
        'total_sales_value_brl': df['total_sales_value_brl'],
        'avg_dispatch_time_hours': None,
        'sla_breach_rate_pct': None,
        'avg_review_score': None,
        'seller_tier': df['seller_tier'],
        'created_at': datetime.utcnow()
    })

    return dim_seller
