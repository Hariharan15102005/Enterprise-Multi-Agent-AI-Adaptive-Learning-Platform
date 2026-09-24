import pandas as pd
import numpy as np

BRAZIL_REGIONS = {
    "SP": "Southeast", "RJ": "Southeast", "MG": "Southeast", "ES": "Southeast",
    "PR": "South", "SC": "South", "RS": "South",
    "BA": "Northeast", "PE": "Northeast", "CE": "Northeast", "MA": "Northeast",
    "PB": "Northeast", "RN": "Northeast", "AL": "Northeast", "PI": "Northeast", "SE": "Northeast",
    "DF": "Central-West", "GO": "Central-West", "MT": "Central-West", "MS": "Central-West",
    "AM": "North", "PA": "North", "RO": "North", "TO": "North", "AC": "North", "AP": "North", "RR": "North"
}

def transform_geolocation(raw_geo_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw geolocation data by:
    1. Filtering geographic outliers outside Brazil boundaries.
    2. Aggregating to 1 row per zip_code_prefix (Mean Lat/Lng, Modal City & State).
    3. Mapping Brazilian Macro-Regions.
    """
    # Boundary box filtering for Brazil
    valid_coords = raw_geo_df[
        (raw_geo_df['geolocation_lat'] >= -33.75) & (raw_geo_df['geolocation_lat'] <= 5.27) &
        (raw_geo_df['geolocation_lng'] >= -73.98) & (raw_geo_df['geolocation_lng'] <= -34.79)
    ].copy()

    # If all points for a zip were filtered, fallback to raw
    if len(valid_coords) < len(raw_geo_df) * 0.5:
        valid_coords = raw_geo_df.copy()

    # Aggregate coords
    geo_agg = valid_coords.groupby('geolocation_zip_code_prefix').agg(
        latitude=('geolocation_lat', 'mean'),
        longitude=('geolocation_lng', 'mean'),
        sample_points_count=('geolocation_lat', 'count')
    ).reset_index()

    # Modal city and state
    mode_city_state = valid_coords.groupby('geolocation_zip_code_prefix')[['geolocation_city', 'geolocation_state']].agg(
        lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    ).reset_index()

    dim_geo = pd.merge(geo_agg, mode_city_state, on='geolocation_zip_code_prefix')
    
    dim_geo.rename(columns={
        'geolocation_zip_code_prefix': 'zip_code_prefix',
        'geolocation_city': 'city_canonical',
        'geolocation_state': 'state_code'
    }, inplace=True)

    dim_geo['brazil_macro_region'] = dim_geo['state_code'].map(BRAZIL_REGIONS).fillna('Other')
    
    # Ensure rounded coordinates for storage
    dim_geo['latitude'] = dim_geo['latitude'].round(7)
    dim_geo['longitude'] = dim_geo['longitude'].round(7)

    return dim_geo
