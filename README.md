# dokottahealth-utils

Small, dependency-free tools for sports and wearable health data. Python 3 standard library only.

| file | what it does |
|---|---|
| [`hrv.py`](hrv.py) | Heart rate variability from RR intervals: mean HR, SDNN, RMSSD, pNN50, with artefact filtering |
| [`training_load.py`](training_load.py) | Session load (Banister TRIMP) and acute:chronic workload ratio from heart-rate sessions |

```sh
python hrv.py rr.csv
python training_load.py sessions.csv --rest 55 --max 190
```

For training and research use, not medical diagnosis. MIT licence.
