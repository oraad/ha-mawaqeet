#!/usr/bin/env python3
"""Generate Mawaqeet brand PNG assets from SVG sources for Home Assistant."""

from __future__ import annotations

import argparse
import io
import re
from pathlib import Path

import resvg_py
from PIL import Image

BRAND_DIR = (
    Path(__file__).resolve().parent.parent / "custom_components" / "mawaqeet" / "brand"
)
SRC_DIR = BRAND_DIR / "src"
PREVIEW_DIR = SRC_DIR / "previews"

VIEWBOX_RE = re.compile(
    r'viewBox\s*=\s*["\']([\d.\-eE]+)\s+([\d.\-eE]+)\s+([\d.\-eE]+)\s+([\d.\-eE]+)["\']'
)

# (filename, svg, canvas_w, canvas_h, pad_px)
ProductionAsset = tuple[str, Path, int, int, int]

PRODUCTION_ASSETS: list[ProductionAsset] = [
    ("icon.png", SRC_DIR / "icon.svg", 256, 256, 4),
    ("icon@2x.png", SRC_DIR / "icon.svg", 512, 512, 8),
    ("dark_icon.png", SRC_DIR / "icon-dark.svg", 256, 256, 4),
    ("dark_icon@2x.png", SRC_DIR / "icon-dark.svg", 512, 512, 8),
    ("logo.png", SRC_DIR / "logo.svg", 512, 128, 8),
    ("logo@2x.png", SRC_DIR / "logo.svg", 1024, 256, 16),
    ("dark_logo.png", SRC_DIR / "logo-dark.svg", 512, 128, 8),
    ("dark_logo@2x.png", SRC_DIR / "logo-dark.svg", 1024, 256, 16),
]

COMPARE_ASSETS: list[ProductionAsset] = [
    ("logo-inter.png", SRC_DIR / "logo-inter.svg", 512, 128, 8),
    ("logo-inter-dark.png", SRC_DIR / "logo-inter-dark.svg", 512, 128, 8),
    ("logo-nunito.png", SRC_DIR / "logo-nunito.svg", 512, 128, 8),
    ("logo-nunito-dark.png", SRC_DIR / "logo-nunito-dark.svg", 512, 128, 8),
]


def _parse_viewbox(svg_text: str) -> tuple[float, float, float, float]:
    """Return viewBox (x, y, width, height) from SVG text."""
    match = VIEWBOX_RE.search(svg_text)
    if not match:
        msg = "SVG has no viewBox attribute"
        raise ValueError(msg)
    return tuple(float(g) for g in match.groups())


def _render_svg(svg_path: Path, render_width: int) -> bytes:
    """Rasterize an SVG at viewBox aspect (avoids resvg letterboxing)."""
    svg_text = svg_path.read_text(encoding="utf-8")
    _x, _y, vb_w, vb_h = _parse_viewbox(svg_text)
    render_height = max(1, round(render_width * vb_h / vb_w))
    return resvg_py.svg_to_bytes(
        svg_string=svg_text,
        width=render_width,
        height=render_height,
    )


def _normalize_png(
    png_bytes: bytes,
    canvas_w: int,
    canvas_h: int,
    pad: int,
) -> bytes:
    """Crop to alpha bbox, scale uniformly, center on canvas with equal padding."""
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    inner_w = canvas_w - 2 * pad
    inner_h = canvas_h - 2 * pad
    scale = min(inner_w / img.width, inner_h / img.height)
    new_w = max(1, round(img.width * scale))
    new_h = max(1, round(img.height * scale))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    ox = (canvas_w - new_w) // 2
    oy = (canvas_h - new_h) // 2
    canvas.paste(img, (ox, oy), img)

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def _margin_stats(img: Image.Image) -> dict[str, int]:
    """Alpha bounding box margins relative to image edges."""
    bbox = img.getbbox()
    if not bbox:
        return {"left": 0, "top": 0, "right": 0, "bottom": 0}
    left, top, right, bottom = bbox
    return {
        "left": left,
        "top": top,
        "right": img.width - right,
        "bottom": img.height - bottom,
    }


def _write_assets(
    assets: list[ProductionAsset],
    output_dir: Path,
    *,
    check_margins: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, svg_path, canvas_w, canvas_h, pad in assets:
        if not svg_path.is_file():
            msg = f"Missing SVG source: {svg_path}"
            raise FileNotFoundError(msg)
        # Render at 2x canvas width for sharper downscale after normalize.
        render_width = canvas_w * 2
        png_bytes = _render_svg(svg_path, render_width)
        png_bytes = _normalize_png(png_bytes, canvas_w, canvas_h, pad)
        path = output_dir / name
        path.write_bytes(png_bytes)
        print(f"Wrote {path}")

        if check_margins:
            img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
            stats = _margin_stats(img)
            lr_delta = abs(stats["left"] - stats["right"])
            tb_delta = abs(stats["top"] - stats["bottom"])
            print(
                f"  margins L{stats['left']} T{stats['top']} "
                f"R{stats['right']} B{stats['bottom']} "
                f"(pad target {pad}, lr_delta={lr_delta}, tb_delta={tb_delta})"
            )


def main() -> None:
    """Write brand PNG assets from SVG sources."""
    parser = argparse.ArgumentParser(description="Generate Mawaqeet brand PNGs")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Also write logo comparison previews (Inter vs Nunito)",
    )
    parser.add_argument(
        "--check-margins",
        action="store_true",
        help="Print alpha margin stats after each PNG",
    )
    args = parser.parse_args()

    _write_assets(
        PRODUCTION_ASSETS,
        BRAND_DIR,
        check_margins=args.check_margins,
    )
    if args.compare:
        _write_assets(
            COMPARE_ASSETS,
            PREVIEW_DIR,
            check_margins=args.check_margins,
        )


if __name__ == "__main__":
    main()
