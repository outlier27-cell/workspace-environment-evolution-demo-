from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from environment_agent.agent import EnvironmentAgent
from environment_agent.diagnosis import diagnose_workspace
from environment_agent.manager_payload import build_manager_payload
from environment_agent.mock_store import MockEnvironmentStore
from environment_agent.quality import build_quality_report
from environment_agent.schemas import (
    AgentStepRequest,
    AgentStepResponse,
    EventLedgerView,
    SimulationRequest,
    SimulationResponse,
)
from environment_agent.validation import PlanValidationError


app = FastAPI(title="Workspace-Bench Environment Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
store = MockEnvironmentStore()
agent = EnvironmentAgent()


@app.exception_handler(PlanValidationError)
def plan_validation_exception_handler(
    _request: Request,
    exc: PlanValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "error": "plan_validation_failed",
                "validation_report": exc.report.model_dump(),
            }
        },
    )


def reset_mock_store_for_tests() -> None:
    global store
    store = MockEnvironmentStore()


class FromStoreRequest(BaseModel):
    user_id: str
    environment_id: str
    workspace_id: str
    seed: int = 0
    apply_to_mock_state: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/environment-agent/backend")
def get_backend():
    return agent.planner_backend_info


@app.get("/profiles/user/{user_id}")
def get_user_profile(user_id: str):
    return store.get_user_profile(user_id)


@app.get("/profiles/environment/{environment_id}")
def get_environment_profile(environment_id: str):
    return store.get_environment_profile(environment_id)


@app.get("/workspace/{workspace_id}/state")
def get_workspace_state(workspace_id: str):
    return store.get_workspace_state(workspace_id)


@app.get("/workspace/{workspace_id}/tasks/history")
def get_historical_tasks(workspace_id: str):
    return store.get_historical_tasks(workspace_id)


@app.get("/workspace/{workspace_id}/events", response_model=EventLedgerView)
def get_events(workspace_id: str) -> EventLedgerView:
    return EventLedgerView(workspace_id=workspace_id, event_ids=store.list_event_ids(workspace_id))


@app.get("/workspace/{workspace_id}/inspect")
def inspect_workspace(workspace_id: str):
    state = store.get_workspace_state(workspace_id)
    history = store.get_historical_tasks(workspace_id)
    event_ids = store.list_event_ids(workspace_id)
    return {
        "workspace_id": workspace_id,
        "snapshot_id": state.current_snapshot_id,
        "event_count": len(event_ids),
        "task_count": len(history.items),
        "artifact_count": len(state.artifacts),
        "dependency_edge_count": len(state.dependency_edges),
        "metrics": state.metrics,
    }


@app.post("/workspace/{workspace_id}/reset")
def reset_workspace(workspace_id: str):
    store.reset_workspace(workspace_id)
    return store.get_workspace_state(workspace_id)


@app.get("/workspace/{workspace_id}/quality")
def get_workspace_quality(workspace_id: str):
    state = store.get_workspace_state(workspace_id)
    report = build_quality_report(store.list_step_responses(workspace_id), state)
    history = store.get_historical_tasks(workspace_id)
    report["task_coverage"]["historical_task_count"] = len(history.items)
    return report


@app.post("/environment-agent/diagnose")
def diagnose(request: FromStoreRequest):
    user = store.get_user_profile(request.user_id)
    environment = store.get_environment_profile(request.environment_id)
    workspace = store.get_workspace_state(request.workspace_id)
    history = store.get_historical_tasks(request.workspace_id)
    return diagnose_workspace(user, environment, workspace, history)


@app.post("/environment-agent/step", response_model=AgentStepResponse)
def step(request: AgentStepRequest) -> AgentStepResponse:
    return agent.step(request)


@app.post("/environment-agent/step/from-store", response_model=AgentStepResponse)
def step_from_store(request: FromStoreRequest) -> AgentStepResponse:
    event_index = store.next_event_index(request.workspace_id)
    agent_request = AgentStepRequest(
        user_profile=store.get_user_profile(request.user_id),
        environment_profile=store.get_environment_profile(request.environment_id),
        workspace_state=store.get_workspace_state(request.workspace_id),
        historical_tasks=store.get_historical_tasks(request.workspace_id),
        seed=request.seed,
        event_index=event_index,
        apply_to_mock_state=request.apply_to_mock_state,
    )
    response = agent.step(agent_request)
    if response.updated_workspace_state is not None:
        store.set_workspace_state(response.updated_workspace_state)
        store.append_event(request.workspace_id, response.external_event)
        store.append_generated_tasks(request.workspace_id, response.task_opportunities)
        store.append_step_response(request.workspace_id, response)
    return response


@app.post("/environment-agent/manager-payload/from-store")
def manager_payload_from_store(request: FromStoreRequest):
    event_index = store.next_event_index(request.workspace_id)
    agent_request = AgentStepRequest(
        user_profile=store.get_user_profile(request.user_id),
        environment_profile=store.get_environment_profile(request.environment_id),
        workspace_state=store.get_workspace_state(request.workspace_id),
        historical_tasks=store.get_historical_tasks(request.workspace_id),
        seed=request.seed,
        event_index=event_index,
        apply_to_mock_state=request.apply_to_mock_state,
    )
    response = agent.step(agent_request)
    return build_manager_payload(response)


@app.post("/environment-agent/simulate", response_model=SimulationResponse)
def simulate(request: SimulationRequest) -> SimulationResponse:
    if request.reset_before_run:
        store.reset_workspace(request.workspace_id)

    responses: list[AgentStepResponse] = []
    for offset in range(request.steps):
        event_index = store.next_event_index(request.workspace_id)
        agent_request = AgentStepRequest(
            user_profile=store.get_user_profile(request.user_id),
            environment_profile=store.get_environment_profile(request.environment_id),
            workspace_state=store.get_workspace_state(request.workspace_id),
            historical_tasks=store.get_historical_tasks(request.workspace_id),
            seed=request.seed + offset,
            event_index=event_index,
            apply_to_mock_state=True,
        )
        response = agent.step(agent_request)
        assert response.updated_workspace_state is not None
        store.set_workspace_state(response.updated_workspace_state)
        store.append_event(request.workspace_id, response.external_event)
        store.append_generated_tasks(request.workspace_id, response.task_opportunities)
        store.append_step_response(request.workspace_id, response)
        responses.append(response)

    return SimulationResponse(
        workspace_id=request.workspace_id,
        steps=responses,
        final_workspace_state=store.get_workspace_state(request.workspace_id),
        event_ids=store.list_event_ids(request.workspace_id),
    )
