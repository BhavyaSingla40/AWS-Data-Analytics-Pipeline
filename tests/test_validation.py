import unittest
from decimal import InvalidOperation

from validation import validate_sale


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.sale = {
            "order_id": "ORD-001",
            "order_date": "2026-01-03",
            "product": "Keyboard",
            "category": "Electronics",
            "quantity": "2",
            "unit_price": "49.99",
            "region": "North",
        }

    def test_valid_sale(self):
        result = validate_sale(self.sale)

        self.assertEqual(result["quantity"], 2)
        self.assertEqual(result["revenue_cents"], 9998)

    def test_invalid_quantity(self):
        for quantity in ("0", "-1", "1.5"):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    validate_sale({**self.sale, "quantity": quantity})

    def test_invalid_price(self):
        for price in ("-1", "NaN", "Infinity", "1.001", "abc"):
            with self.subTest(price=price):
                with self.assertRaises((ValueError, InvalidOperation)):
                    validate_sale({**self.sale, "unit_price": price})

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            validate_sale({**self.sale, "order_date": "2026-02-30"})

    def test_missing_field(self):
        with self.assertRaises(ValueError):
            validate_sale({**self.sale, "region": ""})


if __name__ == "__main__":
    unittest.main()