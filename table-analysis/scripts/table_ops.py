#!/usr/bin/env python3
"""CLI tool wrapping 16 pandas table operations.

Usage: python table_ops.py <command> [options]

Commands: info, filter, select, aggregate, sort, merge, pivot, add-column,
          describe, find, dedup, rename, sample, value-counts, correlation, head
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
    if p.suffix == ".csv":
        return pd.read_csv(p)
    elif p.suffix in (".xlsx", ".xls"):
        return pd.read_excel(p)
    elif p.suffix == ".tsv":
        return pd.read_csv(p, sep="\t")
    elif p.suffix == ".json":
        return pd.read_json(p)
    elif p.suffix == ".parquet":
        return pd.read_parquet(p)
    else:
        print(f"Error: unsupported format: {p.suffix}", file=sys.stderr)
        sys.exit(1)


def _output(df: pd.DataFrame, args):
    fmt = getattr(args, "format", "csv")
    out = getattr(args, "output", None)

    if fmt == "markdown":
        text = df.to_markdown(index=False)
    elif fmt == "json":
        text = df.to_json(orient="records", force_ascii=False, indent=2)
    else:
        text = df.to_csv(index=False)

    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8")
        print(f"Saved {len(df)} rows x {len(df.columns)} cols -> {out}")
    else:
        print(text)


def _add_io_args(parser):
    parser.add_argument("file", help="Input CSV/Excel/TSV/JSON/Parquet file")
    parser.add_argument("-o", "--output", help="Output file path (prints to stdout if omitted)")
    parser.add_argument("-f", "--format", choices=["csv", "markdown", "json"], default="csv",
                        help="Output format (default: csv)")


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_info(args):
    df = _read_table(args.file)
    info = {
        "file": args.file,
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "columns": [],
        "missing_total": int(df.isnull().sum().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
    }
    for col in df.columns:
        info["columns"].append({
            "name": col,
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isnull().sum()),
            "unique": int(df[col].nunique()),
            "sample": str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else None,
        })
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cmd_filter(args):
    df = _read_table(args.file)
    try:
        result = df.query(args.condition)
    except Exception as e:
        print(f"Error in filter condition: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"# Filtered: {len(result)}/{len(df)} rows match '{args.condition}'", file=sys.stderr)
    _output(result, args)


def cmd_select(args):
    df = _read_table(args.file)
    cols = [c.strip() for c in args.columns.split(",")]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        print(f"Error: columns not found: {missing}", file=sys.stderr)
        sys.exit(1)
    _output(df[cols], args)


def cmd_aggregate(args):
    df = _read_table(args.file)
    group_cols = [c.strip() for c in args.group_by.split(",")]
    agg_pairs = {}
    for item in args.agg:
        col, func = item.split(":")
        agg_pairs[col.strip()] = func.strip()
    try:
        result = df.groupby(group_cols).agg(agg_pairs).reset_index()
    except Exception as e:
        print(f"Error in aggregation: {e}", file=sys.stderr)
        sys.exit(1)
    _output(result, args)


def cmd_sort(args):
    df = _read_table(args.file)
    cols = [c.strip() for c in args.by.split(",")]
    ascending = not args.desc
    _output(df.sort_values(by=cols, ascending=ascending), args)


def cmd_merge(args):
    left = _read_table(args.file)
    right = _read_table(args.right)
    kwargs = {"how": args.how}
    if args.on:
        kwargs["on"] = args.on
    elif args.left_on and args.right_on:
        kwargs["left_on"] = args.left_on
        kwargs["right_on"] = args.right_on
    else:
        print("Error: specify --on or both --left-on and --right-on", file=sys.stderr)
        sys.exit(1)
    result = pd.merge(left, right, **kwargs)
    print(f"# Merged: {len(left)} + {len(right)} -> {len(result)} rows", file=sys.stderr)
    _output(result, args)


def cmd_pivot(args):
    df = _read_table(args.file)
    idx = [c.strip() for c in args.index.split(",")]
    vals = [c.strip() for c in args.values.split(",")]
    kwargs = {"index": idx, "values": vals, "aggfunc": args.aggfunc}
    if args.pivot_columns:
        kwargs["columns"] = args.pivot_columns
    try:
        result = pd.pivot_table(df, **kwargs).reset_index()
        result.columns = [str(c) if not isinstance(c, tuple) else "_".join(str(x) for x in c)
                          for c in result.columns]
    except Exception as e:
        print(f"Error in pivot: {e}", file=sys.stderr)
        sys.exit(1)
    _output(result, args)


def cmd_add_column(args):
    df = _read_table(args.file)
    try:
        df[args.name] = df.eval(args.expression)
    except Exception as e:
        print(f"Error in expression: {e}", file=sys.stderr)
        sys.exit(1)
    _output(df, args)


def cmd_describe(args):
    df = _read_table(args.file)
    if args.columns:
        cols = [c.strip() for c in args.columns.split(",")]
        df = df[cols]
    result = df.describe(include="all").reset_index().rename(columns={"index": "stat"})
    _output(result, args)


def cmd_find(args):
    df = _read_table(args.file)
    if args.column not in df.columns:
        print(f"Error: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)
    if args.pattern:
        mask = df[args.column].astype(str).str.contains(args.pattern, case=False, na=False)
    elif args.value is not None:
        try:
            typed_val = type(df[args.column].dropna().iloc[0])(args.value) if not df[args.column].dropna().empty else args.value
        except (ValueError, TypeError):
            typed_val = args.value
        mask = df[args.column] == typed_val
    else:
        print("Error: specify --value or --pattern", file=sys.stderr)
        sys.exit(1)
    result = df[mask]
    print(f"# Found: {len(result)} matching rows", file=sys.stderr)
    _output(result, args)


def cmd_dedup(args):
    df = _read_table(args.file)
    subset = [c.strip() for c in args.subset.split(",")] if args.subset else None
    before = len(df)
    result = df.drop_duplicates(subset=subset)
    print(f"# Dedup: {before} -> {len(result)} rows ({before - len(result)} removed)", file=sys.stderr)
    _output(result, args)


def cmd_rename(args):
    df = _read_table(args.file)
    rename_map = {}
    for item in args.mapping:
        old, new = item.split(":")
        rename_map[old.strip()] = new.strip()
    _output(df.rename(columns=rename_map), args)


def cmd_sample(args):
    df = _read_table(args.file)
    n = min(args.n, len(df))
    _output(df.sample(n=n, random_state=42), args)


def cmd_value_counts(args):
    df = _read_table(args.file)
    if args.column not in df.columns:
        print(f"Error: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)
    vc = df[args.column].value_counts().reset_index()
    vc.columns = [args.column, "count"]
    _output(vc, args)


def cmd_correlation(args):
    df = _read_table(args.file)
    if args.columns:
        cols = [c.strip() for c in args.columns.split(",")]
        df = df[cols]
    numeric = df.select_dtypes(include=[np.number])
    if numeric.empty:
        print("Error: no numeric columns found", file=sys.stderr)
        sys.exit(1)
    corr = numeric.corr().reset_index().rename(columns={"index": "column"})
    _output(corr, args)


def cmd_head(args):
    df = _read_table(args.file)
    _output(df.head(args.n), args)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Table operations CLI", prog="table_ops")
    sub = parser.add_subparsers(dest="command", required=True)

    # info
    p = sub.add_parser("info", help="Table metadata: shape, columns, dtypes, missing, sample")
    p.add_argument("file")
    p.set_defaults(func=cmd_info)

    # filter
    p = sub.add_parser("filter", help="Filter rows with a pandas query expression")
    _add_io_args(p)
    p.add_argument("condition", help="Pandas query string, e.g. 'age > 30 and city == \"NYC\"'")
    p.set_defaults(func=cmd_filter)

    # select
    p = sub.add_parser("select", help="Select a subset of columns")
    _add_io_args(p)
    p.add_argument("columns", help="Comma-separated column names")
    p.set_defaults(func=cmd_select)

    # aggregate
    p = sub.add_parser("aggregate", help="Group by and aggregate")
    _add_io_args(p)
    p.add_argument("--group-by", required=True, help="Comma-separated group columns")
    p.add_argument("--agg", nargs="+", required=True,
                   help="col:func pairs, e.g. sales:sum qty:mean")
    p.set_defaults(func=cmd_aggregate)

    # sort
    p = sub.add_parser("sort", help="Sort by columns")
    _add_io_args(p)
    p.add_argument("--by", required=True, help="Comma-separated sort columns")
    p.add_argument("--desc", action="store_true", help="Sort descending")
    p.set_defaults(func=cmd_sort)

    # merge
    p = sub.add_parser("merge", help="Merge/join two tables")
    _add_io_args(p)
    p.add_argument("right", help="Second table file")
    p.add_argument("--on", help="Common join column")
    p.add_argument("--left-on", help="Left join column")
    p.add_argument("--right-on", help="Right join column")
    p.add_argument("--how", choices=["inner", "left", "right", "outer"], default="inner")
    p.set_defaults(func=cmd_merge)

    # pivot
    p = sub.add_parser("pivot", help="Create a pivot table")
    _add_io_args(p)
    p.add_argument("--index", required=True, help="Comma-separated index columns")
    p.add_argument("--values", required=True, help="Comma-separated value columns")
    p.add_argument("--pivot-columns", help="Pivot column (spreads values)")
    p.add_argument("--aggfunc", default="sum", help="Aggregation function (default: sum)")
    p.set_defaults(func=cmd_pivot)

    # add-column
    p = sub.add_parser("add-column", help="Add a computed column")
    _add_io_args(p)
    p.add_argument("--name", required=True, help="New column name")
    p.add_argument("--expression", required=True, help="Pandas eval expression, e.g. 'price * qty'")
    p.set_defaults(func=cmd_add_column)

    # describe
    p = sub.add_parser("describe", help="Descriptive statistics")
    _add_io_args(p)
    p.add_argument("--columns", help="Comma-separated columns (optional, all by default)")
    p.set_defaults(func=cmd_describe)

    # find
    p = sub.add_parser("find", help="Find rows matching a value or regex")
    _add_io_args(p)
    p.add_argument("--column", required=True)
    p.add_argument("--value", help="Exact value to match")
    p.add_argument("--pattern", help="Regex pattern (case-insensitive)")
    p.set_defaults(func=cmd_find)

    # dedup
    p = sub.add_parser("dedup", help="Remove duplicate rows")
    _add_io_args(p)
    p.add_argument("--subset", help="Comma-separated columns to check for duplicates")
    p.set_defaults(func=cmd_dedup)

    # rename
    p = sub.add_parser("rename", help="Rename columns")
    _add_io_args(p)
    p.add_argument("--mapping", nargs="+", required=True,
                   help="old:new pairs, e.g. col1:new_col1 col2:new_col2")
    p.set_defaults(func=cmd_rename)

    # sample
    p = sub.add_parser("sample", help="Random sample of rows")
    _add_io_args(p)
    p.add_argument("-n", type=int, default=10, help="Number of rows (default: 10)")
    p.set_defaults(func=cmd_sample)

    # value-counts
    p = sub.add_parser("value-counts", help="Count unique values in a column")
    _add_io_args(p)
    p.add_argument("--column", required=True)
    p.set_defaults(func=cmd_value_counts)

    # correlation
    p = sub.add_parser("correlation", help="Pearson correlation matrix")
    _add_io_args(p)
    p.add_argument("--columns", help="Comma-separated numeric columns (optional)")
    p.set_defaults(func=cmd_correlation)

    # head
    p = sub.add_parser("head", help="First N rows")
    _add_io_args(p)
    p.add_argument("-n", type=int, default=10, help="Number of rows (default: 10)")
    p.set_defaults(func=cmd_head)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
