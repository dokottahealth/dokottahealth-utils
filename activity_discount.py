"""Wellness score and discount tier from daily wearable data.

    python activity_discount.py activity.csv [--days 30]

CSV columns: date (YYYY-MM-DD), steps, active_minutes, resting_hr (any can be blank).
Tiers and thresholds are example values, not real underwriting.
"""
import argparse
import csv
import statistics
from datetime import date, timedelta

STEP_GOAL = 10_000          # steps per day
ACTIVE_GOAL = 150           # active minutes per week (WHO guideline)
MIN_COVERAGE = 0.7          # share of days the wearable must have been worn
TIERS = [("gold", 80, 15), ("silver", 60, 10), ("bronze", 40, 5)]  # name, min score, discount %


def read_days(path):
    days = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            num = lambda k: float(row[k]) if row.get(k, "").strip() else None
            days[date.fromisoformat(row["date"].strip())] = {
                "steps": num("steps"), "active_minutes": num("active_minutes"), "resting_hr": num("resting_hr"),
            }
    return days


def wellness_score(days, period=30, end=None):
    """Score out of 100: steps (40), weekly active minutes (40), resting HR trend (20)."""
    end = end or max(days)
    window = [days[d] for d in (end - timedelta(i) for i in range(period)) if d in days]
    coverage = len(window) / period
    if coverage < MIN_COVERAGE:
        return {"coverage": coverage, "score": None, "tier": "insufficient data", "discount_pct": 0}

    steps = [d["steps"] for d in window if d["steps"] is not None]
    active = [d["active_minutes"] for d in window if d["active_minutes"] is not None]
    avg_steps = statistics.fmean(steps) if steps else 0
    weekly_active = 7 * statistics.fmean(active) if active else 0

    trend = None
    hr_points = 10  # neutral when there isn't enough resting HR data
    hr = [(i, days[d]["resting_hr"]) for i, d in enumerate(sorted(d for d in days if end - timedelta(period) < d <= end))
          if days[d]["resting_hr"] is not None]
    if len(hr) >= 7:
        trend = statistics.linear_regression([x for x, _ in hr], [y for _, y in hr]).slope * 30  # bpm per 30 days
        hr_points = 20 if trend <= -1 else 0 if trend >= 2 else 10

    score = round(40 * min(avg_steps / STEP_GOAL, 1) + 40 * min(weekly_active / ACTIVE_GOAL, 1) + hr_points)
    tier, discount = next(((name, pct) for name, low, pct in TIERS if score >= low), ("none", 0))
    return {
        "coverage": coverage, "avg_steps": avg_steps, "weekly_active_min": weekly_active,
        "resting_hr_trend_bpm_per_30d": trend, "score": score, "tier": tier, "discount_pct": discount,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--days", type=int, default=30, help="period to score, ending at the last day in the file")
    a = p.parse_args()
    for k, v in wellness_score(read_days(a.csv), a.days).items():
        print(f"{k:30} {v:.2f}" if isinstance(v, float) else f"{k:30} {v}")
