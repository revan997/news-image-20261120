#!/usr/bin/env python3
"""Round 4 entrypoint: draw the 20 Nov 2026 newspaper front page.

Reads hero-riyadh.webp from this directory, renders a 1024x1024 front
page (masthead, Kyiv/Poland lead, Riyadh hero photo, summit second lead,
four-story grid, GTA VI strip, high-contrast footer), writes entry.png
to $MAKEFUN_OUTPUT_DIR (or the current directory), then validates the
PNG bytes in memory before reporting success.

Stdlib + Pillow only. No network. Deterministic output.
"""

import os
import struct
import sys
import zlib

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 36            # side margin for text columns
HERO_X = 14            # hero spans almost the full page width
HERO_W = PAGE_W - 2 * HERO_X
HERO_H = 240

PAPER = (247, 242, 231)
INK = (26, 26, 26)
FOOTER_INK = (34, 34, 34)
KICKER_RED = (163, 22, 33)
STRIP_BG = (236, 228, 208)
HAIRLINE = (138, 131, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_BOLD = FONT_DIR + "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, face, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=face) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_tracked(draw, xy, text, face, fill, tracking=0):
    """Draw text with extra space between characters; returns width used."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=face, fill=fill)
        x += draw.textlength(ch, font=face) + tracking
    return x - xy[0] - tracking


def draw_lines(draw, x, y, lines, face, fill, line_height):
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += line_height
    return y


def slanted_caption(text, face, fill, width):
    """Render a caption line sheared slightly to read as italic.

    DejaVu Sans ships no oblique face on this machine, so the text is
    drawn flat onto a layer and skewed with an affine transform.
    """
    pad = 24
    layer = Image.new("RGBA", (width + 2 * pad, face.size + 16), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.text((pad, 4), text, font=face, fill=fill + (255,))
    shear = 0.16
    shift = int(face.size * shear) + 2
    layer = layer.transform(
        layer.size, Image.AFFINE,
        (1, -shear, shear * layer.size[1] - shift, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    return layer


def panoramic_crop(hero, target_w, target_h):
    """Centre-crop the hero photo to the target aspect ratio."""
    src_w, src_h = hero.size
    target_ratio = target_w / target_h
    crop_h = int(src_w / target_ratio)
    if crop_h > src_h:  # pragma: no cover - hero is wider than target
        crop_h = src_h
    top = (src_h - crop_h) // 2
    box = (0, top, src_w, top + crop_h)
    return hero.crop(box).resize((target_w, target_h), Image.LANCZOS)


def build_page(base_dir):
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    # Thin dark frame around the page edge.
    draw.rectangle([6, 6, PAGE_W - 7, PAGE_H - 7], outline=INK, width=3)

    content_w = PAGE_W - 2 * MARGIN
    debug = bool(os.environ.get("R4_DEBUG"))
    y = 20

    def mark(tag, yy):
        if debug:
            print(f"  [layout] {tag}: y={yy}", file=sys.stderr)
        return yy

    # ---- Masthead ----
    mast_face = font(SERIF_BOLD, 64)
    draw.text((PAGE_W // 2, y), "THE WORLD IN ONE DAY",
              font=mast_face, fill=INK, anchor="ma")
    y += 82
    date_face = font(SANS, 15)
    date_text = "FRIDAY, 20 NOVEMBER 2026 — THE DAY IN FULL"
    date_w = draw.textlength(date_text, font=date_face) + 3 * (len(date_text) - 1)
    draw_tracked(draw, ((PAGE_W - date_w) // 2, y), date_text,
                 date_face, INK, tracking=3)
    y += 26
    draw.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=2)
    y += 14

    # ---- Lead: Kyiv bridges + missile in Poland ----
    lead_face = font(SERIF_BOLD, 35)
    lead_lines = wrap_text(
        draw, "Russia hits three Kyiv bridges — and a missile lands in Poland",
        lead_face, content_w)
    y = draw_lines(draw, MARGIN, y, lead_lines, lead_face, INK, 46)
    y += 6
    deck_face = font(SANS, 17)
    deck_lines = wrap_text(
        draw,
        "Three Dnipro crossings hit in the biggest strikes on Kyiv since the "
        "war began — 3 killed, 15 injured. A Kh-101 missile crashes near Nowy "
        "Lipowiec, 60 km from the Polish border; PM Tusk calls it 'likely an "
        "intentional provocation'. No one is hurt in Poland.",
        deck_face, content_w)
    y = draw_lines(draw, MARGIN, y, deck_lines, deck_face, INK, 24)
    y += 10

    # ---- Hero: Riyadh PIF Tower after the missile strike ----
    hero_path = os.path.join(base_dir, "hero-riyadh.webp")
    with Image.open(hero_path) as hero_img:
        hero_img = hero_img.convert("RGB")
        hero_band = panoramic_crop(hero_img, HERO_W, HERO_H)
    page.paste(hero_band, (HERO_X, y))
    draw.rectangle([HERO_X, y, HERO_X + HERO_W - 1, y + HERO_H - 1],
                   outline=INK, width=1)
    y += HERO_H + 8

    caption_face = font(SANS, 13)
    caption = ("RIYADH — Houthi missile hits the PIF Tower, HQ of Saudi "
               "Arabia's sovereign wealth fund. Windows blown out across "
               "seven floors. No one is hurt.")
    caption_layer = slanted_caption(caption, caption_face, INK, HERO_W)
    page.paste(caption_layer, (HERO_X, y), caption_layer)
    y += caption_face.size + 10

    # ---- Second lead: summit peace pledge ----
    second_face = font(SERIF_BOLD, 28)
    second_lines = wrap_text(
        draw, "Trump, Xi and Putin sign a peace pledge — but it says nothing "
        "about Ukraine", second_face, content_w)
    y = draw_lines(draw, MARGIN, y, second_lines, second_face, INK, 37)
    y += 4
    second_deck_face = font(SANS, 16)
    second_deck = wrap_text(
        draw, "Trump rates it '12 out of 10'. Putin: no ambitious goals. "
        "Ukraine and Iran are not mentioned.", second_deck_face, content_w)
    y = draw_lines(draw, MARGIN, y, second_deck, second_deck_face, INK, 22)
    y += 12

    # ---- Grid: four stories in one row ----
    grid_top = y
    col_w = content_w // 4
    kicker_face = font(SANS_BOLD, 12)
    grid_head_face = font(SERIF_BOLD, 19)
    grid_body_face = font(SANS, 13)
    stories = [
        ("THE COURT", "Myanmar guilty of Rohingya genocide",
         "ICJ holds a state responsible for genocide for the first time, 9–6. "
         "Reparations ordered."),
        ("THE STORM", "Cyclone Akvan hits India's east coast",
         "Landfall near Gopalpur, winds to 90 km/h. Over 300,000 evacuated; "
         "no deaths reported."),
        ("MARKETS", "Anthropic soars 17% on its market debut",
         "Shares close near $97. The $81.3bn listing is the largest IPO ever."),
        ("CLIMATE", "COP31 draft drops fossil-fuel phase-out",
         "The climate summit's draft text omits the phase-out goal."),
    ]
    grid_bottom = grid_top
    for i, (kicker, headline, body) in enumerate(stories):
        col_x = MARGIN + i * col_w
        text_x = col_x + 8
        text_w = col_w - 16
        cy = grid_top
        draw_tracked(draw, (text_x, cy), kicker, kicker_face,
                     KICKER_RED, tracking=1)
        cy += 20
        head_lines = wrap_text(draw, headline, grid_head_face, text_w)
        cy = draw_lines(draw, text_x, cy, head_lines, grid_head_face, INK, 25)
        cy += 4
        body_lines = wrap_text(draw, body, grid_body_face, text_w)
        cy = draw_lines(draw, text_x, cy, body_lines, grid_body_face, INK, 18)
        grid_bottom = max(grid_bottom, cy)
        if i < 3:
            rule_x = col_x + col_w
            draw.line([(rule_x, grid_top + 2), (rule_x, grid_bottom)],
                      fill=HAIRLINE, width=1)
    y = grid_bottom + 12

    # ---- GTA VI strip ----
    strip_top = y
    strip_h = 64
    draw.rectangle([MARGIN, strip_top, PAGE_W - MARGIN, strip_top + strip_h],
                   fill=STRIP_BG)
    draw.line([(MARGIN, strip_top), (PAGE_W - MARGIN, strip_top)],
              fill=INK, width=1)
    draw.line([(MARGIN, strip_top + strip_h), (PAGE_W - MARGIN, strip_top + strip_h)],
              fill=INK, width=1)
    strip_head_face = font(SERIF_BOLD, 22)
    strip_sub_face = font(SANS, 15)
    draw.text((PAGE_W // 2, strip_top + 7), "GTA VI makes $2.36bn in a single day",
              font=strip_head_face, fill=INK, anchor="ma")
    draw.text((PAGE_W // 2, strip_top + 38),
              "About 24.6m copies — the biggest entertainment launch ever.",
              font=strip_sub_face, fill=INK, anchor="ma")
    y = strip_top + strip_h + 12

    # ---- Footer: ALSO TODAY (high contrast charcoal on cream) ----
    draw.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=1)
    y += 10
    label_face = font(SANS_BOLD, 15)
    draw_tracked(draw, (MARGIN, y), "ALSO TODAY", label_face,
                 FOOTER_INK, tracking=2)
    y += 24
    footer_face = font(SANS, 15)
    footer_text = ("Van Gogh sells for a record $190.4m  •  Migrant boat sinks "
                   "off Senegal, dozens missing  •  Nicholls' 175* lifts New "
                   "Zealand to 368 vs India")
    footer_lines = wrap_text(draw, footer_text, footer_face, content_w)
    y = draw_lines(draw, MARGIN, y, footer_lines, footer_face, FOOTER_INK, 21)

    if y > PAGE_H - 12:
        raise RuntimeError(f"page overflow: content ends at y={y}")
    return page


def validate_png(data):
    """Check PNG bytes in memory. Returns (width, height) or raises ValueError."""
    if not data:
        raise ValueError("empty file")
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        raise ValueError("bad PNG signature")
    pos = 8
    saw_ihdr = False
    saw_iend = False
    width = height = None
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated chunk header")
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        if pos + 8 + length + 4 > len(data):
            raise ValueError("truncated chunk data")
        chunk_data = data[pos + 8:pos + 8 + length]
        stored_crc = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])[0]
        actual_crc = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError(f"bad CRC in {ctype!r} chunk")
        if ctype == b"IHDR":
            if saw_ihdr:
                raise ValueError("duplicate IHDR")
            if length != 13:
                raise ValueError("bad IHDR length")
            width, height = struct.unpack(">II", chunk_data[:8])
            saw_ihdr = True
        if ctype == b"IEND":
            if length != 0:
                raise ValueError("bad IEND length")
            saw_iend = True
            pos += 12 + length
            break
        pos += 12 + length
    if not saw_ihdr:
        raise ValueError("missing IHDR")
    if not saw_iend:
        raise ValueError("missing IEND (truncated file)")
    if pos != len(data):
        raise ValueError("trailing bytes after IEND")
    if width != PAGE_W or height != PAGE_H:
        raise ValueError(f"wrong size {width}x{height}, expected 1024x1024")
    return width, height


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    page = build_page(base_dir)
    page.save(out_path, format="PNG", compress_level=6)

    with open(out_path, "rb") as fh:
        blob = fh.read()
    width, height = validate_png(blob)
    print(f"ok: entry.png {width}x{height}, {len(blob)} bytes")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
