import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from fastapi.testclient import TestClient
    from main import app
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Python Path: {sys.path}")
    raise

client = TestClient(app)

def test_delete_user():
    try:
        response = client.delete("/users/1")

        assert response.status_code == 200
        assert len(response.json()) > 0
    except Exception as e:
        print(f"Test Error: {e}")
        raise