from fastapi.testclient import TestClient
import pytest

from api.index import app
from environment_agent.api import reset_mock_store_for_tests


@pytest.fixture(autouse=True)
def fresh_mock_store():
    reset_mock_store_for_tests()


@pytest.mark.parametrize(
    ("override", "resource_type", "resource_id"),
    [
        ({"user_id": "missing_user"}, "user", "missing_user"),
        ({"environment_id": "missing_environment"}, "environment", "missing_environment"),
        ({"workspace_id": "missing_workspace"}, "workspace", "missing_workspace"),
    ],
)
def test_from_store_endpoint_returns_404_for_unknown_store_resource(
    override,
    resource_type,
    resource_id,
):
    client = TestClient(app, raise_server_exceptions=False)
    payload = {
        "user_id": "user_logistics_001",
        "environment_id": "env_peak_logistics",
        "workspace_id": "workspace_logistics_demo",
    }
    payload.update(override)

    response = client.post("/api/environment-agent/manager-payload/from-store", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == {
        "error": "store_resource_not_found",
        "resource_type": resource_type,
        "resource_id": resource_id,
    }


def test_simulate_endpoint_returns_404_for_unknown_workspace():
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/api/environment-agent/simulate",
        json={
            "user_id": "user_logistics_001",
            "environment_id": "env_peak_logistics",
            "workspace_id": "missing_workspace",
            "steps": 1,
            "reset_before_run": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == {
        "error": "store_resource_not_found",
        "resource_type": "workspace",
        "resource_id": "missing_workspace",
    }
