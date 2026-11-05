import csv
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = ROOT / "data" / "sales.csv"
DATABASE = ROOT / "data" / "sales.db"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

rejected_rows = []

accepted = 0
rejected = 0
seen_ids = set()

with sqlite3.connect(DATABASE) as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            order_id TEXT PRIMARY KEY,
            order_date TEXT NOT NULL,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            revenue_cents INTEGER NOT NULL,
            region TEXT NOT NULL
        )
    """)

    # Replace the dataset so rerunning does not double-count sales.
    connection.execute("DELETE FROM sales")

    with SOURCE.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            try:
                required = (
                    "order_id", "order_date", "product",
                    "category", "quantity", "unit_price", "region"
                )

                if any(not row.get(field, "").strip() for field in required):
                    raise ValueError("A required field is missing")

                order_id = row["order_id"].strip()

                if order_id in seen_ids:
                    raise ValueError("Duplicate order ID")

                order_date = date.fromisoformat(row["order_date"].strip())
                quantity = int(row["quantity"])
                price = Decimal(row["unit_price"])

                if quantity <= 0:
                    raise ValueError("Quantity must be positive")

                if not price.is_finite() or price < 0:
                    raise ValueError("Price must be finite and nonnegative")

                if price != price.quantize(Decimal("0.01")):
                    raise ValueError("Price cannot have more than two decimals")

                revenue_cents = int(quantity * price * 100)

                connection.execute(
                    "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        order_id,
                        order_date.isoformat(),
                        row["product"].strip(),
                        row["category"].strip(),
                        quantity,
                        revenue_cents,
                        row["region"].strip(),
                    ),
                )

                seen_ids.add(order_id)
                accepted += 1

            except (ValueError, InvalidOperation) as error:
                rejected += 1
                print(f"Rejected line {line_number}: {error}")

                rejected_rows.append({
                    "line_number": line_number,
                    "reason": str(error),
                    "original_row": str(row),
                })
    results = connection.execute("""
        SELECT region, SUM(revenue_cents)
        FROM sales
        GROUP BY region
        ORDER BY region
    """).fetchall()

    monthly_results = connection.execute("""
        SELECT
            substr(order_date, 1, 7) AS month,
            region,
            COUNT(*) AS orders,
            SUM(quantity) AS units,
            SUM(revenue_cents) AS revenue_cents
        FROM sales
        GROUP BY month, region
        ORDER BY month, region
    """).fetchall()

print(f"\nAccepted: {accepted} | Rejected: {rejected}")
print("\nRevenue by region:")

for region, cents in results:
    revenue = Decimal(cents) / 100
    print(f"{region}: {revenue:.2f}")

print(f"\nDatabase saved to: {DATABASE}")

rejected_path = OUTPUT / "rejected_rows.csv"

with rejected_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["line_number", "reason", "original_row"],
    )
    writer.writeheader()
    writer.writerows(rejected_rows)

report_path = OUTPUT / "monthly_sales.csv"

with report_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["month", "region", "orders", "units", "revenue"])

    for month, region, orders, units, cents in monthly_results:
        revenue = Decimal(cents) / 100
        writer.writerow([
            month,
            region,
            orders,
            units,
            f"{revenue:.2f}",
        ])

print(f"Rejected rows saved to: {rejected_path}")
print(f"Monthly report saved to: {report_path}")