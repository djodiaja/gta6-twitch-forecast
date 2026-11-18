import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]


def round2(x):
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value == int(value) else value


def quantile_sorted(values, p):
    if not values:
        return 0.0
    n = len(values)
    if n == 1:
        return values[0]
    idx = p * (n - 1)
    lo = int(math.floor(idx))
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return values[lo] * (1 - frac) + values[hi] * frac


def extract_launch_day_ratios(comparables, day_start_key="day_start"):
    ratios_by_hour = {}
    for comp in comparables:
        hourly = comp.get("hourly", [])
        if not hourly:
            continue
        day_start = comp.get(day_start_key, "")
        if not day_start:
            continue
        day_hours = {}
        for entry in hourly:
            entry_time = entry.get("from", "")
            viewers = entry.get("viewers", 0)
            if viewers <= 0:
                continue
            if entry_time >= day_start:
                try:
                    ds_hour = int(day_start[11:13])
                    ds_day = int(day_start[8:10])
                    ds_month = int(day_start[5:7])
                    e_hour = int(entry_time[11:13])
                    e_day = int(entry_time[8:10])
                    e_month = int(entry_time[5:7])
                    day_diff = 0
                    if e_month == ds_month:
                        day_diff = e_day - ds_day
                    elif e_month > ds_month:
                        day_diff = e_day + 30 - ds_day
                    hour_offset = day_diff * 24 + (e_hour - ds_hour)
                    hour_num = hour_offset + 1
                    if 1 <= hour_num <= 24:
                        day_hours[hour_num] = viewers
                except (ValueError, IndexError):
                    continue
        h1 = day_hours.get(1, 0)
        if h1 <= 0:
            continue
        for h in range(2, 25):
            vh = day_hours.get(h, 0)
            if vh > 0:
                ratio = vh / h1
                if h not in ratios_by_hour:
                    ratios_by_hour[h] = []
                ratios_by_hour[h].append(math.log(ratio))
    return ratios_by_hour


def forecast_case(case, name):
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))
    comparables = case.get("comparables", [])
    log_ratios_by_hour = extract_launch_day_ratios(comparables)
    hours_out = []
    for row in case["forecast"]:
        h = row["hour"]
        log_ratios = log_ratios_by_hour.get(h, [])
        if len(log_ratios) >= 2:
            sorted_ratios = sorted(log_ratios)
            quantiles = []
            for level in LEVELS:
                log_q = quantile_sorted(sorted_ratios, level)
                q_val = p1 * math.exp(log_q)
                q_val = max(1.0, min(1e9, q_val))
                quantiles.append(round2(q_val))
            for i in range(1, len(quantiles)):
                if quantiles[i] < quantiles[i - 1]:
                    quantiles[i] = quantiles[i - 1]
        else:
            sigma = 0.20
            Z = [-1.645, -0.674, 0, 0.674, 1.645]
            quantiles = [round2(max(1.0, p1 * math.exp(z * sigma * math.sqrt(h - 1)))) for z in Z]
        hours_out.append({"hour": h, "q": quantiles})
    return {"hours": hours_out}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
