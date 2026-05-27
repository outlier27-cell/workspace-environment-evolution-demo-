from __future__ import annotations

from dataclasses import dataclass

from environment_agent.schemas import EventType


@dataclass(frozen=True)
class EventTemplate:
    event_type: EventType
    source_actor: str
    trigger_reason: str
    expected_workspace_effects: tuple[str, ...]
    affected_entities: tuple[str, ...]
    difficulty_effects: dict[str, str]
    tags: tuple[str, ...]
    score_keywords: tuple[str, ...]


LOGISTICS_EVENT_TEMPLATES: tuple[EventTemplate, ...] = (
    EventTemplate(
        event_type="incident",
        source_actor="carrier_A",
        trigger_reason=(
            "Carrier A reports customs clearance delays causing 17 delayed shipments; "
            "customer X requests an explanation by 17:00 today."
        ),
        expected_workspace_effects=(
            "create customer complaint email",
            "create supplier delay notice email",
            "create April exception shipment sheet",
            "add April SLA update and mark Q1 SLA as stale context",
            "revise weekly operations report",
            "create customer response draft",
        ),
        affected_entities=("carrier_A", "customer_X", "shipment_batch_0421", "sla_policy_april"),
        difficulty_effects={
            "retrieval": "medium",
            "temporal_reasoning": "high",
            "stale_context_pressure": "high",
            "cross_file_update": "high",
        },
        tags=("stale_policy_detection", "cross_file_update", "deadline_pressure"),
        score_keywords=("incident", "policy_change", "deadline"),
    ),
    EventTemplate(
        event_type="collaboration",
        source_actor="customer_support_lead",
        trigger_reason=(
            "Customer support adds a private complaint log that conflicts with the public carrier summary."
        ),
        expected_workspace_effects=(
            "create restricted complaint log",
            "create shared meeting notes",
            "update response ownership table",
        ),
        affected_entities=("customer_support", "finance", "carrier_A"),
        difficulty_effects={
            "retrieval": "medium",
            "access_control_reasoning": "high",
            "multi_actor_synthesis": "high",
        },
        tags=("multi_tenant", "permission_conflict", "cross_workunit_dependency"),
        score_keywords=("collaboration", "resource_constraint"),
    ),
    EventTemplate(
        event_type="resource_constraint",
        source_actor="finance_ops",
        trigger_reason=(
            "Finance temporarily freezes premium carrier spending, forcing the logistics team "
            "to reroute delayed shipments with limited budget."
        ),
        expected_workspace_effects=(
            "create budget freeze notice",
            "create alternative carrier comparison sheet",
            "update mitigation plan",
            "create risk note for customer support",
        ),
        affected_entities=("finance_ops", "carrier_B", "customer_X", "premium_shipping_budget"),
        difficulty_effects={
            "constraint_reasoning": "high",
            "planning": "high",
            "tradeoff_analysis": "medium",
        },
        tags=("resource_constraint", "planning_under_constraints", "cross_workunit_dependency"),
        score_keywords=("resource_constraint", "collaboration"),
    ),
    EventTemplate(
        event_type="policy_change",
        source_actor="operations_policy_team",
        trigger_reason="April SLA policy overrides the Q1 SLA draft for delayed shipment compensation.",
        expected_workspace_effects=(
            "create April SLA policy document",
            "mark Q1 SLA as stale",
            "update policy index",
            "create compliance note",
        ),
        affected_entities=("sla_policy_q1", "sla_policy_april", "customer_X"),
        difficulty_effects={
            "version_selection": "high",
            "stale_context_pressure": "high",
            "rule_following": "medium",
        },
        tags=("stale_policy_detection", "version_selection"),
        score_keywords=("policy_change", "stale"),
    ),
    EventTemplate(
        event_type="feedback",
        source_actor="operations_director",
        trigger_reason="The operations director requests clearer root-cause analysis and customer-facing wording.",
        expected_workspace_effects=(
            "create annotated report feedback",
            "create revision checklist",
            "update customer response draft",
        ),
        affected_entities=("operations_director", "customer_X", "weekly_ops_report"),
        difficulty_effects={
            "feedback_integration": "high",
            "artifact_update": "medium",
            "tone_control": "medium",
        },
        tags=("feedback_integration", "artifact_update"),
        score_keywords=("feedback", "artifact"),
    ),
    EventTemplate(
        event_type="deadline",
        source_actor="customer_success",
        trigger_reason="Customer success moves the response deadline forward by two hours for an executive escalation.",
        expected_workspace_effects=(
            "create escalation note",
            "create deadline checklist",
            "update response draft priority",
        ),
        affected_entities=("customer_success", "executive_escalation", "customer_X"),
        difficulty_effects={
            "temporal_reasoning": "high",
            "prioritization": "high",
            "retrieval": "medium",
        },
        tags=("deadline_pressure", "prioritization"),
        score_keywords=("deadline", "temporal"),
    ),
    EventTemplate(
        event_type="discovery",
        source_actor="customs_broker",
        trigger_reason="A customs broker publishes a new clearance bulletin that changes the interpretation of delay causes.",
        expected_workspace_effects=(
            "create customs bulletin",
            "create evidence comparison note",
            "update exception shipment annotations",
        ),
        affected_entities=("customs_broker", "shipment_batch_0421", "carrier_A"),
        difficulty_effects={
            "information_update": "high",
            "evidence_comparison": "medium",
            "retrieval": "medium",
        },
        tags=("discovery", "information_update"),
        score_keywords=("discovery", "retrieval"),
    ),
    EventTemplate(
        event_type="drift",
        source_actor="regional_ops_team",
        trigger_reason="The regional operations team shifts from incident response to long-term carrier diversification.",
        expected_workspace_effects=(
            "archive old mitigation plan",
            "create carrier diversification brief",
            "create transition note",
        ),
        affected_entities=("regional_ops_team", "carrier_A", "carrier_B", "carrier_C"),
        difficulty_effects={
            "long_term_memory": "high",
            "plan_revision": "high",
            "stale_context_pressure": "medium",
        },
        tags=("drift", "long_term_context_revision"),
        score_keywords=("drift", "planning"),
    ),
)


EVENT_ROTATION: tuple[EventType, ...] = (
    "incident",
    "policy_change",
    "collaboration",
    "resource_constraint",
    "feedback",
    "deadline",
    "discovery",
    "drift",
)
