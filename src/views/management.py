"""Visualização e ativação/desativação de clientes e produtos."""

import logging

import flet as ft

from components.card import build_card
from components.confirmation import show_confirmation_dialog


log = logging.getLogger(f"app.{__name__}")
INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
ACCENT = ft.Colors.INDIGO_700
BORDER = ft.Colors.BLUE_GREY_100


def build_management_view(
    page: ft.Page,
    clientes: list[dict],
    produtos: list[dict],
    pedidos: list[dict],
    on_delete_customer,
    on_delete_product,
):
    active_clients = sum(1 for cliente in clientes if cliente["ativo"])
    active_products = sum(1 for produto in produtos if produto["ativo"])
    client_count = ft.Text(f"{active_clients} ativos de {len(clientes)}", size=12, color=MUTED)
    product_count = ft.Text(f"{active_products} ativos de {len(produtos)}", size=12, color=MUTED)

    def has_pending_client(client_id: int) -> bool:
        return any(
            order["estado"] == "Pendente" and order["cliente_id"] == client_id
            for order in pedidos
        )

    def has_pending_product(product_id: int) -> bool:
        return any(
            order["estado"] == "Pendente"
            and any(item["produto_id"] == product_id for item in order["itens"])
            for order in pedidos
        )

    def client_card(cliente: dict) -> ft.Control:
        blocked = has_pending_client(cliente["id"])
        state_text = ft.Text("Ativo" if cliente["ativo"] else "Inativo", size=12, color=MUTED)

        def change_active(e):
            cliente["ativo"] = bool(e.control.value)
            state_text.value = "Ativo" if cliente["ativo"] else "Inativo"
            refresh_counts()
            log.debug("Customer #%s active=%s", cliente["id"], cliente["ativo"])
            page.update()

        return build_card(
            content=ft.Column(
                spacing=7,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=36,
                                height=36,
                                alignment=ft.Alignment.CENTER,
                                border_radius=18,
                                bgcolor=ft.Colors.INDIGO_50,
                                content=ft.Icon(ft.Icons.PERSON, size=18, color=ACCENT),
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(cliente["nome"], size=14, weight=ft.FontWeight.BOLD, color=INK),
                                    ft.Text(cliente["numero"], size=12, color=MUTED),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        tooltip="Excluir cliente",
                                        icon_color=ft.Colors.RED_700,
                                        disabled=blocked,
                                        on_click=lambda e, customer_id=cliente["id"]: show_confirmation_dialog(
                                            page,
                                            title="Excluir cliente?",
                                            message="Essa ação é irreversível. O cliente será removido das opções de cadastro.",
                                            on_confirm=lambda: on_delete_customer(customer_id),
                                        ),
                                    ),
                                    ft.Column(
                                        spacing=0,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Switch(
                                                value=cliente["ativo"],
                                                disabled=blocked,
                                                on_change=change_active,
                                            ),
                                            state_text,
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            footer=(
                ft.Text(
                    "Relacionado a pedido pendente: não pode ser desativado.",
                    size=11,
                    color=MUTED,
                )
                if blocked
                else None
            ),
        )

    def product_card(produto: dict) -> ft.Control:
        blocked = has_pending_product(produto["id"])
        state_text = ft.Text("Ativo" if produto["ativo"] else "Inativo", size=12, color=MUTED)
        description = produto.get("descricao") or "Sem descrição"

        def change_active(e):
            produto["ativo"] = bool(e.control.value)
            state_text.value = "Ativo" if produto["ativo"] else "Inativo"
            refresh_counts()
            log.debug("Product #%s active=%s", produto["id"], produto["ativo"])
            page.update()

        return build_card(
            content=ft.Column(
                spacing=7,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=36,
                                height=36,
                                alignment=ft.Alignment.CENTER,
                                border_radius=12,
                                bgcolor=ft.Colors.INDIGO_50,
                                content=ft.Icon(ft.Icons.INVENTORY_2, size=18, color=ACCENT),
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(produto["nome"], size=14, weight=ft.FontWeight.BOLD, color=INK),
                                    ft.Text(description, size=12, color=MUTED, max_lines=2),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        tooltip="Excluir produto",
                                        icon_color=ft.Colors.RED_700,
                                        disabled=blocked,
                                        on_click=lambda e, product_id=produto["id"]: show_confirmation_dialog(
                                            page,
                                            title="Excluir produto?",
                                            message="Essa ação é irreversível. O produto será removido das opções de cadastro.",
                                            on_confirm=lambda: on_delete_product(product_id),
                                        ),
                                    ),
                                    ft.Column(
                                        spacing=0,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Switch(
                                                value=produto["ativo"],
                                                disabled=blocked,
                                                on_change=change_active,
                                            ),
                                            state_text,
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f'Código #{produto["id"]}', size=11, color=MUTED),
                            ft.Text(f'R$ {produto["valor"]:.2f}'.replace(".", ","), size=14, weight=ft.FontWeight.BOLD, color=INK),
                        ],
                    ),
                ],
            ),
            footer=(
                ft.Text(
                    "Relacionado a pedido pendente: não pode ser desativado.",
                    size=11,
                    color=MUTED,
                )
                if blocked
                else None
            ),
        )

    def refresh_counts():
        client_count.value = f'{sum(1 for cliente in clientes if cliente["ativo"])} ativos de {len(clientes)}'
        product_count.value = f'{sum(1 for produto in produtos if produto["ativo"])} ativos de {len(produtos)}'

    def entity_panel(title: str, subtitle: ft.Text, icon: str, entries: list[ft.Control], empty_text: str):
        cards = entries or [ft.Text(empty_text, size=13, color=MUTED)]
        return ft.Container(
            expand=True,
            padding=14,
            border_radius=16,
            bgcolor=ft.Colors.BLUE_GREY_100,
            content=ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(icon, size=20, color=ACCENT),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=INK),
                                    subtitle,
                                ],
                            ),
                        ],
                    ),
                    ft.ListView(expand=True, spacing=10, controls=cards),
                ],
            ),
        )

    customer_panel = entity_panel(
        "Clientes",
        client_count,
        ft.Icons.PEOPLE,
        [client_card(cliente) for cliente in clientes],
        "Nenhum cliente cadastrado.",
    )
    product_panel = entity_panel(
        "Produtos",
        product_count,
        ft.Icons.INVENTORY_2,
        [product_card(produto) for produto in produtos],
        "Nenhum produto cadastrado.",
    )
    mobile = (page.width or 1000) < 700
    if mobile:
        selected = {"index": 0}
        content_slot = ft.Container(expand=True, content=customer_panel)
        category_buttons = [
            ft.Button(
                expand=True,
                content="Clientes",
                bgcolor=ACCENT,
                color=ft.Colors.WHITE,
                on_click=lambda e: choose_category(0),
            ),
            ft.Button(
                expand=True,
                content="Produtos",
                bgcolor=ft.Colors.WHITE,
                color=INK,
                on_click=lambda e: choose_category(1),
            ),
        ]
        selectors = ft.Row(spacing=8, controls=category_buttons)

        def choose_category(index: int):
            selected["index"] = index
            content_slot.content = customer_panel if index == 0 else product_panel
            for button_index, button in enumerate(category_buttons):
                is_selected = button_index == index
                button.bgcolor = ACCENT if is_selected else ft.Colors.WHITE
                button.color = ft.Colors.WHITE if is_selected else INK
            page.update()

        return ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Gerenciar cadastros", size=21, weight=ft.FontWeight.BOLD, color=INK),
                        ft.Text("Ative, desative e consulte clientes e produtos.", size=12, color=MUTED),
                    ],
                ),
                selectors,
                content_slot,
            ],
        )

    return ft.Column(
        expand=True,
        spacing=18,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Gerenciar cadastros", size=28, weight=ft.FontWeight.BOLD, color=INK),
                            ft.Text("Consulte os clientes e produtos e controle sua disponibilidade.", size=14, color=MUTED),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        border_radius=12,
                        bgcolor=ft.Colors.INDIGO_50,
                        content=ft.Row(
                            spacing=7,
                            controls=[
                                ft.Icon(ft.Icons.SETTINGS, size=17, color=ACCENT),
                                ft.Text("GESTÃO DE CADASTROS", size=10, color=ACCENT, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                    ),
                ],
            ),
            ft.Row(
                expand=True,
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[customer_panel, product_panel],
            ),
        ],
    )
