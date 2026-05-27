from __future__ import annotations

from environment_agent.schemas import (
    ArtifactPlanItem,
    DependencyMutation,
    EnvironmentConstraint,
    ExternalEvent,
    WorkUnitMutation,
    WorkspaceState,
)


def _event_suffix(event: ExternalEvent) -> str:
    parts = event.event_id.rsplit("_", 2)
    if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
        return parts[1]
    return "0421"


def _incident_ids(suffix: str) -> dict[str, str]:
    if suffix == "0421":
        return {
            "complaint": "art_customer_complaint_0421",
            "delay_notice": "art_supplier_delay_notice_0421",
            "exception_sheet": "art_april_exception_shipments",
            "latest_policy": "art_sla_policy_april_update",
            "revised_report": "art_weekly_report_revised_0421",
            "response_draft": "art_customer_response_draft_0421",
        }
    return {
        "complaint": f"art_customer_complaint_{suffix}",
        "delay_notice": f"art_supplier_delay_notice_{suffix}",
        "exception_sheet": f"art_exception_shipments_{suffix}",
        "latest_policy": f"art_sla_policy_update_{suffix}",
        "revised_report": f"art_weekly_report_revised_{suffix}",
        "response_draft": f"art_customer_response_draft_{suffix}",
    }


def _target_workunit(workunit_mutations: list[WorkUnitMutation]) -> str:
    return workunit_mutations[0].workunit_id


