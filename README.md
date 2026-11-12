# dokottahealth-utils

Small, dependency-free tools for sports, wearable health and insurance data. Python 3 standard library only.

| file | what it does |
|---|---|
| [`hrv.py`](hrv.py) | Heart rate variability from RR intervals: mean HR, SDNN, RMSSD, pNN50, with artefact filtering |
| [`training_load.py`](training_load.py) | Session load (Banister TRIMP) and acute:chronic workload ratio from heart-rate sessions |
| [`activity_discount.py`](activity_discount.py) | Wellness score and example discount tier from daily steps, active minutes and resting HR trend |
| [`claims_stats.py`](claims_stats.py) | Claim frequency, severity, loss ratio and pure premium from a claims list |

```sh
python hrv.py rr.csv
python training_load.py sessions.csv --rest 55 --max 190
python activity_discount.py activity.csv --days 30
python claims_stats.py claims.csv --policy-years 1200 --earned-premium 450000
```

For training and research use, not medical diagnosis or real underwriting. MIT licence.
