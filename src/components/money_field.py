from decimal import Decimal, InvalidOperation

import flet as ft

from utils.money import parse_amount


class MoneyField:
    def __init__(self, label: str, *, value: str = "0,00"):
        self.control = ft.TextField(
            label=label,
            value=value,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

    @property
    def value(self) -> str:
        return self.control.value or ""

    def parse(self, error_message: str = "Informe um valor válido.") -> Decimal:
        try:
            self.control.error_text = None
            return parse_amount(self.value)
        except (InvalidOperation, ValueError):
            self.control.error_text = error_message
            raise
