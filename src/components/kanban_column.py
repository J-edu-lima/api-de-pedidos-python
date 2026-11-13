from collections.abc import Callable

import flet as ft

from views.order_cards import build_order_card


INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
BORDER = ft.Colors.BLUE_GREY_100


def build_kanban_column(
    title: str,
    stage: str,
    accent: str,
    icon: str,
    orders: list[dict],
    clientes: dict,
    produtos: dict,
    etapas: dict,
    move_order: Callable[[int, str], None],
    cancel_order: Callable[[int], None],
    *,
    mobile: bool = False,
    filtered: bool = False,
) -> ft.Control:
    heading = ft.Row(
        spacing=10,
        controls=[
            ft.Container(
                width=34,
                height=34,
                alignment=ft.Alignment.CENTER,
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                content=ft.Icon(icon, color=accent, size=18),
            ),
            ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=INK, expand=True),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=9, vertical=4),
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                content=ft.Text(str(len(orders)), size=12, color=INK, weight=ft.FontWeight.BOLD),
            ),
        ],
    )
    cards = [
        build_order_card(order, clientes, produtos, etapas, move_order, cancel_order)
        for order in orders
    ]
    if not cards:
        empty_message = (
            "Nenhum pedido corresponde à busca."
            if filtered
            else "Nenhum pedido por aqui"
        )
        cards = [
            ft.Container(
                padding=18,
                border=ft.Border.all(1, BORDER),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                content=ft.Text(empty_message, size=12, color=MUTED),
            )
        ]

    return ft.Container(
        expand=True,
        padding=10 if mobile else 14,
        border_radius=16,
        bgcolor=ft.Colors.BLUE_GREY_100,
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                heading,
                ft.ListView(
                    expand=True,
                    spacing=12,
                    padding=ft.Padding.only(bottom=12, right=4),
                    controls=cards,
                ),
            ],
        ),
    )
