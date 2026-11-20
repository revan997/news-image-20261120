#!/usr/bin/env python3
"""news-image-20261120 ROUND 6 — one-day front page, 1024x1024.

Stdlib + PIL only, no network, deterministic. Writes entry.png
(1024x1024, <=1 MiB) ONLY to $MAKEFUN_OUTPUT_DIR (default /output);
it never writes to the repo dir. Layout: masthead -> lead block
(headline + summit kicker) -> big hero (generated Kyiv Dnipro bridge
at dusk) -> 2x2 grid -> ALSO TODAY footer.
All headlines verified against 20 November 2026 news sources.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952 content width

PAPER = (253, 251, 246)
INK = (17, 17, 17)
MUTED = (85, 85, 85)
RED = (176, 30, 30)
RULE = (60, 60, 60)
LIGHT_RULE = (180, 175, 165)
FOOTER_INK = (34, 34, 34)
CAPTION_BAR = (20, 20, 22)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    # Bundled fonts in repo/fonts/ first (grader may lack system fonts);
    # fall back to the system path, then to PIL's default font.
    here = os.path.dirname(os.path.abspath(__file__))
    bundled = os.path.join(here, "fonts", os.path.basename(path))
    if os.path.exists(bundled):
        return ImageFont.truetype(bundled, size)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = os.path.join(out_dir, "entry.png")

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(SERIF_B, 44)
    f_date = font(SANS, 19)
    f_eyebrow = font(SANS_B, 13)
    f_lead = font(SERIF_B, 40)
    f_kicker = font(SANS, 18)
    f_caption = font(SANS, 14)
    f_label = font(SANS_B, 13)
    f_grid_head = font(SANS_B, 20)
    f_grid_body = font(SANS, 14)
    f_footer = font(SANS, 15)

    # ---- 1. Masthead (~72px) ----
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 12), title, font=f_title, fill=INK)
    date = "FRIDAY, 20 NOVEMBER 2026"
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, 58), date, font=f_date, fill=MUTED)
    d.line([(MARGIN, 86), (W - MARGIN, 86)], fill=RULE, width=2)

    # ---- 2. Lead block ----
    y = 94
    d.text((MARGIN, y), "LEAD", font=f_eyebrow, fill=RED)
    y += 20
    lead_lines = [
        "Russia hits three Kyiv bridges \u2014",
        "and a missile lands in Poland",
    ]
    for line in lead_lines:
        d.text((MARGIN, y), line, font=f_lead, fill=INK)
        y += 46
    kicker = ("Also: Trump, Xi and Putin sign a peace pledge \u2014 "
              "but it says nothing about Ukraine")
    d.text((MARGIN, y + 2), kicker, font=f_kicker, fill=MUTED)
    d.line([(MARGIN, 240), (W - MARGIN, 240)], fill=LIGHT_RULE, width=1)

    # ---- 3. Hero (~340px) ----
    hero = Image.open(os.path.join(here, "hero.png")).convert("RGB")
    hero = hero.resize((CW, 340), Image.LANCZOS)
    img.paste(hero, (MARGIN, 250))
    d.rectangle([MARGIN, 250 + 340 - 38, W - MARGIN, 250 + 340],
                fill=CAPTION_BAR)
    d.text((MARGIN + 14, 250 + 340 - 30),
           "Kyiv \u2014 a bridge over the Dnipro at dusk",
           font=f_caption, fill=(255, 255, 255))

    # ---- 4. Grid 2x2 (~300px) ----
    stories = [
        ("COURT",
         "Justice Dept drops Alaska Senate appeal",
         "Mary Peltola won the seat; the U.S. Justice Dept. "
         "gave up its bid to block certification."),
        ("STORM",
         "Cyclone Akvan hits India's east coast",
         "Landfall near Gopalpur; 300,000 people evacuated. "
         "No deaths reported in the first checks."),
        ("MARKETS",
         "Dow sinks below 50,000 as stocks slide",
         "The Dow fell 2.2% after Anthropic's big IPO debut "
         "failed to lift Wall Street."),
        ("COP31",
         "COP31 talks reach final day in deadlock",
         "Nations demand a stronger deal in Antalya as the "
         "draft drops fossil-fuel language."),
    ]
    gutter = 24
    cell_w = (CW - gutter) // 2  # 464
    cell_h = 138
    grid_y = 606
    for i, (label, head, body) in enumerate(stories):
        cx = MARGIN + (i % 2) * (cell_w + gutter)
        cy = grid_y + (i // 2) * (cell_h + 24)
        d.text((cx, cy), label, font=f_label, fill=RED)
        hy = cy + 20
        for line in wrap(d, head, f_grid_head, cell_w)[:2]:
            d.text((cx, hy), line, font=f_grid_head, fill=INK)
            hy += 25
        by = hy + 4
        for line in wrap(d, body, f_grid_body, cell_w)[:3]:
            d.text((cx, by), line, font=f_grid_body, fill=(40, 40, 40))
            by += 19

    # ---- 5. Footer (~90px) ----
    d.line([(MARGIN, 924), (W - MARGIN, 924)], fill=RULE, width=2)
    d.text((MARGIN, 936), "ALSO TODAY", font=f_label, fill=RED)
    footer_items = [
        "NZ 368 all out; India reply 159/1",
        "Anthropic ends IPO day up 17%",
        "US jobless claims rise to 203,000",
    ]
    col_w = CW // 3
    for i, item in enumerate(footer_items):
        d.text((MARGIN + i * col_w, 962), item, font=f_footer,
               fill=FOOTER_INK)

    img.save(out_path, format="PNG")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
