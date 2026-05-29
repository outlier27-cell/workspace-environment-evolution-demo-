from __future__ import annotations

from environment_agent.diagnosis import diagnose_workspace
from environment_agent.interfaces import PlanningBackend
from environment_agent.planning_backend import MockRuleBasedPlanningBackend
from environment_agent.schemas import AgentStepRequest, AgentStepResponse, PlannerBackendInfo
from environment_agent.state_applier import apply_evolution_plan


class EnvironmentAgent:
    def __init__(self, planning_backend: PlanningBackend | None = None) -> None:
        self._planning_backend = planning_backend or MockRuleBasedPlanningBackend()

    @property
    def planner_backend_info(self) -> PlannerBackendInfo:
        return _backend_info(self._planning_backend)

    def step(self, request: AgentStepRequest) -> AgentStepResponse:
        diagnosis = diagnose_workspace(
            request.user_profile,
            request.environment_profile,
            request.workspace_state,
            request.historical_tasks,
        )
        planned_step = self._planning_backend.plan(request, diagnosis)
        updated_state = (
            apply_evolution_plan(
                request.workspace_state,
                planned_step.external_event,
                planned_step.evolution_plan,
            )
            if request.apply_to_mock_state
            else None
        )
        return AgentStepResponse(
            planner_backend=self.planner_backend_info,
            diagnosis=diagnosis,
            external_event=planned_step.external_event,
            constraints=planned_step.constraints,
            evolution_plan=planned_step.evolution_plan,
            task_opportunities=planned_step.task_opportunities,
            updated_workspace_state=updated_state,
        )


def _backend_info(backend: PlanningBackend) -> PlannerBackendInfo:
    info = backend.backend_info
    if isinstance(info, PlannerBackendInfo):
        return info
    return PlannerBackendInfo.model_validate(info)
