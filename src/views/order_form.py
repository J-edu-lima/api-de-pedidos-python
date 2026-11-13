"""Modal de criação de pedidos com validação local do contrato do MVP."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable

import flet as ft

from components.modal import show_form_modal
from components.money_field import MoneyField
from components.order_items_field import OrderItemsField


def show_order_form(
    page: ft.Page,
    on_created: Callable[[dict], None],
    clientes: list[dict],
    produtos: list[dict],
):
    clientes_ativos = [cliente for cliente in clientes if cliente["ativo"]]
    produtos_ativos = [produto for produto in produtos if produto["ativo"]]
    clientes_options = [
        ft.DropdownOption(key=str(cliente["id"]), text=f'{cliente["nome"]} · {cliente["numero"]}')
        for cliente in clientes_ativos
    ]
    customer_dropdown = ft.Dropdown(
        label="Cliente",
        options=clientes_options,
        value=str(clientes_ativos[0]["id"]) if clientes_ativos else None,
    )
    delivery_date_field = ft.TextField(
        label="Data de entrega (opcional)",
        hint_text="DD/MM/AAAA",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def format_delivery_date(e):
        raw = e.control.value or ""
        digits = "".join(character for character in raw if character.isdigit())[:8]
        formatted = digits[:2]
        if len(digits) > 2:
            formatted += "/" + digits[2:4]
        if len(digits) > 4:
            formatted += "/" + digits[4:]
        if formatted != raw:
            e.control.value = formatted
            cursor = len(formatted)
            e.control.selection = ft.TextSelection(base_offset=cursor, extent_offset=cursor)
            page.update()

    delivery_date_field.on_change = format_delivery_date
    delivery_checkbox = ft.Checkbox(label="Este pedido precisa de entrega", value=False)
    address_field = ft.TextField(label="Endereço de entrega", multiline=True, min_lines=1, max_lines=2)
    delivery_fee_field = MoneyField("Valor da entrega")
    delivery_fields = ft.Container()
    error_text = ft.Text(size=12, color=ft.Colors.RED_700, visible=False)
    items_field = OrderItemsField(page, produtos_ativos)

    def toggle_delivery(e):
        if delivery_checkbox.value:
            delivery_fields.content = ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 8},
                        content=address_field,
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=delivery_fee_field.control,
                    ),
                ],
            )
        else:
            delivery_fields.content = None
        page.update()

    delivery_checkbox.on_change = toggle_delivery

    def save_order():
        try:
            if not clientes_ativos or not produtos_ativos:
                raise ValueError("É necessário ter ao menos um cliente e um produto ativos.")
            if not customer_dropdown.value:
                raise ValueError("Selecione um cliente.")
            selected_cliente_id = int(customer_dropdown.value)
            selected_cliente = next(
                cliente for cliente in clientes_ativos if cliente["id"] == selected_cliente_id
            )
            items = items_field.values()
            total = Decimal("0.00")
            for item in items:
                product_id = item["produto_id"]
                product = next(produto for produto in produtos_ativos if produto["id"] == product_id)
                unit_value = Decimal(str(product["valor"]))
                total += unit_value * item["quantidade"]
                item["valor_unitario"] = float(unit_value)

            delivery_date = None
            if delivery_date_field.value and delivery_date_field.value.strip():
                try:
                    delivery_date = datetime.strptime(
                        delivery_date_field.value.strip(), "%d/%m/%Y"
                    ).date().isoformat()
                except ValueError as exc:
                    raise ValueError("Informe a data de entrega no formato DD/MM/AAAA.") from exc

            delivery = None
            if delivery_checkbox.value:
                address = address_field.value.strip() if address_field.value else ""
                if not address:
                    raise ValueError("Informe o endereço para pedidos com entrega.")
                try:
                    fee = delivery_fee_field.parse()
                except (InvalidOperation, ValueError) as exc:
                    raise ValueError("O valor da entrega deve ser um número válido.") from exc
                if fee < 0:
                    raise ValueError("O valor da entrega não pode ser negativo.")
                delivery = {"endereco": address, "valor": float(fee)}
                total += fee

            order = {
                "id": 0,
                "cliente_id": selected_cliente["id"],
                "estado": "Pendente",
                "data_entrada": datetime.now().replace(microsecond=0).isoformat(),
                "data_entrega": delivery_date,
                "entrega": delivery,
                "itens": items,
                "valor_total": float(total),
            }
            on_created(order)
            page.pop_dialog()
        except (ValueError, StopIteration) as exc:
            error_text.value = str(exc) or "Confira os dados do pedido."
            error_text.visible = True
            page.update()

    cancel_button = ft.TextButton(content="Cancelar", on_click=lambda e: page.pop_dialog())
    create_button = ft.Button(content="Criar pedido", on_click=lambda e: save_order())

    show_form_modal(
        page,
        title="Adicionar pedido",
        icon=ft.Icons.ADD_SHOPPING_CART,
        description="Preencha os dados do novo pedido.",
        controls=[
            customer_dropdown,
            delivery_date_field,
            items_field.control,
            delivery_checkbox,
            delivery_fields,
            error_text,
        ],
        actions=[cancel_button, create_button],
        max_width=540,
        scrollable=True,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )
