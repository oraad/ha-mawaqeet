#!/usr/bin/env python3
"""Export font-derived wordmark paths and assemble brand SVG logos."""

from __future__ import annotations

import urllib.request
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "custom_components" / "mawaqeet" / "brand" / "src"
FONTS_DIR = SRC_DIR / "fonts"

FONT_URLS = {
    "Inter-VF.ttf": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/"
        "Inter%5Bopsz%2Cwght%5D.ttf"
    ),
    "NunitoSans-VF.ttf": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/nunitosans/"
        "NunitoSans%5BYTLC%2Copsz%2Cwdth%2Cwght%5D.ttf"
    ),
    "NotoSansArabic-VF.ttf": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansarabic/"
        "NotoSansArabic%5Bwdth%2Cwght%5D.ttf"
    ),
}

LATIN_TEXT = "Mawaqeet"
ARABIC_TEXT = "مواقيت"
TEAL = "#0D7377"
GOLD = "#D4AF5F"

MARK_SCALE = 0.40625
MARK_OFFSET = (14, 12)
TEXT_X = 130
LATIN_Y = 52
ARABIC_Y = 88
LATIN_HEIGHT = 34
ARABIC_HEIGHT = 28
CONTENT_PAD = 6
ICON_PAD = 12  # margin around trimmed icon viewBox (avoids raster clip)
CRESCENT_BOUNDS_PAD = 3  # safety for arc/antialias outside mathematical bbox

# Mark geometry bounds in 256x256 mark space (updated by _write_mark_svg).
MARK_XMIN, MARK_XMAX = 52.0, 186.0
MARK_YMIN, MARK_YMAX = 48.0, 194.0


def _ensure_fonts() -> None:
    """Download bundled OFL variable fonts if missing."""
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FONT_URLS.items():
        path = FONTS_DIR / name
        if path.is_file():
            continue
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(url, path)  # noqa: S310


def _write_mark_svg() -> str:
    """Write mark.svg (crescent + minaret) and return inner <g> markup."""
    global MARK_XMIN, MARK_XMAX, MARK_YMIN, MARK_YMAX

    # Crescent centered; horn faces right
    crescent_cx, crescent_cy = 128.0, 128.0
    outer_r, inner_r, inner_dx = 76.0, 60.0, 28.0
    inner_cx = crescent_cx + inner_dx

    # Minaret aligned in crescent opening
    plinth_x, plinth_y, plinth_w, plinth_h, plinth_rx = 150.0, 178.0, 26.0, 14.0, 4.0
    stem_x, stem_y, stem_w, stem_h, stem_rx = 157.0, 98.0, 12.0, 80.0, 2.5
    balcony_x, balcony_y, balcony_w, balcony_h, balcony_rx = (
        148.0,
        132.0,
        22.0,
        8.0,
        2.0,
    )
    cap_gap = 2.0
    cap_base_y = stem_y - cap_gap
    cap_apex = (163.0, 66.0)
    cap_left = (stem_x, cap_base_y)
    cap_right = (stem_x + stem_w, cap_base_y)

    # Star accent above the horn
    star_cx, star_cy, star_r = 182.0, 54.0, 7.0
    star_path = (
        f"M {star_cx:.2f} {star_cy - star_r:.2f} "
        f"L {star_cx + star_r * 0.28:.2f} {star_cy - star_r * 0.28:.2f} "
        f"L {star_cx + star_r:.2f} {star_cy:.2f} "
        f"L {star_cx + star_r * 0.28:.2f} {star_cy + star_r * 0.28:.2f} "
        f"L {star_cx:.2f} {star_cy + star_r:.2f} "
        f"L {star_cx - star_r * 0.28:.2f} {star_cy + star_r * 0.28:.2f} "
        f"L {star_cx - star_r:.2f} {star_cy:.2f} "
        f"L {star_cx - star_r * 0.28:.2f} {star_cy - star_r * 0.28:.2f} Z"
    )

    crescent_path = (
        f"M {crescent_cx:.2f} {crescent_cy - outer_r:.2f} "
        f"A {outer_r:.2f} {outer_r:.2f} 0 1 1 {crescent_cx:.2f} {crescent_cy + outer_r:.2f} "
        f"A {outer_r:.2f} {outer_r:.2f} 0 1 1 {crescent_cx:.2f} {crescent_cy - outer_r:.2f} "
        f"M {inner_cx:.2f} {crescent_cy - inner_r:.2f} "
        f"A {inner_r:.2f} {inner_r:.2f} 0 1 0 {inner_cx:.2f} {crescent_cy + inner_r:.2f} "
        f"A {inner_r:.2f} {inner_r:.2f} 0 1 0 {inner_cx:.2f} {crescent_cy - inner_r:.2f} Z"
    )

    star_pad = star_r * 1.1
    crescent_x1 = crescent_cx - outer_r - CRESCENT_BOUNDS_PAD
    crescent_x2 = crescent_cx + outer_r + CRESCENT_BOUNDS_PAD
    crescent_y1 = crescent_cy - outer_r - CRESCENT_BOUNDS_PAD
    crescent_y2 = crescent_cy + outer_r + CRESCENT_BOUNDS_PAD
    mark_xmin = min(
        crescent_x1,
        plinth_x,
        balcony_x,
        stem_x,
        cap_left[0],
        star_cx - star_pad,
    )
    mark_xmax = max(
        crescent_x2,
        plinth_x + plinth_w,
        balcony_x + balcony_w,
        stem_x + stem_w,
        cap_right[0],
        star_cx + star_pad,
    )
    mark_ymin = min(
        crescent_y1,
        cap_apex[1],
        star_cy - star_pad,
    )
    mark_ymax = max(
        crescent_y2,
        plinth_y + plinth_h,
        star_cy + star_pad,
    )
    MARK_XMIN, MARK_XMAX = mark_xmin, mark_xmax
    MARK_YMIN, MARK_YMAX = mark_ymin, mark_ymax

    inner = f"""  <g id="mawaqeet-mark">
    <defs>
      <clipPath id="mawaqeet-crescent-clip">
        <path fill-rule="evenodd" d="{crescent_path}" />
      </clipPath>
    </defs>
    <path fill="currentColor" fill-rule="evenodd" d="{crescent_path}" />
    <circle
      cx="{inner_cx:.2f}"
      cy="{crescent_cy:.2f}"
      r="{inner_r:.2f}"
      fill="currentColor"
      fill-opacity="0.45"
      clip-path="url(#mawaqeet-crescent-clip)"
    />
    <rect
      x="{plinth_x:.2f}"
      y="{plinth_y:.2f}"
      width="{plinth_w:.2f}"
      height="{plinth_h:.2f}"
      rx="{plinth_rx:.2f}"
      fill="currentColor"
    />
    <rect
      x="{stem_x:.2f}"
      y="{stem_y:.2f}"
      width="{stem_w:.2f}"
      height="{stem_h:.2f}"
      rx="{stem_rx:.2f}"
      fill="currentColor"
    />
    <rect
      x="{balcony_x:.2f}"
      y="{balcony_y:.2f}"
      width="{balcony_w:.2f}"
      height="{balcony_h:.2f}"
      rx="{balcony_rx:.2f}"
      fill="currentColor"
      fill-opacity="0.85"
    />
    <path
      fill="currentColor"
      d="M {cap_apex[0]:.2f} {cap_apex[1]:.2f} L {cap_left[0]:.2f} {cap_left[1]:.2f} L {cap_right[0]:.2f} {cap_right[1]:.2f} Z"
    />
    <path fill="currentColor" fill-opacity="0.75" d="{star_path}" />
  </g>"""

    icon_viewbox = _icon_viewbox()
    mark = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{icon_viewbox}">\n'
        f"{inner}\n</svg>\n"
    )
    (SRC_DIR / "mark.svg").write_text(mark, encoding="utf-8")
    print(f"Wrote {SRC_DIR / 'mark.svg'}")
    return inner


def _icon_viewbox() -> str:
    """Square viewBox trimmed around the mark."""
    width = MARK_XMAX - MARK_XMIN
    height = MARK_YMAX - MARK_YMIN
    side = max(width, height) + 2 * ICON_PAD
    cx = (MARK_XMIN + MARK_XMAX) / 2
    cy = (MARK_YMIN + MARK_YMAX) / 2
    x = cx - side / 2
    y = cy - side / 2
    return f"{x:.2f} {y:.2f} {side:.2f} {side:.2f}"


def _write_icon_svg(filename: str, color: str, mark_inner: str) -> None:
    viewbox = _icon_viewbox()
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" '
        'role="img" aria-label="Mawaqeet">\n'
        f'  <g color="{color}">\n'
        f"{mark_inner}\n"
        "  </g>\n</svg>\n"
    )
    path = SRC_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")


def _shape_text(
    font_path: Path,
    text: str,
    *,
    direction: str = "ltr",
    script: str = "latn",
    language: str | None = None,
) -> tuple[str, float, float, float]:
    """Return path d, advance width, and bounds height/width in font units."""
    ttfont = TTFont(font_path)
    glyph_set = ttfont.getGlyphSet()

    blob = hb.Blob.from_file_path(str(font_path))
    face = hb.Face(blob)
    hb_font = hb.Font(face)

    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = direction
    buf.script = script
    if language:
        buf.language = language
    hb.shape(hb_font, buf)

    pen = SVGPathPen(glyph_set)
    bounds_pen = BoundsPen(glyph_set)
    width = 0.0

    for info, pos in zip(buf.glyph_infos, buf.glyph_positions, strict=True):
        gid = info.codepoint  # HarfBuzz glyph index
        glyph_name = ttfont.getGlyphName(gid)
        tx = width + pos.x_offset
        ty = pos.y_offset
        transform = TransformPen(pen, (1, 0, 0, 1, tx, ty))
        glyph_set[glyph_name].draw(transform)
        glyph_set[glyph_name].draw(TransformPen(bounds_pen, (1, 0, 0, 1, tx, ty)))
        width += pos.x_advance

    path_d = pen.getCommands()
    if not bounds_pen.bounds:
        return path_d, float(width), 0.0, 0.0
    xmin, ymin, xmax, ymax = bounds_pen.bounds
    path_height = ymax - ymin
    path_width = xmax - xmin
    return path_d, float(width), path_height, path_width


def _scaled_text_svg(
    path_d: str,
    path_height: float,
    target_height: float,
    x: float,
    y_baseline: float,
    fill: str,
) -> str:
    scale = target_height / path_height if path_height else 1.0
    # Font outlines use y-up; SVG uses y-down.
    return (
        f'    <g transform="translate({x:.2f}, {y_baseline:.2f}) '
        f'scale({scale:.6f}, {-scale:.6f})">\n'
        f'      <path fill="{fill}" d="{path_d}"/>\n'
        f"    </g>"
    )


def _logo_viewbox(latin_width: float, arabic_width: float) -> str:
    """Trimmed viewBox around mark and wordmark."""
    mark_x1 = MARK_OFFSET[0] + MARK_XMIN * MARK_SCALE
    mark_x2 = MARK_OFFSET[0] + MARK_XMAX * MARK_SCALE
    mark_y1 = MARK_OFFSET[1] + MARK_YMIN * MARK_SCALE
    mark_y2 = MARK_OFFSET[1] + MARK_YMAX * MARK_SCALE

    text_x1 = TEXT_X
    text_x2 = TEXT_X + max(latin_width, arabic_width)
    text_y1 = LATIN_Y - LATIN_HEIGHT
    text_y2 = ARABIC_Y + ARABIC_HEIGHT

    xmin = min(mark_x1, text_x1) - CONTENT_PAD
    ymin = min(mark_y1, text_y1) - CONTENT_PAD
    xmax = max(mark_x2, text_x2) + CONTENT_PAD
    ymax = max(mark_y2, text_y2) + CONTENT_PAD

    content_w = xmax - xmin
    content_h = ymax - ymin
    return f"{xmin:.2f} {ymin:.2f} {content_w:.2f} {content_h:.2f}"


def _build_logo(
    latin_font: Path,
    fill: str,
    out_path: Path,
    mark_inner: str,
) -> None:
    latin_path, latin_advance, latin_h, _latin_w = _shape_text(
        latin_font, LATIN_TEXT, direction="ltr", script="latn"
    )
    arabic_path, arabic_advance, arabic_h, _arabic_w = _shape_text(
        FONTS_DIR / "NotoSansArabic-VF.ttf",
        ARABIC_TEXT,
        direction="rtl",
        script="Arab",
        language="ar",
    )

    latin_scale = LATIN_HEIGHT / latin_h if latin_h else 1.0
    arabic_scale = ARABIC_HEIGHT / arabic_h if arabic_h else 1.0
    latin_block_w = latin_advance * latin_scale
    arabic_block_w = arabic_advance * arabic_scale
    arabic_x = TEXT_X + (latin_block_w - arabic_block_w) / 2

    latin_svg = _scaled_text_svg(
        latin_path,
        latin_h,
        LATIN_HEIGHT,
        TEXT_X,
        LATIN_Y,
        fill,
    )
    arabic_svg = _scaled_text_svg(
        arabic_path,
        arabic_h,
        ARABIC_HEIGHT,
        arabic_x,
        ARABIC_Y,
        fill,
    )

    viewbox = _logo_viewbox(latin_block_w, arabic_block_w)
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" '
        'role="img" aria-label="Mawaqeet">\n'
        f'  <g transform="translate({MARK_OFFSET[0]}, {MARK_OFFSET[1]}) '
        f'scale({MARK_SCALE})" color="{fill}">\n'
        f"{mark_inner}\n"
        "  </g>\n"
        f"{latin_svg}\n"
        f"{arabic_svg}\n"
        "</svg>\n"
    )
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path}")


def main() -> None:
    """Export all brand SVG sources."""
    _ensure_fonts()
    mark_inner = _write_mark_svg()
    _write_icon_svg("icon.svg", TEAL, mark_inner)
    _write_icon_svg("icon-dark.svg", GOLD, mark_inner)

    _build_logo(
        FONTS_DIR / "Inter-VF.ttf",
        TEAL,
        SRC_DIR / "logo-inter.svg",
        mark_inner,
    )
    _build_logo(
        FONTS_DIR / "Inter-VF.ttf",
        GOLD,
        SRC_DIR / "logo-inter-dark.svg",
        mark_inner,
    )
    _build_logo(
        FONTS_DIR / "NunitoSans-VF.ttf",
        TEAL,
        SRC_DIR / "logo-nunito.svg",
        mark_inner,
    )
    _build_logo(
        FONTS_DIR / "NunitoSans-VF.ttf",
        GOLD,
        SRC_DIR / "logo-nunito-dark.svg",
        mark_inner,
    )

    for src, dst in (
        ("logo-inter.svg", "logo.svg"),
        ("logo-inter-dark.svg", "logo-dark.svg"),
    ):
        (SRC_DIR / dst).write_text(
            (SRC_DIR / src).read_text(encoding="utf-8"), encoding="utf-8"
        )
        print(f"Wrote {SRC_DIR / dst} (from {src})")


if __name__ == "__main__":
    main()
