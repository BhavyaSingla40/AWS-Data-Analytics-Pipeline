from datetime import date
from decimal import Decimal


def validate_sale(row):
    required = (
        "order_id", "order_date", "product",
        "category", "quantity", "unit_price", "region",
    )

    if any(not (row.get(field) or "").strip() for field in required):
        raise ValueError("A required field is missing")

    order_date_text = row["order_date"].strip()
    order_date = date.fromisoformat(order_date_text)

    if order_date.isoformat() != order_date_text:
        raise ValueError("Date must use YYYY-MM-DD")

    quantity = int(row["quantity"])
    price = Decimal(row["unit_price"])

    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    if not price.is_finite() or price < 0:
        raise ValueError("Price must be finite and nonnegative")

    if price != price.quantize(Decimal("0.01")):
        raise ValueError("Price cannot have more than two decimals")

    return {
        **{field: row[field].strip() for field in required},
        "quantity": quantity,
        "order_date": order_date.isoformat(),
        "revenue_cents": int(quantity * price * 100),
    }