"""Ghostty theme integration for sqlit.

Builds a "ghostty" Textual theme from the colors of the active Ghostty
theme, so sqlit can follow the terminal — including themes that another
tool regenerates on the fly. Only activates when a Ghostty config exists.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from textual.color import Color
from textual.theme import Theme

GHOSTTY_THEME_NAME = "ghostty"

GHOSTTY_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "ghostty"
GHOSTTY_SYSTEM_THEME_DIR = Path("/usr/share/ghostty/themes")

# Ghostty reads both file names; later files override earlier ones.
_CONFIG_FILE_NAMES = ("config", "config.ghostty")
_COLOR_KEYS = {"background", "foreground", "selection-background"}
_HEX_COLOR = re.compile(r"#?([0-9a-fA-F]{6})$")


def _parse_ghostty_file(path: Path) -> dict[str, str]:
    """Parse ``key = value`` lines into ``{"theme", color keys, "0".."15"}``.

    Colors that aren't plain hex (named X11 colors) are skipped.
    """
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return values

    for line in lines:
        key, sep, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"')
        if not sep or key.startswith("#"):
            continue
        if key == "theme":
            # "light:Foo,dark:Bar" picks per system appearance; take dark.
            variants = dict(part.split(":", 1) for part in value.split(",") if ":" in part)
            values["theme"] = variants.get("dark", value).strip()
            continue
        if key == "palette":
            key, _, value = value.partition("=")
            key, value = key.strip(), value.strip()
            if not key.isdigit():
                continue
        elif key not in _COLOR_KEYS:
            continue
        match = _HEX_COLOR.match(value)
        if match:
            values[key] = f"#{match.group(1)}"
    return values


def read_ghostty_colors(
    config_dir: Path | None = None,
    system_theme_dir: Path | None = None,
) -> dict[str, str] | None:
    """Return Ghostty's effective colors, or None when they can't be determined.

    Keys: ``background``, ``foreground``, optionally ``selection-background``
    and the palette indexes ``"0"``..``"15"``.
    """
    config_dir = config_dir or GHOSTTY_CONFIG_DIR
    system_theme_dir = system_theme_dir or GHOSTTY_SYSTEM_THEME_DIR

    config: dict[str, str] = {}
    for name in _CONFIG_FILE_NAMES:
        config.update(_parse_ghostty_file(config_dir / name))

    colors: dict[str, str] = {}
    theme_name = config.pop("theme", None)
    if theme_name:
        for candidate in (Path(theme_name).expanduser(), config_dir / "themes" / theme_name, system_theme_dir / theme_name):
            if candidate.is_file():
                colors.update(_parse_ghostty_file(candidate))
                break
    colors.pop("theme", None)
    colors.update(config)  # colors set directly in the config win over the theme

    if "background" not in colors or "foreground" not in colors:
        return None
    return colors


def build_ghostty_theme(colors: dict[str, str]) -> Theme:
    """Map Ghostty colors (see :func:`read_ghostty_colors`) to a Textual theme."""
    background, foreground = colors["background"], colors["foreground"]

    def palette(index: int, default: str) -> str:
        return colors.get(str(index), default)

    border = palette(8, foreground)
    return Theme(
        name=GHOSTTY_THEME_NAME,
        primary=palette(4, foreground),
        secondary=palette(6, foreground),
        accent=palette(5, foreground),
        warning=palette(3, foreground),
        error=palette(1, foreground),
        success=palette(2, foreground),
        foreground=foreground,
        background=background,
        surface=background,
        panel=palette(0, background),
        dark=Color.parse(background).brightness < 0.5,
        variables={
            "border": border,
            "footer-background": background,
            "footer-key-foreground": palette(4, foreground),
            "input-selection-background": f"{colors.get('selection-background', border)} 40%",
        },
    )
