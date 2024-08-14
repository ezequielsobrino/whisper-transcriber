@echo off
cd C:\Users\ezequ\PycharmProjects\whisper-transcriber
call .venv\Scripts\activate

REM Intenta abrir con Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:5000/v2"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:5000/v2"
) else (
    REM Si Chrome no está instalado, usa el navegador por defecto
    start http://127.0.0.1:5000/v2
)

python run.py