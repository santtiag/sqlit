"""Tests for pane navigation: hjkl between panes, enter to go in, escape to leave."""

from __future__ import annotations

import pytest

from sqlit.core.vim import VimMode
from sqlit.domains.shell.app.main import SSMSTUI

from ..mocks import MockConnectionStore, MockSettingsStore, build_test_services, create_test_connection


def _make_app() -> SSMSTUI:
    services = build_test_services(
        connection_store=MockConnectionStore(
            [create_test_connection("a", "sqlite"), create_test_connection("b", "sqlite")]
        ),
        settings_store=MockSettingsStore({"theme": "tokyo-night"}),
    )
    return SSMSTUI(services=services)


@pytest.mark.asyncio
async def test_starts_in_pane_nav_and_hjkl_moves_between_panes():
    app = _make_app()

    async with app.run_test(size=(100, 35)) as pilot:
        await pilot.pause()
        assert app._pane_nav
        assert app.object_tree.has_focus

        # Edge: nothing to the left of / below the explorer.
        await pilot.press("h", "j")
        assert app.object_tree.has_focus

        await pilot.press("l")
        assert app.query_input.has_focus
        await pilot.press("j")
        assert app._get_focus_pane() == "results"
        await pilot.press("k")
        assert app.query_input.has_focus
        await pilot.press("h")
        assert app.object_tree.has_focus
        assert app._pane_nav


@pytest.mark.asyncio
async def test_pane_keys_are_inactive_until_enter():
    app = _make_app()

    async with app.run_test(size=(100, 35)) as pilot:
        await pilot.pause()
        line = app.object_tree.cursor_line

        # In pane navigation "n" (new connection) must not open a dialog.
        await pilot.press("n")
        await pilot.pause()
        assert len(app.screen_stack) == 1

        await pilot.press("enter")
        assert not app._pane_nav
        await pilot.press("j")
        assert app.object_tree.cursor_line == line + 1

        await pilot.press("escape")
        assert app._pane_nav
        assert app.object_tree.has_focus


@pytest.mark.asyncio
async def test_query_enter_insert_and_escape_twice_returns_to_pane_nav():
    app = _make_app()

    async with app.run_test(size=(100, 35)) as pilot:
        await pilot.pause()
        await pilot.press("l", "enter")
        assert app.query_input.has_focus
        assert app.vim_mode == VimMode.NORMAL
        assert not app._pane_nav

        await pilot.press("i", "a", "b")
        assert app.query_input.text == "ab"

        await pilot.press("escape")
        assert app.vim_mode == VimMode.NORMAL
        assert not app._pane_nav

        await pilot.press("escape")
        assert app._pane_nav

        # Back in pane navigation: digits and letters no longer reach the editor.
        await pilot.press("3", "x")
        assert app.query_input.text == "ab"
        assert app._count_buffer == ""
