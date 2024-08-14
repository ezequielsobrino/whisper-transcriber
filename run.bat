@echo off
cd C:\Users\ezequ\PycharmProjects\whisper-transcriber
call .venv\Scripts\activate
start http://127.0.0.1:5000
python run.py