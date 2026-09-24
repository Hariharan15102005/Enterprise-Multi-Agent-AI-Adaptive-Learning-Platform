import pytest
from etl.ingestion.csv_reader import IngestionManager, EXPECTED_SCHEMAS

def test_ingestion_all_files():
    mgr = IngestionManager()
    datasets = mgr.read_all_datasets()
    assert len(datasets) == len(EXPECTED_SCHEMAS)
    for filename in EXPECTED_SCHEMAS.keys():
        assert filename in datasets
        assert len(datasets[filename]) > 0

def test_ingestion_columns():
    mgr = IngestionManager()
    for filename, expected_cols in EXPECTED_SCHEMAS.items():
        df = mgr.read_csv(filename)
        for col in expected_cols:
            assert col in df.columns, f"Missing {col} in {filename}"
