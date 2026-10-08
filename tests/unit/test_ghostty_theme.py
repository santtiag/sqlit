"""Tests for the Ghostty-synced theme."""

from __future__ import annotations

from pathlib import Path

import pytest

from sqlit.domains.shell.app import ghostty
from sqlit.domains.shell.app.ghostty import build_ghostty_theme, read_ghostty_colors
from sqlit.domains.shell.app.main import SSMSTUI
from tests.ui.mocks import MockConnectionStore, MockSettingsStore, build_test_services

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "ghostty"
NO_SYSTEM_THEMES = Path("/nonexistent")


def test_reads_colors_from_the_configured_theme_file():
    colors = read_ghostty_colors(FIXTURE_DIR, NO_SYSTEM_THEMES)

    assert colors is not None
    assert colors["background"] == "#151312"
    assert colors["foreground"] == "#e7e1e0"
    assert colors["4"] == "#cecaba"
    assert colors["selection-background"] == "#4e4540"
    assert "theme" not in colors


def test_config_colors_override_theme_and_variants_pick_dark(tmp_path):
    (tmp_path / "themes").mkdir()
    (tmp_path / "themes" / "night").write_text("background = 000000\nforeground = #ffffff\npalette = 1=#ff0000\n")
    (tmp_path / "themes" / "day").write_text("background = #ffffff\nforeground = #000000\n")
    (tmp_path / "config").write_text('theme = "light:day,dark:night"\n# background = #123456\nforeground = red\n')
    (tmp_path / "config.ghostty").write_text("background = #101010\n")

    colors = read_ghostty_colors(tmp_path, NO_SYSTEM_THEMES)

    # config.ghostty overrides the theme; "red" (not hex) and the comment are ignored.
    assert colors == {"background": "#101010", "foreground": "#ffffff", "1": "#ff0000"}


def test_no_ghostty_config_means_no_theme(tmp_path):
    assert read_ghostty_colors(tmp_path / "missing", NO_SYSTEM_THEMES) is None


def test_theme_maps_terminal_colors():
    theme = build_ghostty_theme(read_ghostty_colors(FIXTURE_DIR, NO_SYSTEM_THEMES))

    assert theme.name == "ghostty"
    assert theme.dark is True
    assert theme.background == theme.surface == "#151312"
    assert theme.primary == "#cecaba"
    assert theme.error == "#ffb4ab"
    assert theme.variables["border"] == "#9a8e88"

    light = build_ghostty_theme({"background": "#ffffff", "foreground": "#000000"})
    assert light.dark is False
    assert light.primary == "#000000"  # no palette: falls back to the foreground


@pytest.mark.asyncio
async def test_app_follows_ghostty_colors_while_running(monkeypatch, tmp_path):
    (tmp_path / "config").write_text("background = #101010\nforeground = #eeeeee\n")
    monkeypatch.setattr(ghostty, "GHOSTTY_CONFIG_DIR", tmp_path)

    services = build_test_services(
        connection_store=MockConnectionStore(),
        settings_store=MockSettingsStore({"theme": "ghostty"}),
    )
    app = SSMSTUI(services=services)

    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        assert app.theme == "ghostty"
        assert app.screen.styles.background.hex == "#101010"

        (tmp_path / "config").write_text("background = #202020\nforeground = #eeeeee\n")
        app._theme_manager.sync_ghostty_theme()
        await pilot.pause()

        assert app.screen.styles.background.hex == "#202020"
        assert app.theme == "ghostty"
