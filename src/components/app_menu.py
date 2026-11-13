import flet as ft


INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
ACCENT = ft.Colors.INDIGO_700
BORDER = ft.Colors.BLUE_GREY_100


def build_app_menu(
    width: int,
    on_orders,
    on_management,
    *,
    mobile: bool = False,
    on_close=None,
) -> ft.Control:
    def menu_button(label: str, icon: str, handler) -> ft.Control:
        def invoke():
            if mobile and on_close is not None:
                on_close()
            handler()

        return ft.Button(
            width=width - 32,
            content=ft.Row(
                spacing=12,
                controls=[ft.Icon(icon, size=18), ft.Text(label, size=13)],
            ),
            on_click=lambda e: invoke(),
        )

    header_controls = [
        ft.Icon(ft.Icons.RECEIPT_LONG, color=ACCENT, size=24),
        ft.Text("PEDIDOS", size=17, weight=ft.FontWeight.BOLD, color=INK, expand=True),
    ]
    if mobile and on_close is not None:
        header_controls.append(
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                tooltip="Fechar menu",
                on_click=lambda e: on_close(),
            )
        )

    return ft.Column(
        expand=True,
        spacing=12,
        controls=[
            ft.Row(spacing=9, controls=header_controls),
            ft.Text("Gestão local de encomendas", size=12, color=MUTED),
            ft.Divider(color=BORDER, thickness=1),
            ft.Text("VISUALIZAÇÃO", size=11, weight=ft.FontWeight.BOLD, color=MUTED),
            menu_button("Painel de pedidos", ft.Icons.DASHBOARD, on_orders),
            menu_button("Gerenciar cadastros", ft.Icons.SETTINGS, on_management),
            ft.Container(expand=True),
            ft.Text("Dados locais desta sessão", size=11, color=MUTED),
        ],
    )
