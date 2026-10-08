"""Explorer tree focused state."""

from __future__ import annotations

from sqlit.core.input_context import InputContext
from sqlit.core.state_base import State, hint_key


class TreeFocusedState(State):
    """Base state when tree has focus."""

    help_category = "Explorer"
    keymap_context = "tree"

    def _setup_actions(self) -> None:
        self.allows("new_connection", label="New", help="New connection")
        self.allows("refresh_tree", label="Refresh", help="Refresh tree")
        self.allows("collapse_tree", help="Collapse all")
        self.allows("tree_cursor_down")  # vim j
        self.allows("tree_cursor_up")  # vim k
        self.allows("tree_filter", help="Filter items")
        self.allows("exit_pane", help="Back to pane navigation")
        self.allows(
            "enter_tree_visual_mode",
            lambda app: app.tree_node_kind is not None,
            label="Visual",
            help="Enter visual selection mode",
        )

    def get_hint(self, app: InputContext) -> str | None:
        return (
            f"{hint_key('tree_cursor_down', 'j')}/{hint_key('tree_cursor_up', 'k')} move. <enter> expands. "
            f"{hint_key('tree_filter', '/')} filters. "
            f"{hint_key('exit_pane', '<esc>')} goes back to pane navigation."
        )

    def is_active(self, app: InputContext) -> bool:
        return app.focus == "explorer" and not app.tree_filter_active
