from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def api(monkeypatch):
    test_activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app), test_activities


def test_get_activities_returns_activity_data(api):
    # Arrange
    client, test_activities = api

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == test_activities


def test_signup_adds_participant(api):
    # Arrange
    client, test_activities = api
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in test_activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant_without_mutating_activity(api):
    # Arrange
    client, test_activities = api
    activity_name = "Chess Club"
    participants_before = list(test_activities[activity_name]["participants"])
    email = participants_before[0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert test_activities[activity_name]["participants"] == participants_before


def test_signup_returns_404_for_unknown_activity(api):
    # Arrange
    client, _ = api

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(api):
    # Arrange
    client, test_activities = api
    activity_name = "Chess Club"
    email = test_activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in test_activities[activity_name]["participants"]


def test_unregister_returns_404_for_missing_participant(api):
    # Arrange
    client, test_activities = api
    activity_name = "Chess Club"
    participants_before = list(test_activities[activity_name]["participants"])
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert test_activities[activity_name]["participants"] == participants_before


def test_unregister_returns_404_for_unknown_activity(api):
    # Arrange
    client, _ = api

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"