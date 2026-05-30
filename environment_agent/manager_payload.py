from __future__ import annotations

from environment_agent.schemas import AgentStepResponse


def build_manager_payload(response: AgentStepResponse) -> dict:
    return {
        "target_agent": "generation_manager",
        "planner_backend": response.planner_backend.model_dump(),
        "validation_report": response.validation_report.model_dump(),
        "source_event": response.external_event.model_dump(),
        "constraints": [constraint.model_dump() for constraint in response.constraints],
        "workspace_agent_queue": [
            {
                "action": item.action,
                "artifact_id": item.artifact_id,
                "path": item.path,
                "artifact_type": item.artifact_type,
                "role": item.role,
                "workunit_id": item.workunit_id,
                "depends_on": item.depends_on,
                "content_brief": item.content_brief,
            }
            for item in response.evolution_plan.artifact_plan
        ],
        "task_agent_queue": [
            {
                "opportunity_id": opportunity.opportunity_id,
                "task_type": opportunity.task_type,
                "instruction": opportunity.instruction,
                "required_artifact_ids": opportunity.required_artifact_ids,
                "capability_tags": opportunity.capability_tags,
                "validation_hints": opportunity.validation_hints,
                "negative_rubric_hints": opportunity.negative_rubric_hints,
            }
            for opportunity in response.task_opportunities
        ],
        "kg_update_queue": [
            mutation.model_dump()
            for mutation in response.evolution_plan.dependency_mutations
        ],
        "workunit_update_queue": [
            mutation.model_dump()
            for mutation in response.evolution_plan.workunit_mutations
        ],
        "snapshot_policy": response.evolution_plan.snapshot_policy,
    }
