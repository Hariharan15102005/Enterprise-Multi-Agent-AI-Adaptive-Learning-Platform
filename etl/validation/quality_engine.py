import os
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
from config.settings import settings

class QualityCheckResult:
    def __init__(self, rule: str, dataset: str, status: str, affected_rows: int, total_rows: int, severity: str, message: str):
        self.rule = rule
        self.dataset = dataset
        self.status = status
        self.affected_rows = affected_rows
        self.total_rows = total_rows
        self.pct_affected = round((affected_rows / total_rows * 100) if total_rows > 0 else 0.0, 3)
        self.severity = severity # 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        self.message = message

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "dataset": self.dataset,
            "status": self.status,
            "affected_rows": self.affected_rows,
            "pct_affected": self.pct_affected,
            "severity": self.severity,
            "message": self.message
        }

class DataQualityEngine:
    def __init__(self, quarantine_dir=settings.QUARANTINE_DATA_PATH):
        self.quarantine_dir = quarantine_dir
        self.results: List[QualityCheckResult] = []
        self.quarantine_records: List[dict] = []

    def log_result(self, result: QualityCheckResult):
        self.results.append(result)

    def quarantine(self, dataset_name: str, records: pd.DataFrame, reason: str, rule: str):
        if len(records) == 0:
            return
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_file = self.quarantine_dir / f"quarantine_{dataset_name}_{timestamp}.csv"
        records.to_csv(out_file, index=False)
        self.quarantine_records.append({
            "dataset": dataset_name,
            "rows_quarantined": len(records),
            "reason": reason,
            "rule": rule,
            "file": str(out_file)
        })

    def validate_primary_key(self, df: pd.DataFrame, key_cols: List[str], dataset_name: str) -> bool:
        dups = df.duplicated(subset=key_cols, keep=False)
        dup_count = int(dups.sum())
        status = "PASSED" if dup_count == 0 else "FAILED"
        severity = "CRITICAL" if dup_count > 0 else "INFO"
        msg = f"PK uniqueness on {key_cols}: {dup_count} duplicate instances found."
        
        self.log_result(QualityCheckResult(
            rule="PRIMARY_KEY_UNIQUENESS",
            dataset=dataset_name,
            status=status,
            affected_rows=dup_count,
            total_rows=len(df),
            severity=severity,
            message=msg
        ))
        return dup_count == 0

    def validate_null_constraints(self, df: pd.DataFrame, not_null_cols: List[str], dataset_name: str):
        for col in not_null_cols:
            if col in df.columns:
                null_count = int(df[col].isna().sum())
                status = "PASSED" if null_count == 0 else "WARNING"
                severity = "ERROR" if null_count > 0 else "INFO"
                self.log_result(QualityCheckResult(
                    rule="NOT_NULL_CONSTRAINT",
                    dataset=dataset_name,
                    status=status,
                    affected_rows=null_count,
                    total_rows=len(df),
                    severity=severity,
                    message=f"Column '{col}' has {null_count} null records ({round(null_count/len(df)*100, 2)}%)."
                ))

    def validate_numeric_ranges(self, df: pd.DataFrame, col: str, min_val: float, max_val: float, dataset_name: str):
        if col in df.columns:
            s = df[col].dropna()
            out_of_bounds = int(((s < min_val) | (s > max_val)).sum())
            status = "PASSED" if out_of_bounds == 0 else "WARNING"
            severity = "WARNING" if out_of_bounds > 0 else "INFO"
            self.log_result(QualityCheckResult(
                rule="NUMERIC_RANGE_VALIDATION",
                dataset=dataset_name,
                status=status,
                affected_rows=out_of_bounds,
                total_rows=len(df),
                severity=severity,
                message=f"Column '{col}' expected between [{min_val}, {max_val}], found {out_of_bounds} values out of range."
            ))

    def validate_foreign_key(self, child_df: pd.DataFrame, child_col: str, parent_df: pd.DataFrame, parent_col: str, child_dataset: str, parent_dataset: str):
        child_keys = set(child_df[child_col].dropna())
        parent_keys = set(parent_df[parent_col].dropna())
        unmatched = child_keys - parent_keys
        unmatched_count = len(unmatched)
        status = "PASSED" if unmatched_count == 0 else "FAILED"
        severity = "ERROR" if unmatched_count > 0 else "INFO"
        self.log_result(QualityCheckResult(
            rule="REFERENTIAL_INTEGRITY",
            dataset=child_dataset,
            status=status,
            affected_rows=unmatched_count,
            total_rows=len(child_df),
            severity=severity,
            message=f"Foreign key {child_dataset}.{child_col} -> {parent_dataset}.{parent_col}: {unmatched_count} orphan keys found."
        ))

    def compute_quality_score(self) -> float:
        if not self.results:
            return 100.0
        critical_count = sum(1 for r in self.results if r.status == "FAILED" and r.severity == "CRITICAL")
        error_count = sum(1 for r in self.results if r.status == "FAILED" and r.severity == "ERROR")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        
        penalty = (critical_count * 20.0) + (error_count * 5.0) + (warning_count * 0.5)
        score = max(0.0, min(100.0, 100.0 - penalty))
        return round(score, 2)

    def get_summary(self) -> dict:
        return {
            "overall_quality_score": self.compute_quality_score(),
            "total_checks_executed": len(self.results),
            "passed_checks": sum(1 for r in self.results if r.status == "PASSED"),
            "failed_checks": sum(1 for r in self.results if r.status == "FAILED"),
            "warning_checks": sum(1 for r in self.results if r.status == "WARNING"),
            "quarantine_batches": len(self.quarantine_records),
            "details": [r.to_dict() for r in self.results]
        }
