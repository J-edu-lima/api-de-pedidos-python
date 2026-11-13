"""Visualização de um pedido no quadro Kanban."""

from datetime import datetime
from typing import Callable

import flet as ft


INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
ACCENT = ft.Colors.INDIGO_700
BORDER = ft.Colors.BLUE_GREY_100


def money(value: float) -> str:
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def build_order_card(
    pedido: dict,
    clientes: dict,
    produtos: dict,
    etapas: dict,
    move_order: Callable[[int, str], None],
    cancel_order: Callable[[int], None],
) -> ft.Control:
    cliente = clientes.get(pedido["cliente_id"], {"nome": "Cliente", "numero": ""})
    entrada = datetime.fromisoformat(pedido["data_entrada"]).strftime("%H:%M")
    product_lines = []
    for item in pedido["itens"]:
        produto = produtos.get(item["produto_id"], {"nome": "Produto"})
        product_lines.append(
            ft.Row(
                spacing=8,
                controls=[
                    ft.Text(f'{item["quantidade"]}×', size=13, weight=ft.FontWeight.BOLD, color=ACCENT),
                    ft.Text(produto["nome"], size=13, color=INK, expand=True),
                ],
            )
        )

    delivery = pedido["entrega"]
    delivery_line = (
        ft.Row(
            spacing=7,
            controls=[
                ft.Icon(ft.Icons.LOCAL_SHIPPING, size=15, color=MUTED),
                ft.Text(delivery["endereco"], size=12, color=MUTED, expand=True),
                ft.IconButton(
                    icon=ft.Icons.CONTENT_COPY,
                    icon_size=16,
                    tooltip="Copiar endereço",
                    action=ft.CopyToClipboard(delivery["endereco"]),
                ),
            ],
        )
        if delivery
        else ft.Row(
            spacing=7,
            controls=[
                ft.Icon(ft.Icons.STORE, size=15, color=MUTED),
                ft.Text("Retirada no local", size=12, color=MUTED),
            ],
        )
    )
    delivery_date = pedido["data_entrega"]
    date_label = (
        f"Entrega: {datetime.fromisoformat(delivery_date).strftime('%d/%m/%Y')}"
        if delivery_date
        else f"Recebido às {entrada}"
    )
    date_line = ft.Row(
        spacing=7,
        controls=[
            ft.Icon(ft.Icons.EVENT, size=15, color=MUTED),
            ft.Text(date_label, size=12, color=MUTED),
        ],
    )
    is_pending = pedido["estado"] == "Pendente"
    actions: list[ft.Control] = []
    if is_pending and etapas.get(pedido["id"]) == "novos":
        actions.append(
            ft.Button(
                content="Iniciar preparo",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=lambda e, order_id=pedido["id"]: move_order(order_id, "andamento"),
            )
        )
    elif is_pending:
        actions.extend(
            [
                ft.TextButton(
                    content="Voltar",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e, order_id=pedido["id"]: move_order(order_id, "novos"),
                ),
                ft.Button(
                    content="Concluir pedido",
                    icon=ft.Icons.DONE,
                    on_click=lambda e, order_id=pedido["id"]: move_order(order_id, "finalizados"),
                ),
            ]
        )
    if is_pending:
        actions.append(
            ft.TextButton(
                content="Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda e, order_id=pedido["id"]: cancel_order(order_id),
            )
        )

    state_color = ft.Colors.GREEN_700 if pedido["estado"] == "Concluido" else ft.Colors.RED_700
    state_bg = ft.Colors.GREEN_50 if pedido["estado"] == "Concluido" else ft.Colors.RED_50
    state_chip = ft.Container(
        padding=ft.Padding.symmetric(horizontal=9, vertical=5),
        border_radius=20,
        bgcolor=state_bg,
        content=ft.Text(pedido["estado"], size=11, color=state_color, weight=ft.FontWeight.BOLD),
    )

    return ft.Container(
        padding=16,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER),
        border_radius=14,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f'Pedido #{pedido["id"]}', size=14, weight=ft.FontWeight.BOLD, color=INK),
                        state_chip if not is_pending else ft.Text(f"Hoje · {entrada}", size=11, color=MUTED),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=34,
                            height=34,
                            alignment=ft.Alignment.CENTER,
                            border_radius=17,
                            bgcolor=ft.Colors.INDIGO_50,
                            content=ft.Icon(ft.Icons.PERSON, size=18, color=ACCENT),
                        ),
                        ft.Column(
                            spacing=1,
                            expand=True,
                            controls=[
                                ft.Text(cliente["nome"], size=14, weight=ft.FontWeight.BOLD, color=INK),
                                ft.Text(cliente["numero"], size=11, color=MUTED),
                            ],
                        ),
                    ],
                ),
                ft.Column(spacing=7, controls=product_lines),
                ft.Container(height=1, bgcolor=BORDER),
                delivery_line,
                date_line,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Total do pedido", size=12, color=MUTED),
                        ft.Text(money(pedido["valor_total"]), size=16, weight=ft.FontWeight.BOLD, color=INK),
                    ],
                ),
                ft.Row(spacing=4, wrap=True, controls=actions) if actions else ft.Container(),
            ],
        ),
    )
