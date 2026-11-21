@echo off
cd /d C:\IGRIS
echo ========================================================
echo Starting IGRIS Local Inference Server (FastAPI + PyTorch)
echo ========================================================
.venv\Scripts\python.exe run_inference_server.py
pause
