import flet as ft


BORDER = ft.Colors.BLUE_GREY_100


def build_card(
    content: ft.Control,
    *,
    footer: ft.Control | None = None,
    padding: int | ft.Padding = 14,
    border_radius: int = 12,
    bgcolor: str = ft.Colors.WHITE,
    col: dict | None = None,
    expand: bool = False,
) -> ft.Container:
    """Create the shared card shell used by dashboard and catalog cards."""
    controls = [content]
    if footer is not None:
        controls.append(footer)

    return ft.Container(
        col=col,
        expand=expand,
        padding=padding,
        bgcolor=bgcolor,
        border=ft.Border.all(1, BORDER),
        border_radius=border_radius,
        content=ft.Column(spacing=7, controls=controls),
    )
