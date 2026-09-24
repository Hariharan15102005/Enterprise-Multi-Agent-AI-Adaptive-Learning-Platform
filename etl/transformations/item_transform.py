import pandas as pd
import numpy as np
from datetime import datetime

def haversine_vectorized(lat1, lon1, lat2, lon2):
    """
    Vectorized calculation of great circle distance in km between coordinate pairs.
    """
    R = 6371.0 # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    return (R * c).round(2)

def transform_order_items(
    raw_items_df: pd.DataFrame,
    raw_orders_df: pd.DataFrame,
    raw_customers_df: pd.DataFrame,
    raw_sellers_df: pd.DataFrame,
    dim_geo_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms line-item level dataset into fact_order_items:
    1. Associates orders, customer identities, and merchant locations.
    2. Calculates physical transit distances (Haversine km) and interstate flags.
    3. Calculates item-level SLA breaches, freight ratios, and transit days.
    """
    items = raw_items_df.copy()
    orders = raw_orders_df.copy()
    cust = raw_customers_df.copy()
    sellers = raw_sellers_df.copy()
    geo = dim_geo_df[['zip_code_prefix', 'latitude', 'longitude']].drop_duplicates(subset=['zip_code_prefix']).copy()

    # Parse timestamps
    for col in ['shipping_limit_date']:
        items[col] = pd.to_datetime(items[col], errors='coerce')
    for col in ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # Merge Orders attributes
    items = pd.merge(
        items,
        orders[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']],
        on='order_id',
        how='inner'
    )

    # Date key (YYYYMMDD)
    items['order_date_key'] = items['order_purchase_timestamp'].dt.strftime('%Y%m%d').astype(int)

    # Merge Customer attributes
    items = pd.merge(
        items,
        cust[['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 'customer_state']],
        on='customer_id',
        how='inner'
    )

    # Merge Seller attributes
    items = pd.merge(
        items,
        sellers[['seller_id', 'seller_zip_code_prefix', 'seller_state']],
        on='seller_id',
        how='inner'
    )

    # Merge Customer Coordinates
    items = pd.merge(
        items,
        geo.rename(columns={'zip_code_prefix': 'customer_zip_code_prefix', 'latitude': 'cust_lat', 'longitude': 'cust_lng'}),
        on='customer_zip_code_prefix',
        how='left'
    )

    # Merge Seller Coordinates
    items = pd.merge(
        items,
        geo.rename(columns={'zip_code_prefix': 'seller_zip_code_prefix', 'latitude': 'seller_lat', 'longitude': 'seller_lng'}),
        on='seller_zip_code_prefix',
        how='left'
    )

    # Distance calculation
    has_coords = items['cust_lat'].notna() & items['seller_lat'].notna()
    items['haversine_distance_km'] = np.where(
        has_coords,
        haversine_vectorized(items['cust_lat'], items['cust_lng'], items['seller_lat'], items['seller_lng']),
        np.nan
    )

    items['is_interstate_shipment'] = items['customer_state'] != items['seller_state']

    # Financial calculations
    items['item_price_brl'] = items['price'].round(2)
    items['freight_value_brl'] = items['freight_value'].round(2)
    items['total_item_cost_brl'] = (items['item_price_brl'] + items['freight_value_brl']).round(2)
    items['freight_ratio_pct'] = np.where(
        items['item_price_brl'] > 0,
        ((items['freight_value_brl'] / items['item_price_brl']) * 100).round(2),
        0.0
    )

    # Logistics SLA & Durations
    approved = items['order_approved_at']
    carrier = items['order_delivered_carrier_date']
    customer_deliv = items['order_delivered_customer_date']
    estimated = items['order_estimated_delivery_date']
    shipping_limit = items['shipping_limit_date']
    purchase = items['order_purchase_timestamp']

    items['dispatch_lead_time_hours'] = np.where(
        carrier.notna() & approved.notna(),
        ((carrier - approved).dt.total_seconds() / 3600.0).round(2),
        np.nan
    )

    items['carrier_transit_days'] = np.where(
        customer_deliv.notna() & carrier.notna(),
        ((customer_deliv - carrier).dt.total_seconds() / 86400.0).round(2),
        np.nan
    )

    items['total_delivery_days'] = np.where(
        customer_deliv.notna() & purchase.notna(),
        ((customer_deliv - purchase).dt.total_seconds() / 86400.0).round(2),
        np.nan
    )

    items['estimated_delivery_days'] = np.where(
        estimated.notna() & purchase.notna(),
        ((estimated - purchase).dt.total_seconds() / 86400.0).round(2),
        np.nan
    )

    items['delivery_delay_days'] = np.where(
        customer_deliv.notna() & estimated.notna(),
        ((customer_deliv - estimated).dt.total_seconds() / 86400.0).round(2),
        np.nan
    )

    items['is_delayed'] = np.where(
        customer_deliv.notna() & estimated.notna(),
        customer_deliv > estimated,
        False
    )

    items['is_seller_sla_breach'] = np.where(
        carrier.notna() & shipping_limit.notna(),
        carrier > shipping_limit,
        False
    )

    fact_order_items = pd.DataFrame({
        'order_id': items['order_id'],
        'order_item_id': items['order_item_id'].astype(int),
        'customer_unique_id': items['customer_unique_id'],
        'product_id': items['product_id'],
        'seller_id': items['seller_id'],
        'order_date_key': items['order_date_key'],
        'purchase_timestamp': items['order_purchase_timestamp'],
        'approved_timestamp': items['order_approved_at'],
        'shipping_limit_timestamp': items['shipping_limit_date'],
        'delivered_carrier_timestamp': items['order_delivered_carrier_date'],
        'delivered_customer_timestamp': items['order_delivered_customer_date'],
        'estimated_delivery_timestamp': items['order_estimated_delivery_date'],
        'item_price_brl': items['item_price_brl'],
        'freight_value_brl': items['freight_value_brl'],
        'total_item_cost_brl': items['total_item_cost_brl'],
        'freight_ratio_pct': items['freight_ratio_pct'],
        'dispatch_lead_time_hours': items['dispatch_lead_time_hours'],
        'carrier_transit_days': items['carrier_transit_days'],
        'total_delivery_days': items['total_delivery_days'],
        'estimated_delivery_days': items['estimated_delivery_days'],
        'delivery_delay_days': items['delivery_delay_days'],
        'is_delayed': items['is_delayed'],
        'is_seller_sla_breach': items['is_seller_sla_breach'],
        'haversine_distance_km': items['haversine_distance_km'],
        'is_interstate_shipment': items['is_interstate_shipment'],
        'order_status': items['order_status'],
        'created_at': datetime.utcnow()
    })

    return fact_order_items
