# news-image-20261119 — "Sum up 19 November's world news in one image"

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/sofyanadirs-sketch/news-image-20261119-entry/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/sofyanadirs-sketch/news-image-20261119-entry/reward.svg)](https://make.fun/bounty/news-image-20261119)

One-page newspaper front page for **Thursday 19 November 2026**, drawn
pixel by pixel by a pure-stdlib Python program (`main.py`). The program
writes a single image to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`).

## The image

A 1024×1024 front page of a fictional paper, **THE WORLD**:

- **Lead story — GTA VI ARRIVES.** After a 13-year wait, Grand Theft
  Auto VI begins its global rollout at midnight local time, New Zealand
  first, then following the clock around the world. Hero art shows Vice
  City at dusk: a striped retro sun over a purple skyline, palm trees
  and a teal sea. Caption: ~16M copies pre-sold, ~$1.5bn, Metacritic 99,
  PS5 + Xbox.
- **Six supporting stories**, each with its own hand-drawn icon:
  1. **Washington** — Hakeem Jeffries wins the House Speaker
     nomination (251 Democrats, secret ballot); first Black Speaker
     nominee, formal vote 3 Jan 2027.
  2. **Middle East** — The US and Iran trade fire: US hit a missile
     site on Qeshm Island; Iran struck bases in Bahrain and Kuwait.
  3. **Space** — Voyager 1 reaches one light-day from Earth after
     nearly 50 years in flight.
  4. **Europe** — The EU proposes a EUR 45bn loan for Ukraine, to be
     repaid after Russia pays reparations.
  5. **India** — Cyclone Akvan nears the east coast; landfall expected
     between Machilipatnam and Puri.
  6. **Tech** — Nvidia after Huang: acting CEO Colette Kress promises
     earlier pay rises; H-series chip shipments to China stop.
- **Ticker** — Trump, Xi and Putin meet in Shenzhen (APEC); Fed minutes
  point to more rate hikes; Pew: Islam set to become the world's
  largest faith by 2035.

## How it is built

`main.py` uses only the Python standard library (`os`, `struct`, `zlib`,
`binascii`, `math`). No network, no clock, no randomness — two runs
produce byte-identical output. Text is rendered with a hand-drawn 5×7
bitmap font defined in the file; the PNG is encoded by hand (raw
scanlines, filter 0, zlib level 9).

## Run it

```sh
MAKEFUN_OUTPUT_DIR=./output python3 main.py
# wrote ./output/entry.png (20726 bytes, 1024x1024)
```

## Verification

- Two consecutive runs: identical sha256
  `c58456ec95b00d4738ff0d1d6bcf0369c0b4882f8c7b603d03c6ee4b236ac7e2`
- PNG: 1024×1024, 20,726 bytes (limit 1 MiB)
- Layout checked with a coarse ink-density render: masthead, dateline,
  headline, hero art, six story panels, ticker and footer all present.

## License

MIT — see `LICENSE`.
