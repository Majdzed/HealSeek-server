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

def test_create_appointment():
    try:
        response = client.post(
            "/appointments",
            json={
                "appointment_time": "2025-01-31 18:48:00",
                "status": "scheduled",
                "type": "in_person",
                "doctor_id": "177607",
                "patient_id": "349095"
            }
        )
        assert response.status_code == 200
    except Exception as e:
        print(f"Test Error: {e}")
        raise