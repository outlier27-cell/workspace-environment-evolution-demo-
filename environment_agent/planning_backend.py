from __future__ import annotations

from environment_agent.artifact_planner import plan_artifacts_and_dependencies
from environment_agent.event_sampler import sample_event
from environment_agent.schemas import (
    AgentStepRequest,
    CoverageDiagnosis,
    PlannedEnvironmentStep,
    PlannerBackendInfo,
    WorkspaceEvolutionPlan,
)
from environment_agent.task_opportunity import generate_task_opportunities
from environment_agent.workunit_planner import plan_workunit_mutations


class MockRuleBasedPlanningBackend:
    backend_info = PlannerBackendInfo(
        name="mock_rule_based",
        generation_mode="mock_rule_based",
        version="0.1.0",
        is_mock=True,
        description=(
            "Deterministic demo backend backed by hand-written event, artifact, "
            "dependency, constraint, and task templates."
        ),
    )

    def plan(
        self,
        request: AgentStepRequest,
        diagnosis: CoverageDiagnosis,
    ) -> PlannedEnvironmentStep:
        event = sample_event(
            request.user_profile,
            request.environment_profile,
            request.workspace_state,
            request.historical_tasks,
            diagnosis,
            request.seed,
            request.event_index,
        )
        workunit_mutations = plan_workunit_mutations(request.workspace_state, event)
        artifact_plan, dependency_mutations, constraints = plan_artifacts_and_dependencies(
            request.workspace_state,
            event,
            workunit_mutations,
        )
        evolution_plan = WorkspaceEvolutionPlan(
            plan_id=f"plan_{event.event_id}",
            source_event_id=event.event_id,
            workunit_mutations=workunit_mutations,
            artifact_plan=artifact_plan,
            dependency_mutations=dependency_mutations,
            snapshot_policy="snapshot_after_plan_application",
            planner_notes=[
                "Environment Agent emits a plan; Workspace Agent materializes files.",
                "Task Agent should sample tasks from event, artifacts, dependency mutations, and constraints.",
            ],
        )
        opportunities = generate_task_opportunities(
            event,
            artifact_plan,
            dependency_mutations,
            constraints,
            request.historical_tasks,
        )
        return PlannedEnvironmentStep(
            external_event=event,
            constraints=constraints,
            evolution_plan=evolution_plan,
            task_opportunities=opportunities,
        )
