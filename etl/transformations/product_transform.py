import pandas as pd
import numpy as np
from datetime import datetime

CUSTOM_TRANSLATIONS = {
    "pc_gamer": "gaming_pc",
    "portateis_cozinha_e_preparadores_de_alimentos": "small_kitchen_appliances"
}

def transform_products(raw_products_df: pd.DataFrame, translation_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms products dataset:
    1. Standardizes Portuguese to English category mappings including custom missing translations.
    2. Imputes missing physical dimensions safely.
    3. Calculates volume (cm3), density (g/cm3), and size tiers.
    """
    df = raw_products_df.copy()
    trans = translation_df.copy()

    # Build unified translation dict
    trans_map = dict(zip(trans['product_category_name'], trans['product_category_name_english']))
    trans_map.update(CUSTOM_TRANSLATIONS)

    # Map categories
    df['category_name_pt'] = df['product_category_name'].fillna('nao_informado')
    df['category_name_en'] = df['category_name_pt'].map(trans_map).fillna('uncategorized')

    # Physical measurements cleaning
    df['weight_g'] = df['product_weight_g'].fillna(0.0).clip(lower=0.0)
    df['length_cm'] = df['product_length_cm'].fillna(0.0).clip(lower=0.0)
    df['height_cm'] = df['product_height_cm'].fillna(0.0).clip(lower=0.0)
    df['width_cm'] = df['product_width_cm'].fillna(0.0).clip(lower=0.0)
    
    # Volume calculation
    df['volume_cm3'] = (df['length_cm'] * df['height_cm'] * df['width_cm']).round(2)
    df['density_g_cm3'] = np.where(df['volume_cm3'] > 0, (df['weight_g'] / df['volume_cm3']).round(4), 0.0)

    # Size tier heuristic
    conditions = [
        (df['weight_g'] >= 10000) | (df['volume_cm3'] >= 50000),
        (df['weight_g'] >= 3000) | (df['volume_cm3'] >= 20000),
        (df['weight_g'] < 500) & (df['volume_cm3'] < 3000),
    ]
    choices = ['Heavy/Bulky', 'Bulky', 'Small']
    df['size_tier'] = np.select(conditions, choices, default='Standard')

    dim_product = pd.DataFrame({
        'product_id': df['product_id'],
        'category_name_pt': df['category_name_pt'],
        'category_name_en': df['category_name_en'],
        'name_length_chars': df['product_name_lenght'].fillna(0).astype(int),
        'description_length_chars': df['product_description_lenght'].fillna(0).astype(int),
        'photos_qty': df['product_photos_qty'].fillna(0).astype(int),
        'weight_g': df['weight_g'].round(2),
        'length_cm': df['length_cm'].round(2),
        'height_cm': df['height_cm'].round(2),
        'width_cm': df['width_cm'].round(2),
        'volume_cm3': df['volume_cm3'],
        'density_g_cm3': df['density_g_cm3'],
        'size_tier': df['size_tier'],
        'created_at': datetime.utcnow()
    })

    return dim_product
