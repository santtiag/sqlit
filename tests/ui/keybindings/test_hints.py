"""Tests for the hint line and for sqlit shortcuts that moved off vim keys."""

from __future__ import annotations

import pytest
from textual.widgets import Static

from sqlit.core.keymap import reset_keymap
from sqlit.domains.shell.app.main import SSMSTUI

from ..mocks import MockConnectionStore, MockSettingsStore, build_test_services, create_test_connection
from .test_direct_leader_bindings import route


def _make_app() -> SSMSTUI:
    services = build_test_services(
        connection_store=MockConnectionStore([create_test_connection("a", "sqlite")]),
        settings_store=MockSettingsStore({"theme": "tokyo-night"}),
    )
    return SSMSTUI(services=services)


def _hint(app: SSMSTUI) -> str:
    return app.query_one("#hint-bar", Static).render().plain


@pytest.mark.asyncio
async def test_hint_line_explains_each_context():
    app = _make_app()

    async with app.run_test(size=(130, 35)) as pilot:
        await pilot.pause()
        assert "switch panes" in _hint(app)

        await pilot.press("l", "enter")
        await pilot.pause()
        assert "runs the WHOLE editor" in _hint(app)
        assert "<space>o opens it in Neovim" in _hint(app)

        await pilot.press("i", "x", "escape", "v")
        await pilot.pause()
        assert "runs ONLY the selection" in _hint(app)

        await pilot.press("escape", "V")
        await pilot.pause()
        assert "runs ONLY the selected lines" in _hint(app)

        # A dialog owns the keys: no hint underneath it.
        await pilot.press("escape")
        app.action_show_help()
        await pilot.pause()
        assert _hint(app) == ""


@pytest.mark.asyncio
async def test_vim_keys_no_longer_trigger_sqlit_shortcuts():
    app = _make_app()

    async with app.run_test(size=(130, 35)) as pilot:
        app.action_focus_query()
        app.query_input.text = "SELECT 1"
        await pilot.pause()

        await pilot.press("N", "backspace", "question_mark")
        await pilot.pause()
        assert app.query_input.text == "SELECT 1"
        assert len(app.screen_stack) == 1

        # New query now lives in the leader menu.
        await pilot.press("space", "n")
        await pilot.pause()
        assert app.query_input.text == ""


def test_history_and_new_query_are_leader_commands():
    reset_keymap()
    assert route("n", focus="query", leader_pending=True) == "leader_new_query"
    assert route("r", focus="query", leader_pending=True, has_connection=True) == "leader_show_history"
    assert route("r", focus="query", leader_pending=True, has_connection=False) is None
    for key in ("N", "backspace", "question_mark"):
        assert route(key, focus="query") is None
