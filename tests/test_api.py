from fastapi.testclient import TestClient
from src.app import app
import uuid

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity check for known activity
    assert "Chess Club" in data


def test_signup_and_delete_participant():
    activity = "Chess Club"
    email = f"testuser+{uuid.uuid4().hex}@example.com"

    # Sign up the new participant
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # Confirm participant appears in the activity
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert email in activities[activity]["participants"]

    # Duplicate signup should be rejected for the same activity
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Remove the participant
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200

    # Confirm removal
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_delete_nonexistent_participant():
    activity = "Chess Club"
    email = f"noone+{uuid.uuid4().hex}@example.com"
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404
