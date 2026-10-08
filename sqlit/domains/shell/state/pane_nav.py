"""Pane navigation state definitions."""

from __future__ import annotations

from sqlit.core.input_context import InputContext
from sqlit.core.state_base import State, hint_key


class PaneNavState(State):
    """A pane is selected but not entered: hjkl move between panes."""

    help_category = "Navigation"
    keymap_context = "pane_nav"

    def _setup_actions(self) -> None:
        self.allows("pane_left", key="h/j/k/l", label="Panes", help="Pane to the left", help_key="h")
        self.allows("pane_down", help="Pane below")
        self.allows("pane_up", help="Pane above")
        self.allows("pane_right", help="Pane to the right")
        self.allows("enter_pane", label="Enter pane", help="Enter the selected pane")

    def get_hint(self, app: InputContext) -> str | None:
        keys = "/".join(
            hint_key(action, fallback)
            for action, fallback in (("pane_left", "h"), ("pane_down", "j"), ("pane_up", "k"), ("pane_right", "l"))
        )
        return f"{keys} switch panes. {hint_key('enter_pane', '<enter>')} goes into the selected pane."

    def is_active(self, app: InputContext) -> bool:
        return app.pane_nav
