import pytest
from database.connection import engine
from sqlalchemy import text
from etl.loaders.db_loader import DatabaseLoader

def test_table_row_counts_positive():
    loader = DatabaseLoader(db_engine=engine)
    counts = loader.get_table_counts()
    for tbl, cnt in counts.items():
        assert isinstance(cnt, int)
        assert cnt > 0, f"Table {tbl} is unexpectedly empty!"

def test_view_accessibility():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT COUNT(*) FROM analytics_obt_orders"))
        obt_count = res.scalar()
        assert obt_count == 99441
