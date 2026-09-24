import pytest
import pandas as pd
from etl.validation.quality_engine import DataQualityEngine

def test_pk_uniqueness_validation():
    engine = DataQualityEngine()
    df_valid = pd.DataFrame({'id': [1, 2, 3], 'val': ['a', 'b', 'c']})
    assert engine.validate_primary_key(df_valid, ['id'], 'test_valid') == True

    df_invalid = pd.DataFrame({'id': [1, 1, 2], 'val': ['a', 'b', 'c']})
    assert engine.validate_primary_key(df_invalid, ['id'], 'test_invalid') == False

def test_fk_integrity_validation():
    engine = DataQualityEngine()
    parent = pd.DataFrame({'parent_id': [10, 20, 30]})
    child_valid = pd.DataFrame({'parent_id': [10, 20]})
    child_invalid = pd.DataFrame({'parent_id': [10, 99]})

    engine.validate_foreign_key(child_valid, 'parent_id', parent, 'parent_id', 'child_v', 'parent')
    res_valid = [r for r in engine.results if r.dataset == 'child_v'][0]
    assert res_valid.status == "PASSED"

    engine.validate_foreign_key(child_invalid, 'parent_id', parent, 'parent_id', 'child_inv', 'parent')
    res_inv = [r for r in engine.results if r.dataset == 'child_inv'][0]
    assert res_inv.status == "FAILED"

def test_quality_score_calculation():
    engine = DataQualityEngine()
    df = pd.DataFrame({'id': [1, 2, 3]})
    engine.validate_primary_key(df, ['id'], 'test')
    score = engine.compute_quality_score()
    assert score == 100.0
