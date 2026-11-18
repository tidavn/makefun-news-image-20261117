# makefun-news-image-20261117
[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/tidavn/makefun-news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/tidavn/makefun-news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

A broadsheet front page that sums up Tuesday 17 November 2026 in one image: 29 real stories across 6 continents, a lead on the Kerch Bridge strike, a "Day in Numbers" strip and a schematic world map — drawn entirely in code with Pillow, so the output is byte-identical on every run.

## Run it

```sh
python3 main.py
```

Writes the front page to `/output/entry.png` (or `$ENTRY_OUTPUT`, falling back to `./entry.png`). No network, no clock, no randomness — the bundled DejaVu fonts in `fonts/` (see `fonts/DejaVu-LICENSE.txt`) make the render self-contained and deterministic.

<sub>Entered on [make.fun](https://make.fun/?ref=k73yfdz2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
