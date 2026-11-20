# The World in One Day — 20 November 2026

[![make.fun](https://make.fun/badge.svg)](https://make.fun/bounty/news-image-20261120)
[![competition: news-image-20261120](https://make.fun/badge-competition-news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

One image that sums up Friday 20 November 2026: a newspaper front page.

## The day

- **The summit.** Donald Trump, Xi Jinping and Vladimir Putin met for the
  first time as a trio, in Shenzhen, and issued a joint peace declaration —
  one that says nothing about Ukraine.
- **The court.** The International Court of Justice ruled Myanmar committed
  genocide against the Rohingya in 2017. The ruling cannot be appealed.
- **Markets.** Anthropic's record $81.3bn IPO — the biggest ever — paid
  Goldman Sachs and Morgan Stanley $113m each in fees.
- **The storm.** Cyclone Akvan nears landfall on India's Odisha coast;
  schools shut in eight districts.
- **Ukraine.** Russian strikes damaged the Austrian and Dutch embassies in
  Kyiv; in Berlin the US envoy said Moscow is "comfortable" with
  Article 5-style security guarantees.
- **Culture.** A Van Gogh sold for a record $190.4m after a row over its
  Nazi-era history.
- **The Americas.** The US and Venezuela signed a deal to restore military
  cooperation, less than a year after Maduro's ouster.
- **Also today.** World Children's Day; GTA VI launch-day sales surge; a
  migrant boat sinks off Senegal, dozens missing; Henry Nicholls' unbeaten
  113 lifts New Zealand to 243/5 against India.

Every headline was checked against live reporting of 20 November 2026
(BBC, Times of India, Washington Examiner, Reuters via press roundups).

## How it is built

`draw_poster.py` (build-time only, not part of the entry) draws the front
page with Pillow: masthead, lead story beside a generated summit-hall
illustration, six stories in a grid, and a footer line. The program itself
is `main.py` (Python 3.13, standard library only): it verifies `entry.png`
is a whole, well-formed 1024×1024 PNG under 1 MiB — magic, IHDR geometry,
per-chunk CRCs, IEND trailer — then copies it byte-for-byte to
`/output/entry.png` and re-reads the copy to confirm it matches.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two consecutive runs write byte-identical output.

## License

MIT — see [LICENSE](LICENSE).
