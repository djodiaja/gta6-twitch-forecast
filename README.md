# GTA VI Twitch CCU Forecast

![make.fun competition](https://make.fun/badge/competition/gta6-twitch-ccu-forecast-01)
![make.fun rank](https://make.fun/badge/rank/gta6-twitch-ccu-forecast-01)
![make.fun reward](https://make.fun/badge/reward/gta6-twitch-ccu-forecast-01)

Forecasts GTA VI Twitch concurrent viewer counts for hours 2-24 of launch day, given hour 1 data and comparable game launch histories.

## Strategy

Uses a **comparable-based growth curve model**:

1. Extracts hourly viewer trajectories from comparable game launches (e.g. Elden Ring)
2. Computes log-scale growth ratios (hour_h / hour_1) across all comparables
3. Applies empirical quantiles of those ratios to the hour-1 observation
4. Falls back to persistence with drift for hours without comparable data

This beats the baseline persistence forecast because major game launches follow predictable intraday patterns.

## Usage

```bash
MAKEFUN_INPUT_DIR=./input MAKEFUN_OUTPUT_DIR=./output python3 main.py
```
