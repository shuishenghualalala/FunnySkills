#!/usr/bin/env python3
"""Quick table profiling: shape, dtypes, missing values, statistics, and sample rows.

Usage: python analyze.py <file> [--top N] [--format csv|markdown|json]
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np


def _read_table(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    ext = p.suffix.lower()
    readers = {
        ".csv": pd.read_csv,
        ".tsv": lambda f: pd.read_csv(f, sep="\t"),
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json,
        ".parquet": pd.read_parquet,
    }
    reader = readers.get(ext)
    if not reader:
        print(f"Error: unsupported format: {ext}", file=sys.stderr)
        sys.exit(1)
    return reader(p)


def profile(df: pd.DataFrame, path: str, top_n: int = 5) -> dict:
    """Generate a comprehensive profile of the DataFrame."""
    mem_mb = round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)

    col_profiles = []
    for col in df.columns:
        s = df[col]
        p = {
            "name": col,
            "dtype": str(s.dtype),
            "missing": int(s.isnull().sum()),
            "missing_pct": round(s.isnull().mean() * 100, 1),
            "unique": int(s.nunique()),
        }
        if pd.api.types.is_numeric_dtype(s):
            desc = s.describe()
            p["min"] = float(desc.get("min", 0))
            p["max"] = float(desc.get("max", 0))
            p["mean"] = round(float(desc.get("mean", 0)), 2)
            p["std"] = round(float(desc.get("std", 0)), 2)
            p["median"] = round(float(s.median()), 2)
            zeros = int((s == 0).sum())
            if zeros > 0:
                p["zeros"] = zeros
        elif pd.api.types.is_string_dtype(s) or s.dtype == "object":
            top = s.value_counts().head(top_n)
            p["top_values"] = {str(k): int(v) for k, v in top.items()}
            lengths = s.dropna().astype(str).str.len()
            if not lengths.empty:
                p["avg_length"] = round(float(lengths.mean()), 1)
        col_profiles.append(p)

    # Detect potential issues
    issues = []
    total = len(df)
    for cp in col_profiles:
        if cp["missing_pct"] > 30:
            issues.append(f"Column '{cp['name']}' has {cp['missing_pct']}% missing values")
        if cp["unique"] == 1 and total > 1:
            issues.append(f"Column '{cp['name']}' has only 1 unique value (constant)")
        if cp["unique"] == total and total > 10:
            issues.append(f"Column '{cp['name']}' has all unique values (possible ID column)")

    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        issues.append(f"{dup_count} duplicate rows detected ({round(dup_count/total*100, 1)}%)")

    return {
        "file": path,
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "memory_mb": mem_mb,
        "columns": col_profiles,
        "duplicate_rows": dup_count,
        "issues": issues,
        "sample_rows": json.loads(df.head(top_n).fillna("").to_json(orient="records", force_ascii=False)),
    }


def print_report(result: dict, fmt: str):
    if fmt == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return

    r = result
    print(f"# Table Profile: {r['file']}")
    print(f"  Rows: {r['shape']['rows']:,}  |  Cols: {r['shape']['cols']}  |  Memory: {r['memory_mb']} MB  |  Duplicates: {r['duplicate_rows']}")
    print()

    if r["issues"]:
        print("## Potential Issues")
        for issue in r["issues"]:
            print(f"  - {issue}")
        print()

    print("## Column Details")
    if fmt == "markdown":
        print("| Column | Type | Missing | Unique | Stats |")
        print("|--------|------|---------|--------|-------|")
        for c in r["columns"]:
            stats = ""
            if "mean" in c:
                stats = f"mean={c['mean']}, std={c['std']}, range=[{c['min']}, {c['max']}]"
            elif "top_values" in c:
                top3 = list(c["top_values"].items())[:3]
                stats = ", ".join(f"{k}({v})" for k, v in top3)
            miss = f"{c['missing']} ({c['missing_pct']}%)" if c["missing"] > 0 else "0"
            print(f"| {c['name']} | {c['dtype']} | {miss} | {c['unique']} | {stats} |")
    else:
        for c in r["columns"]:
            miss = f"{c['missing']} ({c['missing_pct']}%)" if c["missing"] > 0 else "0"
            line = f"  {c['name']:30s}  {c['dtype']:10s}  missing={miss:12s}  unique={c['unique']}"
            if "mean" in c:
                line += f"  mean={c['mean']}  std={c['std']}  [{c['min']}, {c['max']}]"
            elif "top_values" in c:
                top3 = list(c["top_values"].items())[:3]
                line += "  top: " + ", ".join(f"{k}({v})" for k, v in top3)
            print(line)

    print()
    print(f"## Sample Rows (first {len(r['sample_rows'])})")
    sample_df = pd.DataFrame(r["sample_rows"])
    if fmt == "markdown":
        print(sample_df.to_markdown(index=False))
    else:
        print(sample_df.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="Quick table profiling")
    parser.add_argument("file", help="Input table file (CSV/Excel/TSV/JSON/Parquet)")
    parser.add_argument("--top", type=int, default=5, help="Number of sample rows / top values (default: 5)")
    parser.add_argument("-f", "--format", choices=["text", "markdown", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    df = _read_table(args.file)
    result = profile(df, args.file, top_n=args.top)
    print_report(result, args.format)


if __name__ == "__main__":
    main()
