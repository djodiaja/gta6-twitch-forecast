[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/djodiaja/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/djodiaja/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

# GTA VI Twitch CCU Forecast

Entry for the [Forecast GTA VI's launch-day Twitch viewers hour by hour](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?ref=vkeq2szk) bounty on make.fun.

## Strategy

Uses a **comparable-based growth curve model**:

1. Extracts hourly viewer trajectories from comparable game launches (e.g. Elden Ring)
2. Computes log-scale growth ratios (hour_h / hour_1) across all comparables
3. Applies empirical quantiles of those ratios to the hour-1 observation
4. Falls back to persistence with drift (sigma = 0.20, widening with sqrt of the horizon) for hours with fewer than two comparable samples

Quantiles are rounded half-up to 2 decimals and forced to be monotonic.

## Run

```sh
MAKEFUN_INPUT_DIR=./input MAKEFUN_OUTPUT_DIR=./output python3 main.py
```

Reads `*.in` cases from the input directory and writes `*.out` quantile forecasts (hours 2-24) to the output directory.

Referral code: `vkeq2szk`
