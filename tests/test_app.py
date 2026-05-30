import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def activity_signup_url(activity_name: str, email: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"


def activity_remove_url(activity_name: str, email: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/participants?email={quote(email, safe='')}"


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert expected_activity in body
    assert body[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = activity_signup_url(activity_name, email)

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = activity_signup_url(activity_name, email)

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_deletes_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = activity_remove_url(activity_name, email)

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    url = activity_remove_url(activity_name, email)

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_invalid_activity_returns_404_for_signup():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = activity_signup_url(activity_name, email)

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_invalid_activity_returns_404_for_remove():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = activity_remove_url(activity_name, email)

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
