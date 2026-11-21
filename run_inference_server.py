"""IGRIS Local Inference Server Runner.

Automatically configures sys.path to include src/ and launches the FastAPI daemon.
"""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if __name__ == "__main__":
    import uvicorn
    print(f"[*] Starting IGRIS Inference Runtime (PID {os.getpid()})...")
    print("[*] Target endpoint: http://127.0.0.1:8000")
    print("[*] Health check URL: http://127.0.0.1:8000/health")
    uvicorn.run("igris.inference.server:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
