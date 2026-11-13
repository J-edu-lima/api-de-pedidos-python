import flet as ft


def show_confirmation_dialog(
    page: ft.Page,
    *,
    title: str,
    message: str,
    on_confirm,
) -> None:
    def confirm(e):
        page.pop_dialog()
        on_confirm()

    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    content="Cancelar",
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content="Excluir",
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    on_click=confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    )
