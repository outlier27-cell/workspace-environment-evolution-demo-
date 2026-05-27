from __future__ import annotations

from environment_agent.event_templates import EVENT_ROTATION, LOGISTICS_EVENT_TEMPLATES, EventTemplate
from environment_agent.schemas import (
    CoverageDiagnosis,
    EnvironmentProfile,
    ExternalEvent,
    HistoricalTasks,
    UserProfile,
    WorkspaceState,
)


def _score_template(template: EventTemplate, diagnosis: CoverageDiagnosis) -> int:
    score = 0
    recommendation_names = set(diagnosis.recommended_event_types)
    for keyword in template.score_keywords:
        if keyword in recommendation_names:
            score += 3
        if keyword in diagnosis.coverage_gaps:
            score += 2
        if keyword in diagnosis.realism_pressures:
            score += 1
    return score


def _rotation_rank(template: EventTemplate) -> int:
    return EVENT_ROTATION.index(template.event_type)


def _rank_templates(diagnosis: CoverageDiagnosis) -> list[EventTemplate]:
    return sorted(
        LOGISTICS_EVENT_TEMPLATES,
        key=lambda template: (-_score_template(template, diagnosis), _rotation_rank(template)),
    )


def _choose_template(diagnosis: CoverageDiagnosis) -> EventTemplate:
    return _rank_templates(diagnosis)[0]


def _choose_template_for_event_index(
    diagnosis: CoverageDiagnosis,
    event_index: int,
) -> EventTemplate:
    ranked = _rank_templates(diagnosis)
    return ranked[(event_index - 1) % len(ranked)]


def sample_event(
    user_profile: UserProfile,
    environment_profile: EnvironmentProfile,
    workspace_state: WorkspaceState,
    historical_tasks: HistoricalTasks,
    diagnosis: CoverageDiagnosis,
    seed: int,
    event_index: int | None = None,
) -> ExternalEvent:
    _ = (user_profile, environment_profile, historical_tasks)
    template = (
        _choose_template_for_event_index(diagnosis, event_index)
        if event_index is not None
        else _choose_template(diagnosis)
    )
    target_workunit_id = (
        workspace_state.active_work_units[0].workunit_id
        if workspace_state.active_work_units
        else f"wu_{workspace_state.workspace_id}_new"
    )

    event_id = (
        f"evt_{workspace_state.workspace_id}_{template.event_type}_{event_index:04d}_{seed:04d}"
        if event_index is not None
        else f"evt_{workspace_state.workspace_id}_{template.event_type}_{seed:04d}"
    )

    return ExternalEvent(
        event_id=event_id,
        event_type=template.event_type,
        timestamp="2026-04-21T10:30:00",
        source_actor=template.source_actor,
        target_workunit_ids=[target_workunit_id],
        trigger_reason=template.trigger_reason,
        expected_workspace_effects=list(template.expected_workspace_effects),
        affected_entities=list(template.affected_entities),
        difficulty_effects=template.difficulty_effects,  # type: ignore[arg-type]
        tags=list(template.tags),
    )
