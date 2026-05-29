from __future__ import annotations

from typing import Protocol

from environment_agent.schemas import (
    AgentStepResponse,
    AgentStepRequest,
    CoverageDiagnosis,
    EnvironmentProfile,
    ExternalEvent,
    HistoricalTasks,
    PlannedEnvironmentStep,
    PlannerBackendInfo,
    UserProfile,
    WorkspaceEvolutionPlan,
    WorkspaceState,
)


class ProfileProvider(Protocol):
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Return the user profile used by Environment Agent."""

    def get_environment_profile(self, environment_id: str) -> EnvironmentProfile:
        """Return the environment profile used by Environment Agent."""


class WorkspaceStateProvider(Protocol):
    def get_workspace_state(self, workspace_id: str) -> WorkspaceState:
        """Return the current workspace state summary."""


class HistoricalTaskProvider(Protocol):
    def get_historical_tasks(self, workspace_id: str) -> HistoricalTasks:
        """Return historical generated or evaluated tasks for this workspace."""


class EventLedger(Protocol):
    def list_event_ids(self, workspace_id: str) -> list[str]:
        """Return event ids already injected into the workspace."""

    def append_event(self, workspace_id: str, event: ExternalEvent) -> None:
        """Record an event in the event ledger."""


class EvolutionSink(Protocol):
    def apply_plan(
        self,
        workspace_state: WorkspaceState,
        evolution_plan: WorkspaceEvolutionPlan,
        response: AgentStepResponse,
    ) -> WorkspaceState:
        """Apply a generated evolution plan to a backing state store."""


class PlanningBackend(Protocol):
    backend_info: PlannerBackendInfo | dict

    def plan(
        self,
        request: AgentStepRequest,
        diagnosis: CoverageDiagnosis,
    ) -> PlannedEnvironmentStep:
        """Generate one environment event, evolution plan, constraints, and task opportunities."""
