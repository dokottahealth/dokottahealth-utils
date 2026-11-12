"""Claim frequency, severity, loss ratio and pure premium from a claims list.

    python claims_stats.py claims.csv --policy-years 1200 --earned-premium 450000 [--expense-ratio 0.25]

CSV columns: date (YYYY-MM-DD), amount. Policy-years is total exposure, e.g. 100 policies for 6 months = 50.
"""
import argparse
import csv
import statistics
from collections import Counter


def read_claims(path):
    with open(path, newline="") as f:
        return [(row["date"].strip(), float(row["amount"])) for row in csv.DictReader(f) if row.get("amount", "").strip()]


def claims_stats(amounts, policy_years, earned_premium=None, expense_ratio=0.25):
    if policy_years <= 0:
        raise ValueError("policy_years must be positive")
    n, total = len(amounts), sum(amounts)
    pure = total / policy_years  # expected claims cost per policy-year = frequency x severity
    out = {
        "claims": n,
        "total_incurred": total,
        "frequency_per_policy_year": n / policy_years,
        "severity_mean": statistics.fmean(amounts) if n else 0.0,
        "severity_median": statistics.median(amounts) if n else 0.0,
        "severity_p90": statistics.quantiles(amounts, n=10, method="inclusive")[-1] if n >= 2 else (amounts[0] if n else 0.0),
        "pure_premium": pure,
        "indicated_premium": pure / (1 - expense_ratio),  # loaded for expenses and margin
    }
    if earned_premium:
        out["loss_ratio_pct"] = 100 * total / earned_premium
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--policy-years", type=float, required=True)
    p.add_argument("--earned-premium", type=float)
    p.add_argument("--expense-ratio", type=float, default=0.25)
    a = p.parse_args()
    claims = read_claims(a.csv)
    for k, v in claims_stats([amt for _, amt in claims], a.policy_years, a.earned_premium, a.expense_ratio).items():
        print(f"{k:28} {v:,.2f}" if isinstance(v, float) else f"{k:28} {v}")
    print("\nclaims by month")
    for month, count in sorted(Counter(d[:7] for d, _ in claims).items()):
        print(f"  {month}  {count}")