def plan_artifacts_and_dependencies(
    workspace_state: WorkspaceState,
    event: ExternalEvent,
    workunit_mutations: list[WorkUnitMutation],
) -> tuple[list[ArtifactPlanItem], list[DependencyMutation], list[EnvironmentConstraint]]:
    _ = workspace_state
    workunit_id = _target_workunit(workunit_mutations)

    if event.event_type == "policy_change":
        return _plan_policy_artifacts(event, workunit_id)
    if event.event_type != "incident":
        return _plan_generic_event_artifacts(event, workunit_id)

    suffix = _event_suffix(event)
    ids = _incident_ids(suffix)
    complaint_id = ids["complaint"]
    delay_notice_id = ids["delay_notice"]
    exception_sheet_id = ids["exception_sheet"]
    latest_policy_id = ids["latest_policy"]
    revised_report_id = ids["revised_report"]
    response_draft_id = ids["response_draft"]

    artifacts = [
        ArtifactPlanItem(
            action="create",
            artifact_id=complaint_id,
            path=f"/emails/customer_complaint_{suffix}.eml",
            artifact_type="eml",
            role="customer_complaint",
            workunit_id=workunit_id,
            reason="Customer complaint creates the urgent external pressure.",
            content_brief="Email from customer X requesting explanation for delayed shipments by 17:00.",
        ),
        ArtifactPlanItem(
            action="create",
            artifact_id=delay_notice_id,
            path=f"/emails/supplier_delay_notice_{suffix}.eml",
            artifact_type="eml",
            role="supplier_delay_notice",
            workunit_id=workunit_id,
            reason="Carrier notice explains the operational cause.",
            content_brief="Carrier A reports customs clearance delays affecting 17 shipments.",
        ),
        ArtifactPlanItem(
            action="create",
            artifact_id=exception_sheet_id,
            path=f"/orders/exception_shipments_{suffix}.xlsx",
            artifact_type="xlsx",
            role="exception_shipment_table",
            workunit_id=workunit_id,
            reason="The incident requires a concrete affected-order table.",
            depends_on=[delay_notice_id],
            content_brief="Spreadsheet listing 17 delayed shipment IDs, carrier, customer, delay reason, and SLA status.",
        ),
        ArtifactPlanItem(
            action="create",
            artifact_id=latest_policy_id,
            path=f"/policies/sla_policy_update_{suffix}.pdf",
            artifact_type="pdf",
            role="latest_sla_policy",
            workunit_id=workunit_id,
            reason="New SLA policy makes old Q1 policy a decoy.",
            content_brief="April SLA update defining compensation and response deadlines for delayed shipments.",
        ),
        ArtifactPlanItem(
            action="mark_stale",
            artifact_id="art_sla_policy_q1",
            path="/policies/sla_policy_q1.pdf",
            artifact_type="pdf",
            role="old_policy_decoy",
            workunit_id=workunit_id,
            reason="Q1 SLA should not be used after April update.",
            content_brief="Existing Q1 SLA remains in workspace but is stale for current incident.",
            stale_of=latest_policy_id,
        ),
        ArtifactPlanItem(
            action="update",
            artifact_id=revised_report_id,
            path=f"/reports/weekly_ops_report_revised_{suffix}.docx",
            artifact_type="docx",
            role="revised_weekly_report",
            workunit_id=workunit_id,
            reason="Weekly report must include incident analysis and SLA impact.",
            depends_on=[
                complaint_id,
                exception_sheet_id,
                latest_policy_id,
            ],
            content_brief="Revised weekly report section summarizing 17 delayed shipments and mitigation plan.",
        ),
        ArtifactPlanItem(
            action="create",
            artifact_id=response_draft_id,
            path=f"/drafts/customer_response_draft_{suffix}.docx",
            artifact_type="docx",
            role="customer_response_draft",
            workunit_id=workunit_id,
            reason="Customer-facing response is the deliverable triggered by the incident.",
            depends_on=[
                complaint_id,
                delay_notice_id,
                latest_policy_id,
                revised_report_id,
            ],
            content_brief="Draft response to customer X explaining cause, affected shipments, SLA handling, and next steps.",
        ),
    ]

    dependencies = [
        DependencyMutation(
            action="add",
            source_artifact_id=latest_policy_id,
            target_artifact_id="art_sla_policy_q1",
            relation="supersedes",
            reason="April SLA policy overrides Q1 SLA policy.",
        ),
        DependencyMutation(
            action="add",
            source_artifact_id=complaint_id,
            target_artifact_id=response_draft_id,
            relation="requires_response",
            reason="Customer complaint drives the response draft.",
        ),
        DependencyMutation(
            action="add",
            source_artifact_id=exception_sheet_id,
            target_artifact_id=revised_report_id,
            relation="summarized_by",
            reason="Exception shipment table must be summarized in revised weekly report.",
        ),
        DependencyMutation(
            action="add",
            source_artifact_id=revised_report_id,
            target_artifact_id=response_draft_id,
            relation="supports",
            reason="Customer response uses the revised internal analysis.",
        ),
    ]

    constraints = [
        EnvironmentConstraint(
            constraint_id="rule_april_sla_overrides_q1",
            scope="shipping_policy_documents",
            description="The April SLA policy overrides all Q1 SLA drafts for delayed shipment handling.",
            applies_to_event_id=event.event_id,
            required_behavior=f"Use {latest_policy_id} instead of art_sla_policy_q1.",
            violation_modes=[
                "uses stale Q1 SLA policy",
                "ignores 17:00 customer response deadline",
                "updates weekly report without exception shipment table",
            ],
        )
    ]

    return artifacts, dependencies, constraints


def _plan_policy_artifacts(
    event: ExternalEvent,
    workunit_id: str,
) -> tuple[list[ArtifactPlanItem], list[DependencyMutation], list[EnvironmentConstraint]]:
    suffix = _event_suffix(event)
    latest_policy_id = (
        "art_sla_policy_april_update"
        if suffix == "0421"
        else f"art_sla_policy_update_{suffix}"
    )
    artifacts = [
        ArtifactPlanItem(
            action="create",
            artifact_id=latest_policy_id,
            path=f"/policies/sla_policy_update_{suffix}.pdf",
            artifact_type="pdf",
            role="latest_sla_policy",
            workunit_id=workunit_id,
            reason=event.trigger_reason,
            content_brief="April SLA update superseding Q1 SLA draft.",
        ),
        ArtifactPlanItem(
            action="mark_stale",
            artifact_id="art_sla_policy_q1",
            path="/policies/sla_policy_q1.pdf",
            artifact_type="pdf",
            role="old_policy_decoy",
            workunit_id=workunit_id,
            reason="Q1 policy is retained as stale context.",
            content_brief="Q1 SLA is stale after April policy update.",
            stale_of=latest_policy_id,
        ),
    ]
    dependencies = [
        DependencyMutation(
            action="add",
            source_artifact_id=latest_policy_id,
            target_artifact_id="art_sla_policy_q1",
            relation="supersedes",
            reason="New policy overrides old policy.",
        )
    ]
    constraints = [
        EnvironmentConstraint(
            constraint_id="rule_latest_policy_required",
            scope="policy_documents",
            description="Latest policy must be used for current tasks.",
            applies_to_event_id=event.event_id,
            required_behavior=f"Use {latest_policy_id} and treat older policies as stale context.",
            violation_modes=["uses stale policy"],
        )
    ]
    return artifacts, dependencies, constraints


