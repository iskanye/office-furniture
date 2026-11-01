"""Procedural processing of an office-furniture wholesale request."""

import json
import sys
from decimal import Decimal


def validate_request(request, customers, products):
    if request.get("customer_id") not in customers:
        return "Неизвестный покупатель"
    if not request.get("lines"):
        return "В заявке нет позиций"
    for line in request["lines"]:
        if line.get("product_id") not in products:
            return f"Неизвестный артикул: {line.get('product_id')}"
        quantity = line.get("quantity")
        if type(quantity) is not int or quantity <= 0:
            return "Количество должно быть положительным целым числом"
    return None


def merge_lines(lines):
    quantities = {}
    for line in lines:
        product_id = line["product_id"]
        quantities[product_id] = quantities.get(product_id, 0) + line["quantity"]
    return [{"product_id": key, "quantity": value} for key, value in quantities.items()]


def check_availability(lines, stocks, reservations):
    """Scan every active reservation for every requested product: O(n*m)."""
    shortages = []
    for line in lines:
        product_id = line["product_id"]
        reserved = 0
        for reservation in reservations:
            if reservation["product_id"] == product_id and reservation["active"]:
                reserved += reservation["quantity"]
        available = stocks.get(product_id, 0) - reserved
        if line["quantity"] > available:
            shortages.append({"product_id": product_id, "missing": line["quantity"] - available})
    return shortages


def calculate_total(lines, products):
    """Calculate agreed prices, preserving kopecks: O(n)."""
    total = Decimal("0.00")
    for line in lines:
        price = Decimal(products[line["product_id"]]["price"])
        total += price * line["quantity"]
    return total.quantize(Decimal("0.01"))


def reserve_request(request, lines, products, stocks, reservations):
    if any(item["request_id"] == request["id"] and item["active"] for item in reservations):
        return {"status": "rejected", "reason": "Заявка уже зарезервирована"}
    shortages = check_availability(lines, stocks, reservations)
    if shortages:
        return {"status": "rejected", "reason": "Недостаточно товара", "shortages": shortages}
    total = calculate_total(lines, products)
    for line in lines:
        reservations.append({"id": f"{request['id']}:{line['product_id']}",
                             "request_id": request["id"], "product_id": line["product_id"],
                             "quantity": line["quantity"], "active": True})
    return {"status": "reserved", "request_id": request["id"], "total": str(total)}


def process_request(data):
    customers = {item["id"]: item for item in data["customers"]}
    products = {item["id"]: item for item in data["products"]}
    stocks = {item["product_id"]: item["quantity"] for item in data["stocks"]}
    request = data["request"]
    error = validate_request(request, customers, products)
    if error:
        return {"status": "rejected", "reason": error}
    lines = merge_lines(request["lines"])
    shortages = check_availability(lines, stocks, data["reservations"])
    if shortages:
        return {"status": "rejected", "reason": "Недостаточно товара", "shortages": shortages}
    total = calculate_total(lines, products)
    if not request.get("confirmed"):
        return {"status": "awaiting_confirmation", "total": str(total)}
    if request.get("agreed_total") != str(total):
        return {"status": "rejected", "reason": "Согласованная цена изменилась", "total": str(total)}
    return reserve_request(request, lines, products, stocks, data["reservations"])


def main(argv):
    if len(argv) != 2:
        print("Использование: python3 main.py example.json", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as stream:
        data = json.load(stream)
    print(json.dumps(process_request(data), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
