import pytest
import pandas as pd
from etl.transformations.geolocation_transform import transform_geolocation
from etl.transformations.product_transform import transform_products
from etl.transformations.date_transform import generate_date_dimension

def test_geolocation_aggregation_no_multiplication():
    # Synthetic multi-point geolocation data for 1 zip prefix
    raw_geo = pd.DataFrame({
        'geolocation_zip_code_prefix': [1001, 1001, 1001],
        'geolocation_lat': [-23.54, -23.55, -23.56],
        'geolocation_lng': [-46.63, -46.64, -46.65],
        'geolocation_city': ['sao paulo', 'sao paulo', 'sao paulo'],
        'geolocation_state': ['SP', 'SP', 'SP']
    })
    dim_geo = transform_geolocation(raw_geo)
    assert len(dim_geo) == 1
    assert dim_geo.iloc[0]['zip_code_prefix'] == 1001
    assert dim_geo.iloc[0]['brazil_macro_region'] == 'Southeast'

def test_product_category_custom_mappings():
    raw_prod = pd.DataFrame({
        'product_id': ['p1', 'p2', 'p3'],
        'product_category_name': ['pc_gamer', 'portateis_cozinha_e_preparadores_de_alimentos', None],
        'product_name_lenght': [10, 20, None],
        'product_description_lenght': [100, 200, None],
        'product_photos_qty': [1, 2, None],
        'product_weight_g': [1500, 500, None],
        'product_length_cm': [30, 20, None],
        'product_height_cm': [10, 15, None],
        'product_width_cm': [20, 10, None]
    })
    trans_df = pd.DataFrame({
        'product_category_name': [],
        'product_category_name_english': []
    })
    dim_prod = transform_products(raw_prod, trans_df)
    assert len(dim_prod) == 3
    assert dim_prod.loc[dim_prod['product_id'] == 'p1', 'category_name_en'].iloc[0] == 'gaming_pc'
    assert dim_prod.loc[dim_prod['product_id'] == 'p2', 'category_name_en'].iloc[0] == 'small_kitchen_appliances'
    assert dim_prod.loc[dim_prod['product_id'] == 'p3', 'category_name_en'].iloc[0] == 'uncategorized'

def test_date_dimension_generation():
    dim_date = generate_date_dimension("2017-01-01", "2017-01-10")
    assert len(dim_date) == 10
    assert 'date_key' in dim_date.columns
    assert 'is_holiday_br' in dim_date.columns
    assert dim_date.iloc[0]['is_holiday_br'] == True # New Year's Day
