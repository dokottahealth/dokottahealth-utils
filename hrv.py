"""Heart rate variability from RR intervals (ms), as exported by chest straps and watches.

    python hrv.py rr.csv            # one RR interval per line, or a column named rr / rr_ms
"""
import csv
import math
import statistics
import sys


def clean_rr(rr, low=300, high=2000, max_jump=0.2):
    """Drop physiologically implausible beats and ectopic jumps larger than 20%."""
    out = []
    for x in rr:
        if not low <= x <= high:
            continue
        if out and abs(x - out[-1]) / out[-1] > max_jump:
            continue
        out.append(x)
    return out


def hrv(rr):
    """Time-domain HRV: mean HR, SDNN, RMSSD, pNN50 and ln(RMSSD)."""
    rr = clean_rr(rr)
    if len(rr) < 3:
        raise ValueError("need at least 3 valid RR intervals")
    diffs = [b - a for a, b in zip(rr, rr[1:])]
    rmssd = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    return {
        "beats": len(rr),
        "mean_hr_bpm": 60000 / statistics.fmean(rr),
        "sdnn_ms": statistics.stdev(rr),
        "rmssd_ms": rmssd,
        "pnn50_pct": 100 * sum(abs(d) > 50 for d in diffs) / len(diffs),
        "ln_rmssd": math.log(rmssd) if rmssd > 0 else float("nan"),
    }


def read_rr(path):
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    if rows and rows[0] and not rows[0][0].replace(".", "", 1).isdigit():
        col = [h.strip().lower() for h in rows[0]].index(
            next(h for h in ("rr_ms", "rr") if h in [c.strip().lower() for c in rows[0]])
        )
        rows = rows[1:]
    else:
        col = 0
    return [float(r[col]) for r in rows if r and r[col].strip()]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for k, v in hrv(read_rr(sys.argv[1])).items():
        print(f"{k:12} {v:.1f}" if isinstance(v, float) else f"{k:12} {v}")
