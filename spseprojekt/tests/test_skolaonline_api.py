import os

import pytest
from dotenv import load_dotenv

from bot.skolaonline import SkolaOnlineClient


load_dotenv()


def _client_from_env() -> SkolaOnlineClient:
    username = os.getenv("SKOLAONLINE_USERNAME")
    password = os.getenv("SKOLAONLINE_PASSWORD")

    if not username or not password:
        pytest.skip("SKOLAONLINE_USERNAME and SKOLAONLINE_PASSWORD are required")

    return SkolaOnlineClient(
        username=username,
        password=password,
        base_url=os.getenv(
            "SKOLAONLINE_BASE_URL",
            "https://aplikace.skolaonline.cz/solapi/api",
        ),
        client_id=os.getenv("SKOLAONLINE_CLIENT_ID", "test_client"),
        scope=os.getenv("SKOLAONLINE_SCOPE", "openid offline_access profile sol_api"),
        timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
    )


@pytest.mark.integration
def test_can_fetch_current_user_from_skolaonline_api():
    client = _client_from_env()

    token_data = client.login()
    user = client.get_user()

    assert token_data["access_token"]
    assert user["personID"]
    assert user["fullName"]


@pytest.mark.integration
def test_can_fetch_marks_from_skolaonline_api():
    if os.getenv("SKOLAONLINE_FETCH_MARKS") != "1":
        pytest.skip("set SKOLAONLINE_FETCH_MARKS=1 to fetch grades in this test")

    client = _client_from_env()
    user = client.get_user()
    marks = client.get_marks(user["personID"])

    assert "marks" in marks
    assert isinstance(marks["marks"], list)
