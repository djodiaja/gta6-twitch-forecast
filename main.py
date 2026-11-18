import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]


def round2(x):
    """Deterministic round-half-up to 2 decimals (not banker's rounding)."""
    return math.floor(x * 100 + 0.5) / 100


def quantile_sorted(values, p):
    """Linear-interpolation quantile of an ascending-sorted list."""
    n = len(values)
    if n == 0:
        raise ValueError("empty values")
    if n == 1:
        return values[0]
    pos = p * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return values[lo] + (values[hi] - values[lo]) * frac


def _parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def extract_launch_day_ratios(comparables):
    """Return {hour: [log(viewers_h / viewers_1), ...]} for hours 2..24.

    Each comparable has `day_start` (ISO timestamp) and `hourly`, a list of
    {"from": ISO timestamp, "viewers": int}. Hour k is the bucket starting
    (k-1) hours after day_start. Comparables without a positive hour-1 print
    are skipped.
    """
    ratios_by_hour = {}
    for comp in comparables:
        day_start = comp.get("day_start")
        hourly = comp.get("hourly") or []
        if not day_start or not hourly:
            continue
        try:
            t0 = _parse_ts(day_start)
        except (ValueError, TypeError):
            continue
        by_hour = {}
        for entry in hourly:
            try:
                viewers = float(entry.get("viewers", 0))
                delta = _parse_ts(entry["from"]) - t0
            except (ValueError, TypeError, KeyError):
                continue
            if viewers <= 0:
                continue
            hour = int(delta.total_seconds() // 3600) + 1
            if 1 <= hour <= 24:
                by_hour[hour] = viewers
        h1 = by_hour.get(1)
        if not h1:
            continue
        for h in range(2, 25):
            if h in by_hour:
                ratios_by_hour.setdefault(h, []).append(math.log(by_hour[h] / h1))
    return ratios_by_hour


FALLBACK_SIGMA = 0.20
FALLBACK_Z = [-1.645, -0.674, 0.0, 0.674, 1.645]
MIN_SAMPLES = 2


def forecast_case(case, name):
    if case.get("levels") != LEVELS:
        raise ValueError(f"{name} asks for levels {case.get('levels')}, not {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))
    ratios_by_hour = extract_launch_day_ratios(case.get("comparables", []))

    hours_out = []
    for row in case["forecast"]:
        h = row["hour"]
        log_ratios = ratios_by_hour.get(h, [])
        if len(log_ratios) >= MIN_SAMPLES:
            s = sorted(log_ratios)
            raw = [p1 * math.exp(quantile_sorted(s, lv)) for lv in LEVELS]
        else:
            spread = FALLBACK_SIGMA * math.sqrt(max(h - 1, 0))
            raw = [p1 * math.exp(z * spread) for z in FALLBACK_Z]
        q = []
        for v in raw:
            v = round2(max(1.0, min(1e9, v)))
            if q and v < q[-1]:
                v = q[-1]
            q.append(v)
        hours_out.append({"hour": h, "q": q})
    return {"hours": hours_out}


INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        result = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
