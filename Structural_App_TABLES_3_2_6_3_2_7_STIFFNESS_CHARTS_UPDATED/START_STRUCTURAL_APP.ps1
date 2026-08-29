Set-Location $PSScriptRoot
if (!(Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
Start-Process "http://127.0.0.1:8000"
& ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
