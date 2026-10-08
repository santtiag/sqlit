"""Results filter state."""

from __future__ import annotations

from sqlit.core.input_context import InputContext
from sqlit.core.state_base import BlockingState, DisplayBinding, hint_key, resolve_display_key


class ResultsFilterActiveState(BlockingState):
    """State when results filter is active."""

    help_category = "Results"
    keymap_context = "results_filter"

    def _setup_actions(self) -> None:
        self.allows("results_filter_close", help="Close filter", help_key="esc")
        self.allows("results_filter_accept", help="Select row", help_key="enter")
        self.allows("quit")

    def get_display_bindings(self, app: InputContext) -> tuple[list[DisplayBinding], list[DisplayBinding]]:
        close_key = resolve_display_key("results_filter_close") or "esc"
        accept_key = resolve_display_key("results_filter_accept") or "enter"
        left: list[DisplayBinding] = [
            DisplayBinding(key=close_key, label="Close", action="results_filter_close"),
            DisplayBinding(key=accept_key, label="Select", action="results_filter_accept"),
        ]
        return left, []

    def get_hint(self, app: InputContext) -> str | None:
        return (
            f"Type to filter. {hint_key('results_filter_accept', '<enter>')} keeps the filter, "
            f"{hint_key('results_filter_close', '<esc>')} clears it."
        )

    def is_active(self, app: InputContext) -> bool:
        return app.focus == "results" and app.results_filter_active
