"""Tela principal responsiva de pedidos e estado local da sessão."""

import logging

import flet as ft

from components.app_menu import build_app_menu
from components.card import build_card
from components.kanban_column import build_kanban_column
from components.stage_navigator import StageNavigator
from state.order_store import OrderStore
from views.catalog_forms import show_customer_form, show_product_form
from views.management import build_management_view
from views.order_form import show_order_form


log = logging.getLogger(f"app.{__name__}")
INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
ACCENT = ft.Colors.INDIGO_700
BORDER = ft.Colors.BLUE_GREY_100
STAGES = [
    ("Novos", "novos", ft.Colors.INDIGO_700, ft.Icons.INBOX),
    ("Em andamento", "andamento", ft.Colors.AMBER_800, ft.Icons.PENDING_ACTIONS),
    ("Finalizados", "finalizados", ft.Colors.GREEN_700, ft.Icons.TASK_ALT),
]
MOBILE_BREAKPOINT = 700


def build_orders_view(page: ft.Page) -> ft.Control:
    store = OrderStore()
    pedidos = store.pedidos
    clientes = store.clientes
    produtos = store.produtos
    etapas = store.etapas
    log.debug("Loaded %d mocked orders", len(pedidos))

    cliente_por_id = store.cliente_por_id
    produto_por_id = store.produto_por_id
    summary_new = ft.Text(size=22, weight=ft.FontWeight.BOLD, color=INK)
    summary_active = ft.Text(size=22, weight=ft.FontWeight.BOLD, color=INK)
    summary_done = ft.Text(size=22, weight=ft.FontWeight.BOLD, color=INK)
    current_view = {"name": "orders"}
    current_stage = {"index": 0}
    search_query = {"value": ""}
    menu_open = {"value": False}
    board = ft.Row(
        expand=True,
        margin=ft.Margin.symmetric(horizontal=14, vertical=4),
        spacing=16,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    desktop_search_field = ft.TextField(
        hint_text="Buscar por nome do cliente",
        prefix_icon=ft.Icons.SEARCH,
        filled=True,
        fill_color=ft.Colors.WHITE,
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=16,
                side=ft.BorderSide(color=BORDER),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=16,
                side=ft.BorderSide(color=ACCENT),
            ),
        },
        on_change=lambda e: filter_orders(e.control.value, e.control),
    )
    mobile_search_field = ft.TextField(
        hint_text="Buscar por nome do cliente",
        prefix_icon=ft.Icons.SEARCH,
        filled=True,
        fill_color=ft.Colors.WHITE,
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=16,
                side=ft.BorderSide(color=BORDER),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=16,
                side=ft.BorderSide(color=ACCENT),
            ),
        },
        on_change=lambda e: filter_orders(e.control.value, e.control),
    )
    mobile_title = ft.Text("Pedidos", size=20, weight=ft.FontWeight.BOLD, color=INK, expand=True)
    main_content = ft.Container(
        expand=True,
        padding=ft.Padding.only(left=4, right=4, top=4, bottom=4),
    )
    responsive_root = ft.Container(expand=True)

    def is_mobile() -> bool:
        return (page.width or 1000) < MOBILE_BREAKPOINT

    def update_summary():
        summary_new.value = str(sum(1 for stage in etapas.values() if stage == "novos"))
        summary_active.value = str(sum(1 for stage in etapas.values() if stage == "andamento"))
        summary_done.value = str(sum(1 for order in pedidos if order["estado"] != "Pendente"))

    def lane_orders(key: str) -> list[dict]:
        return store.lane_orders(key, search_query["value"])

    def update_mobile_navigation():
        index = current_stage["index"]
        counts = {key: len(lane_orders(key)) for _, key, _, _ in STAGES}
        stage_navigator.update(index, counts)

    def select_stage(index: int):
        current_stage["index"] = max(0, min(index, len(STAGES) - 1))
        update_mobile_navigation()
        render_board()
        page.update()

    def filter_orders(value: str | None, source: ft.Control):
        search_query["value"] = value or ""
        if source is not desktop_search_field:
            desktop_search_field.value = search_query["value"]
        if source is not mobile_search_field:
            mobile_search_field.value = search_query["value"]
        render_board()
        page.update()

    stage_navigator = StageNavigator(STAGES, select_stage)

    def move_order(order_id: int, destination: str):
        if not store.move_order(order_id, destination):
            return
        update_summary()
        update_mobile_navigation()
        render_board()
        page.update()

    def cancel_order(order_id: int):
        if not store.cancel_order(order_id):
            return
        update_summary()
        update_mobile_navigation()
        render_board()
        page.update()

    def add_created_order(order: dict):
        store.add_order(order)
        current_stage["index"] = 0
        log.debug("Created local order #%s", order["id"])
        update_summary()
        update_mobile_navigation()
        render_board()
        page.update()

    def add_created_customer(customer: dict):
        store.add_customer(customer)
        log.debug("Added local customer #%s", customer["id"])
        if current_view["name"] == "management":
            open_management_view()
        else:
            page.update()

    def add_created_product(product: dict):
        store.add_product(product)
        log.debug("Added local product #%s", product["id"])
        if current_view["name"] == "management":
            open_management_view()
        else:
            page.update()

    def delete_customer(customer_id: int):
        if not store.delete_customer(customer_id):
            log.warning("Could not delete customer #%s", customer_id)
            return
        log.debug("Deleted local customer #%s", customer_id)
        open_management_view()

    def delete_product(product_id: int):
        if not store.delete_product(product_id):
            log.warning("Could not delete product #%s", product_id)
            return
        log.debug("Deleted local product #%s", product_id)
        open_management_view()

    def open_order_form():
        show_order_form(page, add_created_order, clientes, produtos)

    def open_customer_form():
        show_customer_form(page, add_created_customer)

    def open_product_form():
        show_product_form(page, add_created_product)

    def inclusion_actions():
        return ft.Row(
            spacing=0,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ADD_SHOPPING_CART,
                    tooltip="Incluir pedido",
                    icon_color=ACCENT,
                    on_click=lambda e: open_order_form(),
                ),
                ft.IconButton(
                    icon=ft.Icons.PERSON_ADD,
                    tooltip="Incluir cliente",
                    icon_color=ACCENT,
                    on_click=lambda e: open_customer_form(),
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD_BOX,
                    tooltip="Incluir produto",
                    icon_color=ACCENT,
                    on_click=lambda e: open_product_form(),
                ),
            ],
        )

    def summary_card(label: str, value: ft.Text, icon: str, tint: str):
        return build_card(
            col={"xs": 12, "sm": 4},
            padding=16,
            border_radius=14,
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=40,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        border_radius=12,
                        bgcolor=tint,
                        content=ft.Icon(icon, color=ACCENT, size=20),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[ft.Text(label, size=13, color=MUTED), value],
                    ),
                ],
            ),
        )

    def order_column(title: str, key: str, accent: str, icon: str) -> ft.Control:
        return build_kanban_column(
            title,
            key,
            accent,
            icon,
            lane_orders(key),
            cliente_por_id,
            produto_por_id,
            etapas,
            move_order,
            cancel_order,
            mobile=is_mobile(),
            filtered=bool(search_query["value"].strip()),
        )

    def render_board():
        if is_mobile():
            title, key, accent, icon = STAGES[current_stage["index"]]
            board.controls = [
                ft.GestureDetector(
                    expand=True,
                    on_horizontal_drag_start=stage_navigator.on_swipe_start,
                    on_horizontal_drag_update=stage_navigator.on_swipe_update,
                    on_horizontal_drag_end=stage_navigator.on_swipe_end,
                    content=order_column(title, key, accent, icon),
                )
            ]
        else:
            board.controls = [order_column(*stage) for stage in STAGES]
        update_mobile_navigation()

    def close_mobile_menu():
        menu_open["value"] = False
        mobile_menu_backdrop.visible = False
        mobile_menu_panel.visible = False
        page.update()

    def toggle_mobile_menu():
        menu_open["value"] = not menu_open["value"]
        mobile_menu_backdrop.visible = menu_open["value"]
        mobile_menu_panel.visible = menu_open["value"]
        page.update()

    def summary_view():
        return ft.ResponsiveRow(
            spacing=14,
            run_spacing=14,
            controls=[
                summary_card("Novos", summary_new, ft.Icons.INBOX, ft.Colors.INDIGO_50),
                summary_card("Em andamento", summary_active, ft.Icons.PENDING_ACTIONS, ft.Colors.AMBER_50),
                summary_card("Finalizados", summary_done, ft.Icons.TASK_ALT, ft.Colors.GREEN_50),
            ],
        )

    update_summary()
    render_board()
    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True,
        controls=[
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Pedidos", size=30, weight=ft.FontWeight.BOLD, color=INK),
                    ft.Text("Acompanhe cada pedido, do recebimento à entrega.", size=14, color=MUTED),
                ],
            ),
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                        border_radius=12,
                        bgcolor=ft.Colors.INDIGO_50,
                        content=ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.DASHBOARD, color=ACCENT, size=18),
                                ft.Text("QUADRO DE PEDIDOS", size=11, color=ACCENT, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                    ),
                    inclusion_actions(),
                ],
            ),
        ],
    )
    desktop_orders_panel = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=18,
        controls=[header, summary_view(), desktop_search_field, board],
    )
    mobile_header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER),
        border_radius=14,
        content=ft.Row(
            spacing=8,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    tooltip="Abrir menu",
                    on_click=lambda e: toggle_mobile_menu(),
                ),
                mobile_title,
                inclusion_actions(),
            ],
        ),
    )
    mobile_orders_panel = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=10,
        controls=[mobile_search_field, stage_navigator.control, board],
    )
    orders_panel = desktop_orders_panel
    main_content.content = orders_panel

    def open_orders_view():
        current_view["name"] = "orders"
        mobile_title.value = "Pedidos"
        orders_panel = mobile_orders_panel if is_mobile() else desktop_orders_panel
        main_content.content = orders_panel
        render_board()
        page.update()

    def open_management_view():
        current_view["name"] = "management"
        mobile_title.value = "Cadastros"
        main_content.content = build_management_view(
            page,
            clientes,
            produtos,
            pedidos,
            delete_customer,
            delete_product,
        )
        page.update()

    desktop_sidebar = ft.Container(
        width=224,
        padding=16,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER),
        border_radius=16,
        content=build_app_menu(224, open_orders_view, open_management_view),
    )
    mobile_menu_backdrop = ft.Container(
        left=0,
        top=0,
        right=0,
        bottom=0,
        bgcolor=ft.Colors.with_opacity(0.42, ft.Colors.BLACK),
        visible=False,
        on_click=lambda e: close_mobile_menu(),
    )
    mobile_menu_panel = ft.Container(
        left=0,
        top=0,
        bottom=0,
        width=280,
        padding=16,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER),
        border_radius=ft.BorderRadius.only(top_right=16, bottom_right=16),
        visible=False,
        content=build_app_menu(
            280,
            open_orders_view,
            open_management_view,
            mobile=True,
            on_close=close_mobile_menu,
        ),
    )
    mobile_layout = ft.SafeArea(
        expand=True,
        content=ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=12,
                    controls=[mobile_header, main_content],
                ),
                mobile_menu_backdrop,
                mobile_menu_panel,
            ],
        ),
    )
    desktop_layout = ft.Row(
        expand=True,
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[desktop_sidebar, main_content],
    )

    def apply_layout():
        mobile = is_mobile()
        page.padding = 8 if mobile else 16
        main_content.padding = ft.Padding.all(0) if mobile else ft.Padding.all(4)
        if current_view["name"] == "orders":
            mobile_title.value = "Pedidos"
            main_content.content = mobile_orders_panel if mobile else desktop_orders_panel
            render_board()
        else:
            mobile_title.value = "Cadastros"
            main_content.content = build_management_view(
                page,
                clientes,
                produtos,
                pedidos,
                delete_customer,
                delete_product,
            )
        responsive_root.content = mobile_layout if mobile else desktop_layout

    def handle_resize(e):
        apply_layout()
        page.update()

    page.on_resize = handle_resize
    apply_layout()
    return responsive_root
