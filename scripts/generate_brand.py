#!/usr/bin/env python3
"""Generate Mawaqeet brand PNG assets for Home Assistant."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BRAND_DIR = (
    Path(__file__).resolve().parent.parent / "custom_components" / "mawaqeet" / "brand"
)

TEAL = (13, 115, 119, 255)
GOLD = (212, 175, 95, 255)
WHITE = (245, 245, 245, 255)


def _draw_icon(
    draw: ImageDraw.ImageDraw, size: int, fg: tuple[int, int, int, int]
) -> None:
    """Draw crescent and minaret motif centered in a square."""
    cx, cy = size // 2, size // 2
    r = int(size * 0.32)
    draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        outline=fg,
        width=max(2, size // 32),
    )
    draw.ellipse(
        (cx - int(r * 0.55), cy - r, cx + int(r * 0.55), cy + r),
        fill=(0, 0, 0, 0),
    )
    draw.rectangle(
        (cx + int(r * 0.35), cy - int(r * 1.1), cx + int(r * 0.55), cy + int(r * 1.2)),
        fill=fg,
    )
    draw.polygon(
        [
            (cx + int(r * 0.45), cy - int(r * 1.25)),
            (cx + int(r * 0.72), cy - int(r * 0.85)),
            (cx + int(r * 0.18), cy - int(r * 0.85)),
        ],
        fill=fg,
    )


def _make_icon(size: int, fg: tuple[int, int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _draw_icon(draw, size, fg)
    return img


def _make_logo(width: int, height: int, fg: tuple[int, int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    icon_size = height - 16
    icon = _make_icon(icon_size, fg)
    img.paste(icon, (8, 8), icon)
    text = "Mawaqeet"
    try:
        font = ImageFont.truetype("arial.ttf", max(28, height // 3))
    except OSError:
        font = ImageFont.load_default()
    draw.text((icon_size + 24, height // 2 - 14), text, fill=fg, font=font)
    return img


def main() -> None:
    """Write all brand assets."""
    BRAND_DIR.mkdir(parents=True, exist_ok=True)

    assets: list[tuple[str, Image.Image]] = [
        ("icon.png", _make_icon(256, TEAL)),
        ("dark_icon.png", _make_icon(256, GOLD)),
        ("icon@2x.png", _make_icon(512, TEAL)),
        ("dark_icon@2x.png", _make_icon(512, GOLD)),
        ("logo.png", _make_logo(512, 128, TEAL)),
        ("dark_logo.png", _make_logo(512, 128, GOLD)),
    ]

    for name, image in assets:
        path = BRAND_DIR / name
        image.save(path, format="PNG", optimize=True)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
