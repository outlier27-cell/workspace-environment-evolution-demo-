from __future__ import annotations

from environment_agent.schemas import ExternalEvent, WorkUnitMutation, WorkspaceState


def plan_workunit_mutations(
    workspace_state: WorkspaceState,
    event: ExternalEvent,
) -> list[WorkUnitMutation]:
    target_id = event.target_workunit_ids[0]
    existing = next(
        (workunit for workunit in workspace_state.active_work_units if workunit.workunit_id == target_id),
        None,
    )

    if existing is None:
        return [
            WorkUnitMutation(
                action="create",
                workunit_id=target_id,
                title="Environment-driven work unit",
                reason=event.trigger_reason,
                resulting_status="active",
                priority="high",
                related_entities=event.affected_entities,
                deadline="2026-04-21T17:00:00" if "deadline_pressure" in event.tags else None,
            )
        ]

    return [
        WorkUnitMutation(
            action="advance",
            workunit_id=existing.workunit_id,
            title=existing.title,
            reason=f"External event requires updating {existing.title}.",
            resulting_status="active",
            priority="high" if event.event_type in {"incident", "deadline"} else existing.priority,
            related_entities=list(dict.fromkeys(existing.related_entities + event.affected_entities)),
            deadline="2026-04-21T17:00:00" if "deadline_pressure" in event.tags else existing.deadline,
        )
    ]
