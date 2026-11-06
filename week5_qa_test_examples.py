"""
Week 5 QA task – reusable Python/pytest API test examples.

Install:
    python -m pip install pytest requests

Run:
    pytest -v week5_qa_test_examples.py

Configure the API base URL:
    Windows PowerShell:  $env:API_BASE_URL="http://localhost:8000"
    macOS/Linux:          export API_BASE_URL="http://localhost:8000"

IMPORTANT:
- These are illustrative examples for a REST API.
- Update endpoint paths, payload fields, status codes, and response keys
  to match your own project.
- The example assumes:
    POST /api/auth/login
    POST /api/records
  and a JSON response for login containing an access_token.
"""

import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
TIMEOUT_SECONDS = 10


@pytest.fixture
def api():
    """A reusable HTTP session for API tests."""
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


def test_login_with_valid_credentials(api):
    """
    TC-LOGIN-01:
    A registered, active user can authenticate successfully.
    Replace these sample credentials with a dedicated test account.
    """
    payload = {
        "email": os.getenv("TEST_USER_EMAIL", "qa.user@example.com"),
        "password": os.getenv("TEST_USER_PASSWORD", "ChangeMe123!"),
    }

    response = api.post(
        f"{BASE_URL}/api/auth/login",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("access_token"), "Expected an access_token in response"


def test_login_with_invalid_password_is_rejected(api):
    """
    TC-LOGIN-02:
    Incorrect credentials must not create an authenticated session.
    """
    payload = {
        "email": os.getenv("TEST_USER_EMAIL", "qa.user@example.com"),
        "password": "DefinitelyWrongPassword!",
    }

    response = api.post(
        f"{BASE_URL}/api/auth/login",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )

    assert response.status_code in (400, 401), response.text
    # Avoid asserting a specific error message because APIs may intentionally
    # use a generic message to avoid revealing whether an account exists.


def test_create_record_with_valid_data(api):
    """
    TC-RECORD-01:
    An authenticated, authorized user can create a valid record.
    Adapt the request body to your application's data model.
    """
    login_response = api.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": os.getenv("TEST_USER_EMAIL", "qa.user@example.com"),
            "password": os.getenv("TEST_USER_PASSWORD", "ChangeMe123!"),
        },
        timeout=TIMEOUT_SECONDS,
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json().get("access_token")
    assert token, "Login response did not contain access_token"

    payload = {
        "title": "QA sample record",
        "description": "Created by an automated integration test",
    }
    response = api.post(
        f"{BASE_URL}/api/records",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=TIMEOUT_SECONDS,
    )

    assert response.status_code in (200, 201), response.text
    created = response.json()
    assert created.get("id") is not None, "Created record should have an ID"
    assert created.get("title") == payload["title"]


@pytest.mark.parametrize(
    "payload",
    [
        {},  # Missing required fields
        {"title": ""},  # Empty required title
    ],
)
def test_create_record_with_invalid_data_is_rejected(api, payload):
    """
    Negative validation example.
    If the endpoint requires authentication before validation, obtain a token
    as in test_create_record_with_valid_data and pass it in the request.
    """
    response = api.post(
        f"{BASE_URL}/api/records",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )

    assert response.status_code in (400, 401, 403, 422), response.text


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", __file__]))
