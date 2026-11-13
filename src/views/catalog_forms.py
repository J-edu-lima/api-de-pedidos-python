"""Modais para cadastrar clientes e produtos nos dados locais da sessão."""

from decimal import Decimal, InvalidOperation
from typing import Callable

import flet as ft

from components.money_field import MoneyField
from components.modal import show_form_modal


def show_customer_form(page: ft.Page, on_created: Callable[[dict], None]):
    name_field = ft.TextField(label="Nome", autofocus=True)
    number_field = ft.TextField(label="Telefone / número", keyboard_type=ft.KeyboardType.PHONE)
    error_text = ft.Text(size=12, color=ft.Colors.RED_700, visible=False)

    def save_customer():
        name = name_field.value.strip() if name_field.value else ""
        number = number_field.value.strip() if number_field.value else ""
        if not name or not number:
            error_text.value = "Nome e número são obrigatórios."
            error_text.visible = True
            page.update()
            return
        on_created({"id": 0, "nome": name, "numero": number, "ativo": True})
        page.pop_dialog()

    cancel_button = ft.TextButton(content="Cancelar", on_click=lambda e: page.pop_dialog())
    save_button = ft.Button(content="Salvar", on_click=lambda e: save_customer())

    show_form_modal(
        page,
        title="Incluir cliente",
        icon=ft.Icons.PERSON_ADD,
        description="O cliente poderá ser selecionado em novos pedidos.",
        controls=[name_field, number_field, error_text],
        actions=[cancel_button, save_button],
        max_width=420,
    )


def show_product_form(page: ft.Page, on_created: Callable[[dict], None]):
    name_field = ft.TextField(label="Nome do produto", autofocus=True)
    description_field = ft.TextField(label="Descrição (opcional)", multiline=True, min_lines=1, max_lines=3)
    value_field = MoneyField("Valor unitário")
    error_text = ft.Text(size=12, color=ft.Colors.RED_700, visible=False)

    def save_product():
        name = name_field.value.strip() if name_field.value else ""
        if not name:
            error_text.value = "O nome do produto é obrigatório."
            error_text.visible = True
            page.update()
            return
        try:
            value = value_field.parse()
            if value < 0:
                raise ValueError("O valor do produto não pode ser negativo.")
        except InvalidOperation:
            error_text.value = "Informe um valor unitário válido."
            error_text.visible = True
            page.update()
            return
        except ValueError as exc:
            error_text.value = str(exc)
            error_text.visible = True
            page.update()
            return

        description = description_field.value.strip() if description_field.value else ""
        on_created(
            {
                "id": 0,
                "nome": name,
                "descricao": description or None,
                "valor": float(value),
                "ativo": True,
            }
        )
        page.pop_dialog()

    cancel_button = ft.TextButton(content="Cancelar", on_click=lambda e: page.pop_dialog())
    save_button = ft.Button(content="Salvar", on_click=lambda e: save_product())

    show_form_modal(
        page,
        title="Incluir produto",
        icon=ft.Icons.ADD_SHOPPING_CART,
        description="O produto ficará disponível nos novos pedidos.",
        controls=[name_field, description_field, value_field.control, error_text],
        actions=[cancel_button, save_button],
        max_width=460,
        scrollable=True,
    )
