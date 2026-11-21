import httpx
import fastapi
from starlette.testclient import TestClient
print("FastAPI:", fastapi.__version__)
print("HTTPX:", httpx.__version__)
print("TestClient available!")
