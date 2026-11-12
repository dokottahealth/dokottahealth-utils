# dokottahealth-utils

[English](README.md) | **Português**

Ferramentas pequenas e sem dependências para dados de desporto e de dispositivos de saúde vestíveis. Apenas a biblioteca padrão do Python 3.

| ficheiro | o que faz |
|---|---|
| [`hrv.py`](hrv.py) | Variabilidade da frequência cardíaca a partir de intervalos RR: FC média, SDNN, RMSSD, pNN50, com filtragem de artefactos |
| [`training_load.py`](training_load.py) | Carga por sessão (TRIMP de Banister) e rácio de carga aguda:crónica a partir de sessões de frequência cardíaca |

```sh
python hrv.py rr.csv
python training_load.py sessions.csv --rest 55 --max 190
```

Para treino e investigação, não para diagnóstico médico. Licença MIT.
