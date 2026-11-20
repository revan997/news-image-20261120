#!/usr/bin/env python3
"""gen_hero.py — procedurally generate the round-6 Kyiv hero (952x340).

Stdlib + PIL only, no network, fully deterministic (fixed seed).
Scene: a cable-stayed bridge over the Dnipro at dusk, Kyiv skyline
on the far bank — Motherland Monument silhouette + a domed church —
warm deck lights and their reflections in the river.
Run: python3 gen_hero.py  -> writes hero.png next to this script.
"""

import math
import os
import random

from PIL import Image, ImageDraw

W, H = 952, 340
HORIZON = 205          # where sky meets the far bank / river top
RIVER_TOP = 228        # river band starts below the far bank
DECK_Y = 196           # bridge deck height


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    rng = random.Random(20261120)
    here = os.path.dirname(os.path.abspath(__file__))
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # ---- 1. Dusk sky: deep blue-violet top -> warm amber at horizon ----
    top = (16, 16, 58)
    mid = (58, 48, 110)
    horizon = (232, 138, 58)
    for y in range(HORIZON + 1):
        t = y / HORIZON
        if t < 0.55:
            col = lerp(top, mid, t / 0.55)
        else:
            col = lerp(mid, horizon, (t - 0.55) / 0.45)
        d.line([(0, y), (W, y)], fill=col)

    # Low sun glow just above the horizon, left of centre.
    sun_x, sun_y = 330, HORIZON - 18
    for r in range(90, 0, -2):
        alpha = 1.0 - r / 90.0
        col = lerp(horizon, (255, 214, 130), alpha)
        d.ellipse([sun_x - r, sun_y - r * 0.62,
                   sun_x + r, sun_y + r * 0.62], fill=col)
    d.ellipse([sun_x - 26, sun_y - 16, sun_x + 26, sun_y + 16],
              fill=(255, 226, 150))

    # A few early stars in the upper sky.
    for _ in range(46):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, 90)
        b = rng.randint(120, 220)
        d.point((x, y), fill=(b, b, 230))

    # Thin clouds catching the sunset light.
    for _ in range(7):
        cx = rng.randint(0, W - 160)
        cy = rng.randint(28, 150)
        cw = rng.randint(90, 180)
        ch = rng.randint(5, 10)
        shade = rng.randint(150, 200)
        d.ellipse([cx, cy, cx + cw, cy + ch], fill=(shade, 110, 110))

    # ---- 2. Far-bank skyline silhouette (dark, low, behind the bridge) ----
    bank = (18, 14, 34)
    d.rectangle([0, HORIZON - 4, W, RIVER_TOP], fill=bank)
    # Blocky rooftops along the far bank.
    x = 0
    while x < W:
        bw = rng.randint(28, 78)
        bh = rng.randint(8, 34)
        d.rectangle([x, HORIZON - 4 - bh, x + bw, RIVER_TOP], fill=bank)
        x += bw + rng.randint(2, 14)
    # Motherland Monument: tall statue on a pedestal — broad body, head,
    # sword held up in the right hand, shield on the left arm.
    mx = 120
    d.polygon([(mx - 16, HORIZON - 4), (mx - 10, HORIZON - 26),
               (mx + 10, HORIZON - 26), (mx + 16, HORIZON - 4)], fill=bank)
    d.polygon([(mx - 7, HORIZON - 26), (mx - 5, HORIZON - 108),
               (mx + 5, HORIZON - 108), (mx + 7, HORIZON - 26)], fill=bank)
    d.ellipse([mx - 7, HORIZON - 122, mx + 7, HORIZON - 106], fill=bank)
    d.line([(mx + 5, HORIZON - 110), (mx + 11, HORIZON - 150)],
           fill=bank, width=3)
    d.rectangle([mx - 24, HORIZON - 98, mx - 12, HORIZON - 76], fill=bank)
    # Domed church (right): drum + onion dome + cross, bell tower beside.
    cx = 800
    d.rectangle([cx - 26, HORIZON - 52, cx + 26, HORIZON - 4], fill=bank)
    d.rectangle([cx - 40, HORIZON - 30, cx + 40, HORIZON - 4], fill=bank)
    d.ellipse([cx - 22, HORIZON - 82, cx + 22, HORIZON - 46], fill=bank)
    d.line([(cx, HORIZON - 96), (cx, HORIZON - 82)], fill=bank, width=2)
    d.line([(cx - 5, HORIZON - 90), (cx + 5, HORIZON - 90)], fill=bank,
           width=2)
    d.rectangle([cx + 52, HORIZON - 66, cx + 70, HORIZON - 4], fill=bank)
    d.polygon([(cx + 50, HORIZON - 66), (cx + 72, HORIZON - 66),
               (cx + 61, HORIZON - 82)], fill=bank)
    # A few lit windows in the skyline.
    for _ in range(34):
        wx = rng.randint(4, W - 5)
        wy = rng.randint(HORIZON - 30, RIVER_TOP - 6)
        d.point((wx, wy), fill=(255, 196, 90))

    # ---- 3. The Dnipro: dark river band, lower third ----
    river_top_col = (30, 34, 74)
    river_bot_col = (10, 12, 34)
    for y in range(RIVER_TOP, H):
        t = (y - RIVER_TOP) / (H - RIVER_TOP)
        d.line([(0, y), (W, y)], fill=lerp(river_top_col, river_bot_col, t))
    # Horizontal light reflections (sun path + deck lights).
    for _ in range(60):
        rx = rng.randint(180, 520)
        ry = rng.randint(RIVER_TOP + 4, H - 6)
        rw = rng.randint(14, 90)
        warm = rng.choice([(232, 150, 70), (255, 196, 110), (120, 130, 200)])
        d.line([(rx, ry), (rx + rw, ry)], fill=warm, width=1)

    # ---- 4. The bridge: cable-stayed, deck + two pylons + cables ----
    # Pylons (behind deck, rising from the river into the sky).
    pylon = (12, 10, 30)
    pylons = [300, 660]
    for px in pylons:
        d.polygon([(px - 9, H), (px - 5, 78), (px + 5, 78), (px + 9, H)],
                  fill=pylon)
        d.rectangle([px - 14, 72, px + 14, 82], fill=pylon)
    # Cables fanning from each pylon top to the deck.
    cable = (200, 190, 220)
    for px in pylons:
        for tx in range(px - 260, px + 261, 44):
            if 0 <= tx <= W:
                d.line([(px, 80), (tx, DECK_Y)], fill=cable, width=1)
    # Deck: a solid dark band spanning the full width, with a warm edge.
    d.rectangle([0, DECK_Y, W, DECK_Y + 12], fill=(14, 12, 32))
    d.line([(0, DECK_Y), (W, DECK_Y)], fill=(255, 170, 80), width=2)
    # Row of small warm lights along the deck.
    for lx in range(12, W, 26):
        d.ellipse([lx - 2, DECK_Y + 3, lx + 2, DECK_Y + 7],
                  fill=(255, 205, 110))
    # Bridge reflection in the water (vertical streaks under the pylons
    # and the deck), drawn as short horizontal dashes.
    for px in pylons:
        for k in range(14):
            ry = RIVER_TOP + 8 + k * 7
            half = max(4, 26 - k)
            d.line([(px - half, ry), (px + half, ry)],
                   fill=(150, 130, 90), width=1)
    for lx in range(12, W, 26):
        ry = RIVER_TOP + 4 + (lx % 5) * 6
        d.line([(lx - 6, ry), (lx + 6, ry)], fill=(200, 150, 70), width=1)

    # ---- 5. Foreground bank at the very bottom (dark, keeps caption legible) ----
    d.rectangle([0, H - 26, W, H], fill=(8, 8, 20))

    out = os.path.join(here, "hero.png")
    img.save(out, format="PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
