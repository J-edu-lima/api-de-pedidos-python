import flet as ft


INK = ft.Colors.BLUE_GREY_900
MUTED = ft.Colors.BLUE_GREY_600
ACCENT = ft.Colors.INDIGO_700
BORDER = ft.Colors.BLUE_GREY_100


class StageNavigator:
    def __init__(self, stages: list[tuple[str, str, str, str]], on_select):
        self._stages = stages
        self._on_select = on_select
        self._selected_index = 0
        self._swipe_distance = 0.0
        self.stage_buttons = ft.Row(spacing=10, controls=[])
        self.stage_counter = ft.Text(size=12, color=MUTED)
        self.control = ft.Column(
            spacing=10,
            controls=[self.stage_buttons, self.stage_counter],
        )

    def update(self, selected_index: int, counts: dict[str, int]) -> None:
        self._selected_index = selected_index
        title, key, _, _ = self._stages[selected_index]
        count = counts.get(key, 0)
        self.stage_counter.value = f"{title} · {count} pedido" + ("s" if count != 1 else "")
        self.stage_buttons.controls = [
            ft.Container(
                expand=True,
                height=68,
                padding=ft.Padding.symmetric(horizontal=4, vertical=8),
                alignment=ft.Alignment.CENTER,
                bgcolor=ACCENT if index == selected_index else ft.Colors.WHITE,
                border=ft.Border.all(1, ACCENT if index == selected_index else BORDER),
                border_radius=14,
                on_click=lambda e, selected=index: self._on_select(selected),
                content=ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            stage_icon,
                            size=18,
                            color=ft.Colors.WHITE if index == selected_index else stage_accent,
                        ),
                        ft.Text(
                            stage_title,
                            size=10,
                            max_lines=1,
                            no_wrap=True,
                            color=ft.Colors.WHITE if index == selected_index else INK,
                        ),
                    ],
                ),
            )
            for index, (stage_title, _, stage_accent, stage_icon) in enumerate(self._stages)
        ]

    def on_swipe_start(self, e) -> None:
        self._swipe_distance = 0.0

    def on_swipe_update(self, e) -> None:
        self._swipe_distance += e.primary_delta or 0

    def on_swipe_end(self, e) -> None:
        velocity = e.primary_velocity or 0
        delta = self._swipe_distance
        self._swipe_distance = 0.0
        if abs(velocity) < 250 and abs(delta) < 50:
            return
        direction = -1 if (velocity if abs(velocity) >= 250 else delta) < 0 else 1
        next_index = self._selected_index + direction
        if 0 <= next_index < len(self._stages):
            self._on_select(next_index)
