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


def test_event_ledger_endpoint_returns_404_for_unknown_workspace():
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/api/workspace/missing_workspace/events")

    assert response.status_code == 404
    assert response.json()["detail"] == {
        "error": "store_resource_not_found",
        "resource_type": "workspace",
        "resource_id": "missing_workspace",
    }


def test_simulate_endpoint_is_scoped_by_run_id():
    client = TestClient(app, raise_server_exceptions=False)
    payload = {
        "user_id": "user_logistics_001",
        "environment_id": "env_peak_logistics",
        "workspace_id": "workspace_logistics_demo",
        "seed": 7,
        "steps": 1,
        "reset_before_run": True,
    }

    first_response = client.post(
        "/api/environment-agent/simulate",
        json={**payload, "run_id": "run_a"},
    )
    run_a_state = client.get("/api/workspace/workspace_logistics_demo/inspect?run_id=run_a")
    run_b_state = client.get("/api/workspace/workspace_logistics_demo/inspect?run_id=run_b")

    assert first_response.status_code == 200
    assert run_a_state.json()["event_count"] == 1
    assert run_b_state.json()["event_count"] == 0


def test_run_id_rejects_unbounded_or_unsafe_values():
    client = TestClient(app, raise_server_exceptions=False)
    payload = {
        "user_id": "user_logistics_001",
        "environment_id": "env_peak_logistics",
        "workspace_id": "workspace_logistics_demo",
        "run_id": "bad run id " + ("x" * 80),
        "steps": 1,
    }

    body_response = client.post("/api/environment-agent/simulate", json=payload)
    query_response = client.get(
        "/api/workspace/workspace_logistics_demo/inspect",
        params={"run_id": payload["run_id"]},
    )

    assert body_response.status_code == 422
    assert query_response.status_code == 422


def test_run_scoped_mock_stores_evict_oldest_run_after_limit():
    client = TestClient(app, raise_server_exceptions=False)
    payload = {
        "user_id": "user_logistics_001",
        "environment_id": "env_peak_logistics",
        "workspace_id": "workspace_logistics_demo",
        "seed": 7,
        "steps": 1,
        "reset_before_run": True,
    }

    for index in range(33):
        response = client.post(
            "/api/environment-agent/simulate",
            json={**payload, "run_id": f"run_{index:02d}"},
        )
        assert response.status_code == 200

    first_run_state = client.get(
        "/api/workspace/workspace_logistics_demo/inspect",
        params={"run_id": "run_00"},
    )
    latest_run_state = client.get(
        "/api/workspace/workspace_logistics_demo/inspect",
        params={"run_id": "run_32"},
    )

    assert first_run_state.status_code == 200
    assert first_run_state.json()["event_count"] == 0
    assert latest_run_state.json()["event_count"] == 1


def test_manager_payload_apply_to_mock_state_persists_requested_evolution():
    client = TestClient(app, raise_server_exceptions=False)
    payload = {
        "user_id": "user_logistics_001",
        "environment_id": "env_peak_logistics",
        "workspace_id": "workspace_logistics_demo",
        "seed": 7,
        "apply_to_mock_state": True,
    }

    before = client.get("/api/workspace/workspace_logistics_demo/inspect").json()
    response = client.post("/api/environment-agent/manager-payload/from-store", json=payload)
    after = client.get("/api/workspace/workspace_logistics_demo/inspect").json()

    assert response.status_code == 200
    assert response.json()["validation_report"]["status"] == "passed"
    assert after["event_count"] == before["event_count"] + 1
    assert after["snapshot_id"] == "snap_0002"
