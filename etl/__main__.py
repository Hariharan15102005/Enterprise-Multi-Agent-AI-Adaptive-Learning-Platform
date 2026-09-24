import sys
from etl.pipelines.pipeline_runner import ETLPipeline

def main():
    pipeline = ETLPipeline()
    report = pipeline.run()
    if report.get("status") == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
