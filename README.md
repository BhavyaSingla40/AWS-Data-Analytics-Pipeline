# AWS Data Analytics Pipeline

A sales analytics project built with Python and SQLite, with an AWS pipeline planned as the next stage.

## Current features

- Read sales records from CSV.
- Validate required fields, dates, quantities, and prices.
- Reject duplicate order IDs.
- Store valid records in SQLite.
- Export rejected rows and monthly sales reports.
- Run automated validation tests through GitHub Actions.

## Architecture

Current local pipeline:

```text
Sales CSV → Python validation → SQLite → Monthly CSV report
                   ↓
             Rejected rows CSV
```

Planned AWS pipeline:

```text
Amazon S3 → AWS Glue → S3 Parquet → Amazon Athena
```

## Requirements

- Python 3.11 or newer
- Git
- VS Code recommended

The local pipeline uses only Python's standard library.
No AWS account is required to run it.

## Run on Windows

Clone the repository and create a virtual environment:

```powershell
git clone https://github.com/BhavyaSingla40/AWS-Data-Analytics-Pipeline.git
cd AWS-Data-Analytics-Pipeline
py -m venv .venv
```

Run the pipeline:

```powershell
.\.venv\Scripts\python.exe main.py
```

Run the tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Input data

Save synthetic sample data in `data/sales.csv` using these columns:

```csv
order_id,order_date,product,category,quantity,unit_price,region
ORD-001,2026-01-03,Keyboard,Electronics,2,49.99,North
```

Each row represents one order containing one product.
Use a single currency throughout the dataset.

Validation rules:

- All fields are required.
- Dates must use `YYYY-MM-DD`.
- Quantities must be positive integers.
- Prices must be finite, nonnegative, and have at most two decimal places.
- Later occurrences of an accepted order ID are rejected.

## Generated outputs

| File | Purpose |
|------|---------|
| `data/sales.db` | Validated sales stored in SQLite |
| `output/monthly_sales.csv` | Monthly revenue by region |
| `output/rejected_rows.csv` | Invalid rows and rejection reasons |

Each run replaces the stored dataset and reports.
Money is stored as integer cents to avoid floating-point rounding errors.

Generated outputs are excluded from Git.

## Project structure

```text
AWS-Data-Analytics-Pipeline/
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   └── sales.csv
├── tests/
│   └── test_validation.py
├── .gitignore
├── main.py
├── validation.py
└── README.md
```

## Automated checks

GitHub Actions runs validation tests and executes the pipeline
on every push and pull request.

## Next steps

- Upload sample sales data to Amazon S3.
- Transform sales data with AWS Glue.
- Query curated data using Amazon Athena.
- Document AWS permissions, costs, and cleanup.