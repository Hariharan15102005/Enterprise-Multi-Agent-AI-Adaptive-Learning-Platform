import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from etl.pipelines.pipeline_runner import ETLPipeline

if __name__ == "__main__":
    pipeline = ETLPipeline()
    report = pipeline.run()
    print("ETL Execution Complete. Report Summary:")
    print(f"Status: {report['status']} | Duration: {report['duration_seconds']}s")
    for tbl, cnt in report['final_table_counts'].items():
        print(f"  {tbl}: {cnt}")
