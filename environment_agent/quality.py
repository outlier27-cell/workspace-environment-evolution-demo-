from __future__ import annotations

from collections import Counter
from typing import Any

from environment_agent.schemas import AgentStepResponse, WorkspaceState


def _as_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def build_quality_report(
    steps: list[AgentStepResponse | dict[str, Any]],
    final_workspace_state: WorkspaceState | dict[str, Any],
) -> dict[str, Any]:
    step_dicts = [_as_dict(step) for step in steps]
    workspace = _as_dict(final_workspace_state)

    event_types = [step["external_event"]["event_type"] for step in step_dicts]
    event_type_counts = dict(Counter(event_types))
    opportunities = [
        opportunity
        for step in step_dicts
        for opportunity in step.get("task_opportunities", [])
    ]
    capability_tags = sorted(
        {
            tag
            for opportunity in opportunities
            for tag in opportunity.get("capability_tags", [])
        }
    )
    negative_rubrics = [
        hint
        for opportunity in opportunities
        for hint in opportunity.get("negative_rubric_hints", [])
    ]
    validation_hints = [
        hint
        for opportunity in opportunities
        for hint in opportunity.get("validation_hints", [])
    ]
    artifacts = workspace.get("artifacts", [])
    dependency_edges = workspace.get("dependency_edges", [])
    work_units = workspace.get("active_work_units", [])

    return {
        "event_type_coverage": {
            "event_count": len(event_types),
            "unique_event_types": len(set(event_types)),
            "event_type_counts": event_type_counts,
            "coverage_ratio": round(len(set(event_types)) / 8, 3),
        },
        "task_coverage": {
            "task_opportunity_count": len(opportunities),
            "task_types": sorted({opportunity["task_type"] for opportunity in opportunities}),
            "capability_tags": capability_tags,
        },
        "workspace_health": {
            "snapshot_id": workspace.get("current_snapshot_id"),
            "artifact_count": len(artifacts),
            "dependency_edge_count": len(dependency_edges),
            "active_workunit_count": len(
                [workunit for workunit in work_units if workunit.get("status") == "active"]
            ),
            "stale_file_ratio": workspace.get("metrics", {}).get("stale_file_ratio", 0.0),
        },
        "validation_readiness": {
            "has_validation_hints": bool(validation_hints),
            "has_negative_rubrics": bool(negative_rubrics),
            "required_artifact_links": all(
                opportunity.get("required_artifact_ids") for opportunity in opportunities
            )
            if opportunities
            else False,
            "ready": bool(validation_hints and negative_rubrics and opportunities),
        },
    }
