import flet as ft


INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
ACCENT = ft.Colors.INDIGO_700


def show_form_modal(
    page: ft.Page,
    *,
    title: str,
    icon: str,
    description: str,
    controls: list[ft.Control],
    actions: list[ft.Control],
    max_width: float,
    scrollable: bool = False,
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER,
) -> None:
    dialog_width = min(max_width, max(280, (page.width or 600) - 80))
    for action in actions:
        action.width = min(140, max(120, (dialog_width - 8) / 2))

    action_row = ft.Row(
        width=dialog_width,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        run_spacing=8,
        wrap=True,
        controls=actions,
    )

    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            scrollable=scrollable,
            title=ft.Row(
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, color=ACCENT),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=INK),
                ],
            ),
            content=ft.Container(
                width=dialog_width,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    horizontal_alignment=horizontal_alignment,
                    controls=[
                        ft.Text(
                            description,
                            size=13,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        *controls,
                        action_row,
                    ],
                ),
            ),
        )
    )