def _plan_generic_event_artifacts(
    event: ExternalEvent,
    workunit_id: str,
) -> tuple[list[ArtifactPlanItem], list[DependencyMutation], list[EnvironmentConstraint]]:
    event_slug = event.event_type
    event_suffix = _event_suffix(event)
    base_id = f"{event_slug}_{event_suffix}"
    base_dir = {
        "collaboration": "meetings",
        "resource_constraint": "planning",
        "feedback": "feedback",
        "deadline": "todos",
        "discovery": "research",
        "drift": "strategy",
    }.get(event.event_type, "events")

    artifacts = [
        ArtifactPlanItem(
            action="create",
            artifact_id=f"art_{base_id}_source",
            path=f"/{base_dir}/{event_slug}_source_{event_suffix}.md",
            artifact_type="md",
            role=f"{event_slug}_source_record",
            workunit_id=workunit_id,
            reason=f"Record the external {event.event_type} trigger.",
            content_brief=event.trigger_reason,
        ),
        ArtifactPlanItem(
            action="create",
            artifact_id=f"art_{base_id}_analysis",
            path=f"/{base_dir}/{event_slug}_analysis_{event_suffix}.docx",
            artifact_type="docx",
            role=f"{event_slug}_analysis",
            workunit_id=workunit_id,
            reason=f"Analyze how the {event.event_type} changes current work.",
            depends_on=[f"art_{base_id}_source"],
            content_brief=f"Analysis of affected entities: {', '.join(event.affected_entities)}.",
        ),
        ArtifactPlanItem(
            action="update",
            artifact_id=f"art_{base_id}_action_plan",
            path=f"/{base_dir}/{event_slug}_action_plan_{event_suffix}.xlsx",
            artifact_type="xlsx",
            role=f"{event_slug}_action_plan",
            workunit_id=workunit_id,
            reason=f"Translate {event.event_type} into trackable workspace actions.",
            depends_on=[f"art_{base_id}_source", f"art_{base_id}_analysis"],
            content_brief="Structured action plan with owners, deadline, dependency, and validation columns.",
        ),
    ]

    dependencies = [
        DependencyMutation(
            action="add",
            source_artifact_id=f"art_{base_id}_source",
            target_artifact_id=f"art_{base_id}_analysis",
            relation="explained_by",
            reason=f"The source record explains the {event.event_type} analysis.",
        ),
        DependencyMutation(
            action="add",
            source_artifact_id=f"art_{base_id}_analysis",
            target_artifact_id=f"art_{base_id}_action_plan",
            relation="operationalizes",
            reason=f"The action plan operationalizes the {event.event_type} analysis.",
        ),
    ]

    constraints = [
        EnvironmentConstraint(
            constraint_id=f"rule_{base_id}_must_be_reflected",
            scope=f"{event.event_type}_artifacts",
            description=f"The {event.event_type} event must be reflected in downstream plans and tasks.",
            applies_to_event_id=event.event_id,
            required_behavior=f"Use the {event.event_type} source and analysis before updating action plans.",
            violation_modes=[
                f"ignores {event.event_type} source record",
                "updates action plan without dependency evidence",
            ],
        )
    ]

    return artifacts, dependencies, constraints
