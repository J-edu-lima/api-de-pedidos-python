from decimal import Decimal


def parse_amount(value: str) -> Decimal:
    normalized = value.strip().replace("R$", "").replace(" ", "")
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    return Decimal(normalized or "0")
