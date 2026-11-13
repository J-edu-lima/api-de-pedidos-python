import flet as ft


class OrderItemsField:
    def __init__(self, page: ft.Page, produtos: list[dict]):
        self._page = page
        self._produtos = produtos
        self._product_options = [
            ft.DropdownOption(key=str(produto["id"]), text=produto["nome"])
            for produto in produtos
        ]
        self._rows: list[dict] = []
        self._items_section = ft.Column(spacing=12)
        self.control = ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[ft.Text("Produtos", size=14, weight=ft.FontWeight.BOLD)],
                ),
                self._items_section,
                ft.TextButton(
                    content="Adicionar outro produto",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.add_item(),
                ),
            ],
        )
        self.add_item()

    def add_item(self) -> None:
        product_dropdown = ft.Dropdown(
            label="Produto",
            options=self._product_options,
            value=str(self._produtos[0]["id"]) if self._produtos else None,
            expand=True,
        )
        quantity_field = ft.TextField(
            label="Qtd.",
            value="1",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=75,
        )
        item: dict = {"product": product_dropdown, "quantity": quantity_field}
        remove_button = ft.IconButton(
            ft.Icons.DELETE_OUTLINE,
            tooltip="Remover item",
            icon_color=ft.Colors.RED_700,
            on_click=lambda e, row=item: self.remove_item(row),
        )
        item["remove"] = remove_button
        item["row"] = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[product_dropdown, quantity_field, remove_button],
        )
        self._rows.append(item)
        self._items_section.controls.append(item["row"])
        self._refresh_remove_buttons()

    def remove_item(self, item: dict) -> None:
        if len(self._rows) <= 1:
            return
        self._rows.remove(item)
        self._items_section.controls.remove(item["row"])
        self._refresh_remove_buttons()
        self._page.update()

    def values(self) -> list[dict]:
        if not self._rows:
            raise ValueError("Adicione pelo menos um produto ao pedido.")

        items = []
        for item in self._rows:
            if not item["product"].value:
                raise ValueError("Selecione um produto para cada item.")
            try:
                quantity = int(item["quantity"].value or "")
            except ValueError as exc:
                raise ValueError("A quantidade deve ser um número inteiro maior que zero.") from exc
            if quantity <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")
            items.append({"produto_id": int(item["product"].value), "quantidade": quantity})
        return items

    def _refresh_remove_buttons(self) -> None:
        for item in self._rows:
            item["remove"].disabled = len(self._rows) == 1
