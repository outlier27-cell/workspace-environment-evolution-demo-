from __future__ import annotations

from environment_agent.schemas import (
    CoverageDiagnosis,
    EnvironmentProfile,
    EventType,
    HistoricalTasks,
    UserProfile,
    WorkspaceState,
)


def diagnose_workspace(
    user_profile: UserProfile,
    environment_profile: EnvironmentProfile,
    workspace_state: WorkspaceState,
    historical_tasks: HistoricalTasks,
) -> CoverageDiagnosis:
    metrics = workspace_state.metrics
    gaps: list[str] = []
    pressures: list[str] = []
    recommended: list[EventType] = []

    if int(metrics.get("active_work_units", len(workspace_state.active_work_units))) <= 1:
        gaps.append("low_dynamic_event_pressure")
        recommended.extend(["incident", "deadline"])

    if int(metrics.get("cross_workunit_edges", 0)) < 2:
        gaps.append("weak_cross_workunit_dependencies")
        recommended.extend(["collaboration", "resource_constraint"])

    if float(metrics.get("stale_file_ratio", 0.0)) < 0.15:
        gaps.append("low_stale_context_pressure")
        recommended.append("policy_change")

    if float(metrics.get("file_type_entropy", 0.0)) < 1.2:
        gaps.append("low_artifact_diversity")
        recommended.extend(["feedback", "discovery"])

    observed_task_types = {item.task_type for item in historical_tasks.items}
    if "stale_policy_detection" not in observed_task_types:
        gaps.append("missing_stale_policy_detection_tasks")
        recommended.append("policy_change")

    if environment_profile.incident_rate in {"high", "critical"}:
        pressures.append("environment_has_high_incident_rate")
        recommended.append("incident")

    if environment_profile.deadline_intensity in {"high", "critical"}:
        pressures.append("environment_has_high_deadline_intensity")
        recommended.append("deadline")

    if environment_profile.multi_tenant_pressure in {"medium", "high", "critical"}:
        pressures.append("environment_requires_collaboration_state")
        recommended.append("collaboration")

    if any("stale" in pattern.lower() for pattern in user_profile.workspace_behavior_patterns):
        pressures.append("user_behavior_supports_stale_context_decoys")
        recommended.append("policy_change")

    return CoverageDiagnosis(
        coverage_gaps=list(dict.fromkeys(gaps)),
        realism_pressures=list(dict.fromkeys(pressures)),
        recommended_event_types=list(dict.fromkeys(recommended)),
        explanation=(
            "Workspace lacks enough dynamic pressure, stale-context conflict, and cross-workunit "
            "dependencies for realistic Workspace-Bench 2.0 task generation."
        ),
    )
