BankFlask (cleaned)

This repository contains the working Flask banking demo app in `BankFlask/`.

Quick start (Windows PowerShell):

```powershell
# activate venv (if present)
& .venv\Scripts\Activate.ps1

# install deps
pip install -r BankFlask\requirements.txt

# run dev server
python BankFlask\run.py
```

Notes:
- The repo was cleaned to keep only `BankFlask/` and the virtualenv `.venv/`.
- Secrets and local files are ignored by `.gitignore`.
