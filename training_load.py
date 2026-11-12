"""Training load from heart rate: Banister TRIMP per session, then acute:chronic workload ratio.

    python training_load.py sessions.csv --rest 55 --max 190 [--female]
    # sessions.csv columns: date,minutes,avg_hr
"""
import argparse
import csv
import math
from datetime import date, timedelta


def trimp(minutes, avg_hr, rest_hr, max_hr, female=False):
    """Banister TRIMP: duration weighted by heart-rate reserve."""
    hrr = min(max((avg_hr - rest_hr) / (max_hr - rest_hr), 0.0), 1.0)
    a, b = (0.86, 1.67) if female else (0.64, 1.92)
    return minutes * hrr * a * math.exp(b * hrr)


def daily_loads(sessions):
    """Sum load per day and fill rest days with 0, from first to last session."""
    by_day = {}
    for d, load in sessions:
        by_day[d] = by_day.get(d, 0.0) + load
    if not by_day:
        return []
    day, last, out = min(by_day), max(by_day), []
    while day <= last:
        out.append((day, by_day.get(day, 0.0)))
        day += timedelta(days=1)
    return out


def acwr(loads, acute=7, chronic=28):
    """Exponentially weighted acute and chronic load for each day; the ratio starts once `chronic` days exist."""
    la, lc = 2 / (acute + 1), 2 / (chronic + 1)
    a = c = 0.0
    out = []
    for i, (d, x) in enumerate(loads):
        a = la * x + (1 - la) * a
        c = lc * x + (1 - lc) * c
        out.append({"date": d, "load": x, "acute": a, "chronic": c, "ratio": a / c if c and i + 1 >= chronic else None})
    return out


def zone(ratio):
    """Commonly cited ACWR bands; a guide, not a diagnosis."""
    if ratio is None:
        return "building"
    if ratio < 0.8:
        return "low"
    if ratio <= 1.3:
        return "ok"
    if ratio <= 1.5:
        return "high"
    return "spike"


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--rest", type=float, required=True, help="resting heart rate")
    p.add_argument("--max", type=float, required=True, help="maximum heart rate")
    p.add_argument("--female", action="store_true")
    args = p.parse_args()
    with open(args.csv, newline="") as f:
        sessions = [
            (date.fromisoformat(r["date"]), trimp(float(r["minutes"]), float(r["avg_hr"]), args.rest, args.max, args.female))
            for r in csv.DictReader(f)
        ]
    print("date        load  acute chronic ratio zone")
    for r in acwr(daily_loads(sessions)):
        ratio = f"{r['ratio']:.2f}" if r["ratio"] else "  -  "
        print(f"{r['date']} {r['load']:5.0f} {r['acute']:6.1f} {r['chronic']:7.1f} {ratio:>5} {zone(r['ratio'])}")
