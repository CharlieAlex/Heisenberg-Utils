# heisenberg-utils

## 套件架構

```bash
.
├── __init__.py
├── array_utils.py
├── bigquery_utils.py
├── config_utils.py
├── decorators.py
├── functional_utils.py
├── gcs_utils.py
├── gsheet_utils.py
├── io_utils.py
├── logger_utils.py
├── ml_utils.py
├── pandas_utils.py
└── sequence_utils.py

1 directory, 13 files
```

## 注意事項

- 一定要有 `.env`，裡面放 `GOOGLE_APPLICATION_CREDENTIALS` 的路徑
- 一定要有 `MAIN_PATH`，代表專案根目錄路徑