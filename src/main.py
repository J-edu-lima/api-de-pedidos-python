import logging

import flet as ft

from views.orders import build_orders_view


LOG_LEVEL = logging.INFO
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("app").setLevel(LOG_LEVEL)


def main(page: ft.Page):
    page.title = "Painel de Pedidos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 16
    page.add(build_orders_view(page))


ft.run(main)
