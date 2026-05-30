from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


RiskLevel = Literal["low", "medium", "high", "critical"]
EventType = Literal[
    "deadline",
    "incident",
    "feedback",
    "policy_change",
    "collaboration",
    "resource_constraint",
    "discovery",
    "drift",
]
WorkUnitStatus = Literal["active", "paused", "closed", "stale"]
WorkUnitAction = Literal["create", "advance", "split", "merge", "pause", "close"]
ArtifactAction = Literal["create", "update", "mark_stale", "archive", "reference"]
DependencyAction = Literal["add", "remove", "mark_stale"]
GenerationMode = Literal["mock_rule_based", "llm", "external_provider"]
RUN_ID_PATTERN = r"^[A-Za-z0-9_.-]{1,48}$"


class UserProfile(BaseModel):
    user_id: str
    primary_role: str
    primary_domain: str
    core_work_activities: list[str] = Field(min_length=1)
    recurring_deliverables: list[str] = Field(min_length=1)
    deadline_behavior: dict[str, Any] = Field(default_factory=dict)
    workspace_behavior_patterns: list[str] = Field(default_factory=list)
    secondary_roles: list[str] = Field(default_factory=list)
    long_term_goals: list[str] = Field(default_factory=list)
    short_term_goals: list[str] = Field(default_factory=list)


class EnvironmentProfile(BaseModel):
    environment_id: str
    organization_type: str
    industry_domain: str
    collaboration_topology: str
    external_event_frequency: RiskLevel | Literal["rare", "frequent"]
    deadline_intensity: RiskLevel
    incident_rate: RiskLevel
    policy_volatility: RiskLevel
    resource_constraint_level: RiskLevel
    seasonality: str
    multi_tenant_pressure: RiskLevel


class ArtifactState(BaseModel):
    artifact_id: str
    path: str
    artifact_type: str
    role: str
    workunit_id: str
    version: str = "v1"
    is_stale: bool = False
    created_by_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DependencyEdge(BaseModel):
    source_artifact_id: str
    target_artifact_id: str
    relation: str
    reason: str
    is_active: bool = True


class WorkUnitState(BaseModel):
    workunit_id: str
    title: str
    status: WorkUnitStatus
    priority: RiskLevel
    related_entities: list[str] = Field(default_factory=list)
    deadline: str | None = None
    source_event_ids: list[str] = Field(default_factory=list)


class WorkspaceState(BaseModel):
    workspace_id: str
    current_snapshot_id: str
    active_work_units: list[WorkUnitState] = Field(default_factory=list)
    artifacts: list[ArtifactState] = Field(default_factory=list)
    dependency_edges: list[DependencyEdge] = Field(default_factory=list)
    event_log: list[str] = Field(default_factory=list)
    metrics: dict[str, float | int] = Field(default_factory=dict)


class TaskHistoryItem(BaseModel):
    task_id: str
    task_type: str
    capability_tags: list[str] = Field(default_factory=list)
    source_event_ids: list[str] = Field(default_factory=list)


class HistoricalTasks(BaseModel):
    workspace_id: str
    items: list[TaskHistoryItem] = Field(default_factory=list)


class EventLedgerView(BaseModel):
    workspace_id: str
    event_ids: list[str]


class CoverageDiagnosis(BaseModel):
    coverage_gaps: list[str]
    realism_pressures: list[str]
    recommended_event_types: list[EventType]
    explanation: str


class ExternalEvent(BaseModel):
    event_id: str
    event_type: EventType
    timestamp: str
    source_actor: str
    target_workunit_ids: list[str]
    trigger_reason: str
    expected_workspace_effects: list[str]
    affected_entities: list[str]
    difficulty_effects: dict[str, RiskLevel]
    tags: list[str] = Field(default_factory=list)

    @field_validator("expected_workspace_effects")
    @classmethod
    def expected_effects_must_not_be_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("external events must describe workspace effects")
        return value


class EnvironmentConstraint(BaseModel):
    constraint_id: str
    scope: str
    description: str
    applies_to_event_id: str
    required_behavior: str
    violation_modes: list[str] = Field(default_factory=list)


class WorkUnitMutation(BaseModel):
    action: WorkUnitAction
    workunit_id: str
    title: str
    reason: str
    resulting_status: WorkUnitStatus
    priority: RiskLevel
    related_entities: list[str] = Field(default_factory=list)
    deadline: str | None = None


class ArtifactPlanItem(BaseModel):
    action: ArtifactAction
    artifact_id: str
    path: str
    artifact_type: str
    role: str
    workunit_id: str
    reason: str
    depends_on: list[str] = Field(default_factory=list)
    content_brief: str
    stale_of: str | None = None


class DependencyMutation(BaseModel):
    action: DependencyAction
    source_artifact_id: str
    target_artifact_id: str
    relation: str
    reason: str


class WorkspaceEvolutionPlan(BaseModel):
    plan_id: str
    source_event_id: str
    workunit_mutations: list[WorkUnitMutation]
    artifact_plan: list[ArtifactPlanItem]
    dependency_mutations: list[DependencyMutation]
    snapshot_policy: str
    planner_notes: list[str] = Field(default_factory=list)


class TaskOpportunity(BaseModel):
    opportunity_id: str
    source_event_id: str
    task_type: str
    instruction: str
    required_artifact_ids: list[str]
    capability_tags: list[str]
    validation_hints: list[str]
    negative_rubric_hints: list[str] = Field(default_factory=list)


class PlannerBackendInfo(BaseModel):
    name: str
    generation_mode: GenerationMode
    version: str = "0.1.0"
    is_mock: bool = False
    description: str


class PlannedEnvironmentStep(BaseModel):
    external_event: ExternalEvent
    constraints: list[EnvironmentConstraint]
    evolution_plan: WorkspaceEvolutionPlan
    task_opportunities: list[TaskOpportunity]


class PlanValidationReport(BaseModel):
    status: Literal["passed", "failed"]
    checks: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AgentStepRequest(BaseModel):
    user_profile: UserProfile
    environment_profile: EnvironmentProfile
    workspace_state: WorkspaceState
    historical_tasks: HistoricalTasks
    seed: int = 0
    event_index: int | None = None
    apply_to_mock_state: bool = False


class AgentStepResponse(BaseModel):
    planner_backend: PlannerBackendInfo
    validation_report: PlanValidationReport
    diagnosis: CoverageDiagnosis
    external_event: ExternalEvent
    constraints: list[EnvironmentConstraint]
    evolution_plan: WorkspaceEvolutionPlan
    task_opportunities: list[TaskOpportunity]
    updated_workspace_state: WorkspaceState | None = None


class SimulationRequest(BaseModel):
    user_id: str
    environment_id: str
    workspace_id: str
    run_id: str = Field(default="default", min_length=1, max_length=48, pattern=RUN_ID_PATTERN)
    seed: int = 0
    steps: int = Field(default=1, ge=1, le=50)
    reset_before_run: bool = True


class SimulationResponse(BaseModel):
    workspace_id: str
    steps: list[AgentStepResponse]
    final_workspace_state: WorkspaceState
    event_ids: list[str]
