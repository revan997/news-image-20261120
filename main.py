#!/usr/bin/env python3
"""news-image-20261120 round 6 — one-day newspaper front page.

Draws a 1024x1024 front page (masthead, lead story with a Kyiv hero
photograph of a bridge over the Dnipro at dusk, a 2x2 grid of shorter
stories, and a footer) and writes entry.png ONLY to the directory named
by $MAKEFUN_OUTPUT_DIR (default /output). It never writes to the repo
directory by default.

Stdlib + PIL only, no network, deterministic.
"""

import os

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1024, 1024
MARGIN = 36
CONTENT_W = 952

PAPER = (253, 251, 246)
INK = (17, 17, 17)
MUTED = (85, 85, 85)
RED = (176, 30, 30)
DARK_RULE = (60, 60, 60)
LIGHT_RULE = (180, 175, 165)
FOOTER_INK = (34, 34, 34)
CAPTION_BAR = (20, 20, 22)
GRID_BODY = (40, 40, 40)
WHITE = (255, 255, 255)

SYSTEM_FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(filename, size):
    """Load a font from the bundled fonts/ copy first, then the system
    copy, then fall back to PIL's default font."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "fonts", filename),
        os.path.join(SYSTEM_FONT_DIR, filename),
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap: add each word to the current line while the
    line still fits max_width (measured with the draw context's
    text-length for the font); otherwise start a new line."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred_text(draw, y, text, font, fill):
    """Draw text centred horizontally on the page at the given y."""
    x = (WIDTH - draw.textlength(text, font=font)) / 2
    draw.text((x, y), text, font=font, fill=fill)


def rule(draw, y, height, fill):
    """A horizontal rule across the content width at y."""
    draw.rectangle(
        [MARGIN, y, MARGIN + CONTENT_W, y + height - 1], fill=fill
    )


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(img)

    serif_bold_44 = load_font("DejaVuSerif-Bold.ttf", 44)
    serif_bold_40 = load_font("DejaVuSerif-Bold.ttf", 40)
    sans_19 = load_font("DejaVuSans.ttf", 19)
    sans_18 = load_font("DejaVuSans.ttf", 18)
    sans_15 = load_font("DejaVuSans.ttf", 15)
    sans_14 = load_font("DejaVuSans.ttf", 14)
    sans_bold_13 = load_font("DejaVuSans-Bold.ttf", 13)
    sans_bold_20 = load_font("DejaVuSans-Bold.ttf", 20)

    # ---- Masthead ----
    centred_text(draw, 12, "THE WORLD IN ONE DAY", serif_bold_44, INK)
    centred_text(draw, 58, "FRIDAY, 20 NOVEMBER 2026", sans_19, MUTED)
    rule(draw, 86, 2, DARK_RULE)

    # ---- Lead block ----
    draw.text((MARGIN, 94), "LEAD", font=sans_bold_13, fill=RED)
    draw.text(
        (MARGIN, 114),
        "Russia hits three Kyiv bridges \u2014",
        font=serif_bold_40,
        fill=INK,
    )
    draw.text(
        (MARGIN, 160),
        "and a missile lands in Poland",
        font=serif_bold_40,
        fill=INK,
    )
    draw.text(
        (MARGIN, 208),
        "Also: Trump, Xi and Putin sign a peace pledge \u2014 "
        "but it says nothing about Ukraine",
        font=sans_18,
        fill=MUTED,
    )
    rule(draw, 240, 1, LIGHT_RULE)

    # ---- Hero: Kyiv bridge over the Dnipro at dusk ----
    here = os.path.dirname(os.path.abspath(__file__))
    hero = Image.open(os.path.join(here, "hero.png")).convert("RGB")
    hero = hero.resize((CONTENT_W, 340), Image.LANCZOS)
    img.paste(hero, (MARGIN, 250))
    draw = ImageDraw.Draw(img)
    caption_top = 250 + 340 - 38
    draw.rectangle(
        [MARGIN, caption_top, MARGIN + CONTENT_W, 250 + 340],
        fill=CAPTION_BAR,
    )
    draw.text(
        (50, 250 + 340 - 30),
        "Kyiv \u2014 a bridge over the Dnipro at dusk",
        font=sans_14,
        fill=WHITE,
    )

    # ---- Grid of four stories, 2x2 ----
    stories = [
        (
            "COURT",
            "Justice Dept drops Alaska Senate appeal",
            "Mary Peltola won the seat; the U.S. Justice Dept. gave up "
            "its bid to block certification.",
        ),
        (
            "STORM",
            "Cyclone Akvan hits India's east coast",
            "Landfall near Gopalpur; 300,000 people evacuated. No deaths "
            "reported in the first checks.",
        ),
        (
            "MARKETS",
            "Dow sinks below 50,000 as stocks slide",
            "The Dow fell 2.2% after Anthropic's big IPO debut failed to "
            "lift Wall Street.",
        ),
        (
            "COP31",
            "COP31 talks reach final day in deadlock",
            "Nations demand a stronger deal in Antalya as the draft drops "
            "fossil-fuel language.",
        ),
    ]
    cell_w = 464
    cell_h = 138
    gutter = 24
    for index, (label, headline, body) in enumerate(stories):
        col = index % 2
        row = index // 2
        x = MARGIN + col * (cell_w + gutter)
        y = 606 + row * (cell_h + gutter)
        draw.text((x, y), label, font=sans_bold_13, fill=RED)
        headline_y = y + 20
        head_lines = wrap_text(draw, headline, sans_bold_20, cell_w)[:2]
        for i, line in enumerate(head_lines):
            draw.text(
                (x, headline_y + i * 25),
                line,
                font=sans_bold_20,
                fill=INK,
            )
        body_y = headline_y + len(head_lines) * 25 + 4
        body_lines = wrap_text(draw, body, sans_14, cell_w)[:3]
        for i, line in enumerate(body_lines):
            draw.text(
                (x, body_y + i * 19),
                line,
                font=sans_14,
                fill=GRID_BODY,
            )

    # ---- Footer ----
    rule(draw, 924, 2, DARK_RULE)
    draw.text((MARGIN, 936), "ALSO TODAY", font=sans_bold_13, fill=RED)
    footer_items = [
        "NZ 368 all out; India reply 159/1",
        "Anthropic ends IPO day up 17%",
        "US jobless claims rise to 203,000",
    ]
    col_w = CONTENT_W // 3
    for i, item in enumerate(footer_items):
        draw.text(
            (MARGIN + i * col_w, 962),
            item,
            font=sans_15,
            fill=FOOTER_INK,
        )

    # ---- Output: ONLY to $MAKEFUN_OUTPUT_DIR (default /output) ----
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG")
    print(out_path)


if __name__ == "__main__":
    main()
