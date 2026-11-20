# The World in One Day — 20 November 2026 (Round 3)

[![make.fun](https://make.fun/badge.svg)](https://make.fun/bounty/news-image-20261120)
[![competition: news-image-20261120](https://make.fun/badge-competition-news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

One image that sums up Friday 20 November 2026 — the whole day, not just
the morning: a newspaper front page. This is round 3 of the entry: it
keeps the verified stories of the morning edition, updates them with what
actually happened during the day, and adds the day's late-breaking news.
Round 3 tightens the lead to two lines, leads the page with the Riyadh
strike photograph (the damaged PIF Tower — evidential, not decorative),
and cuts the story grid from four small items to three bigger ones.

## The day

- **The summit (lead).** Trump, Xi and Putin signed a joint peace pledge
  in Shenzhen — but it says nothing about Ukraine. Trump rated the summit
  "12 out of 10"; Putin admitted it sets no ambitious goals; the
  declaration also skips the war in Iran. (BusinessWorld / Reuters
  roundup, 20 Nov 2026)
- **Ukraine · Poland.** Overnight Russian ballistic strikes hit three
  bridges over the Dnipro in Kyiv, killing at least three people — and a
  Russian Kh-101 cruise missile crashed in south-east Poland. Prime
  Minister Tusk called it a deliberate provocation. (Reuters, AP,
  20 Nov 2026)
- **The court.** The International Court of Justice ruled, 9–6, that
  Myanmar committed genocide against the Rohingya in 2017 — the first time
  the court has held a state responsible for genocide. Reparations are
  ordered; Myanmar called the ruling "unfair". (CNN / Reuters,
  19–20 Nov 2026)
- **The storm.** Cyclone Akvan made landfall near Gopalpur, on India's
  Odisha coast, with winds of 70–80 km/h. More than 300,000 people were
  evacuated; no deaths or major damage were reported. (IMD / The Hindu,
  20 Nov 2026)
- **Markets.** Anthropic's shares closed near $97, up 17% on their Nasdaq
  debut, after the biggest IPO in history — $81.3bn raised. Goldman Sachs
  and Morgan Stanley earned $113m each in fees. (Anthropic, 20 Nov 2026)
- **Riyadh.** A Houthi missile hit Riyadh's tallest tower, the PIF Tower,
  home of Saudi Arabia's sovereign wealth fund, blowing out windows across
  seven floors. No one was hurt. (Reuters, 19 Nov 2026)
- **Culture · Gaming.** GTA VI made an estimated $2.36bn in a single day
  — about 24.6 million copies, the biggest entertainment launch ever.
  (Sensor Tower via Deadline, 20 Nov 2026)
- **Also today.** A Van Gogh sold for a record $190.4m; a migrant boat
  sank off Senegal, dozens missing; Henry Nicholls' unbeaten 175 lifted
  New Zealand to 368 against India; the COP31 draft dropped its call to
  phase out fossil fuels.

Every headline was checked against live reporting of 20 November 2026
(BBC, Reuters, AP, CNN, IMD, The Hindu, Anthropic, Sensor Tower).

## How it is built

`draw_poster_r3.py` (build-time only, not part of the entry) draws the
front page with Pillow: masthead, a two-line lead headline, a fresh
photographic strike hero (the Riyadh PIF Tower after the Houthi missile
hit — twisted glass, shattered windows, smoke, emergency vehicles below;
no text in it), a full-width second lead, three stories in one row, a
GTA VI strip and a larger footer. The program itself is `main.py` (Python 3.13, standard library
only): it verifies `entry.png` is a whole, well-formed 1024×1024 PNG under
1 MiB — magic, IHDR geometry, per-chunk CRCs, IEND trailer, no trailing
bytes — then copies it byte-for-byte to `/output/entry.png` and re-reads
the copy to confirm it matches.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two consecutive runs write byte-identical output.

## License

MIT — see [LICENSE](LICENSE).
