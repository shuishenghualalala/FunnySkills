# Table Operations Reference

All commands use `python scripts/table_ops.py <command>`. Common flags: `-o <output_file>`, `-f csv|markdown|json`.

## Quick Profiling

```bash
python scripts/analyze.py data.csv                     # Full profile (text)
python scripts/analyze.py data.csv -f markdown          # Markdown output
python scripts/analyze.py data.xlsx -f json --top 10    # JSON, 10 sample rows
```

## info — Table Metadata

```bash
python scripts/table_ops.py info data.csv
```

Returns JSON: shape, columns (dtype, missing, unique, sample value), memory usage.

## filter — Filter Rows

```bash
python scripts/table_ops.py filter data.csv 'age > 30' -f markdown
python scripts/table_ops.py filter data.csv 'region == "East" and revenue > 10000' -o filtered.csv
python scripts/table_ops.py filter data.csv 'category.str.contains("Tech")' -f markdown
```

Condition uses pandas query syntax. String comparisons need inner quotes.

## select — Select Columns

```bash
python scripts/table_ops.py select data.csv "name,age,salary" -f markdown
python scripts/table_ops.py select data.csv "date,revenue,profit" -o subset.csv
```

## aggregate — Group By + Aggregate

```bash
python scripts/table_ops.py aggregate data.csv --group-by region --agg revenue:sum profit:mean
python scripts/table_ops.py aggregate data.csv --group-by "region,quarter" --agg revenue:sum units:count -f markdown
python scripts/table_ops.py aggregate data.csv --group-by category --agg price:min price:max -o agg.csv
```

Supported functions: sum, mean, count, min, max, std, median, first, last.

## sort — Sort Rows

```bash
python scripts/table_ops.py sort data.csv --by revenue --desc -f markdown
python scripts/table_ops.py sort data.csv --by "region,name" -o sorted.csv
```

## merge — Join Two Tables

```bash
python scripts/table_ops.py merge left.csv right.csv --on id --how inner
python scripts/table_ops.py merge orders.csv customers.csv --left-on customer_id --right-on id --how left -o joined.csv
```

Join types: inner (default), left, right, outer.

## pivot — Pivot Table

```bash
python scripts/table_ops.py pivot data.csv --index region --values revenue --pivot-columns quarter --aggfunc sum -f markdown
python scripts/table_ops.py pivot data.csv --index "category,region" --values units_sold --aggfunc mean
```

## add-column — Computed Column

```bash
python scripts/table_ops.py add-column data.csv --name margin --expression "profit / revenue" -o enriched.csv
python scripts/table_ops.py add-column data.csv --name total --expression "price * quantity"
```

Expression uses pandas eval syntax. Supports arithmetic, comparison, and column references.

## describe — Descriptive Statistics

```bash
python scripts/table_ops.py describe data.csv -f markdown
python scripts/table_ops.py describe data.csv --columns "revenue,profit,units" -f markdown
```

Returns count, mean, std, min, 25%, 50%, 75%, max for numeric columns.

## find — Search Rows

```bash
python scripts/table_ops.py find data.csv --column name --value "Alice"
python scripts/table_ops.py find data.csv --column email --pattern ".*@gmail\\.com" -f markdown
python scripts/table_ops.py find data.csv --column product --pattern "laptop|monitor" -o matches.csv
```

`--value` for exact match, `--pattern` for regex (case-insensitive).

## dedup — Remove Duplicates

```bash
python scripts/table_ops.py dedup data.csv -o clean.csv
python scripts/table_ops.py dedup data.csv --subset "email,phone" -f markdown
```

## rename — Rename Columns

```bash
python scripts/table_ops.py rename data.csv --mapping old_name:new_name col2:better_name -o renamed.csv
```

## sample — Random Sample

```bash
python scripts/table_ops.py sample data.csv -n 20 -f markdown
```

Deterministic (seed=42) for reproducibility.

## value-counts — Frequency Counts

```bash
python scripts/table_ops.py value-counts data.csv --column category -f markdown
python scripts/table_ops.py value-counts data.csv --column region -o counts.csv
```

## correlation — Correlation Matrix

```bash
python scripts/table_ops.py correlation data.csv -f markdown
python scripts/table_ops.py correlation data.csv --columns "revenue,cost,profit" -f markdown
```

Pearson correlation for numeric columns.

## head — First N Rows

```bash
python scripts/table_ops.py head data.csv -n 20 -f markdown
```

## Supported File Formats

| Extension | Format |
|-----------|--------|
| .csv      | Comma-separated values |
| .tsv      | Tab-separated values |
| .xlsx/.xls | Excel |
| .json     | JSON (records or columnar) |
| .parquet  | Apache Parquet |

## When to Use Inline Python Instead

Use inline Python with pandas when:
- Chaining multiple operations in a single pass
- Complex transformations not covered by built-in commands (e.g., string parsing, date operations, window functions)
- Custom visualization or chart generation
- Statistical modeling or ML tasks
- Operations requiring intermediate variables or conditional logic

Example inline pattern:

```python
import pandas as pd
df = pd.read_csv("data.csv")
# Complex multi-step analysis here
result = df.groupby("region").agg({"revenue": "sum"}).sort_values("revenue", ascending=False)
result.to_csv("result.csv", index=False)
print(result.to_markdown(index=False))
```
