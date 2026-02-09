# EduAI — Frontend Templates (BankFlask)

This folder contains the Flask app and frontend templates for the EduAI project.

Quick run (local development):

```powershell
# activate virtualenv
& C:\language\Bank\.venv\Scripts\Activate.ps1
# install deps
python -m pip install -r requirements.txt
# run dev server
python run.py
```

Run tests:

```powershell
Set-Location -Path 'C:\language\Bank\BankFlask'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest tests/test_smoke_routes.py -q
```

Build in Docker:

```powershell
cd C:\language\Bank\BankFlask
docker build -t eduai:latest .
docker run -p 5000:5000 eduai:latest
```

CI: A GitHub Actions workflow at `.github/workflows/ci.yml` runs tests on push/PR.
