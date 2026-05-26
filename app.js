const scenarios = {
  logistics: {
    persona: "Logistics Manager",
    tag: "operations / multi-file reasoning",
    summary:
      "负责跨境电商物流异常处理、承运商评估和周报交付。常用 Excel、邮件、Word 报告，deadline 前会产生多个草稿和临时版本。",
    env: {
      deadline: "High",
      incident: "High",
      policy: "Medium",
    },
    coverage: [
      "缺少跨 snapshot 的事件链",
      "缺少新旧 SLA 政策冲突",
      "缺少需要修改已有交付物的任务",
    ],
    event: {
      type: "incident + policy change",
      title: "承运商延误触发客户投诉",
      description:
        "4 月新 SLA 政策生效后，承运商 A 因清关延误导致 17 个订单超时，客户要求当天 17:00 前给出解释。",
      source: "supplier + customer",
      workunit: "WU-Q2-Delivery-Exception-Review",
      effects: [
        "create supplier email",
        "update shipment exception sheet",
        "revise weekly report",
        "create customer response draft",
      ],
      difficulty: "retrieval=medium, temporal=high, stale_context=high",
    },
    workunit: {
      name: "Q2 物流异常复盘",
      status: "active -> urgent -> resolved",
      owner: "Logistics Manager",
      deadline: "2026-04-21 17:00",
      priority: "High",
      entities: "承运商A / 客户X / 17个订单 / SLA 2026-Apr",
    },
    snapshots: [
      [
        ["orders/march_shipments.xlsx", "base", "XLS"],
        ["vendors/carrier_scorecard_q1.xlsx", "base", "XLS"],
        ["reports/weekly_ops_report_draft.docx", "base", "DOC"],
        ["policies/sla_policy_q1.pdf", "base", "PDF"],
      ],
      [
        ["emails/customer_complaint_0421.eml", "new", "EML"],
        ["emails/supplier_delay_notice_0421.eml", "new", "EML"],
        ["orders/april_exception_shipments.xlsx", "new", "XLS"],
        ["vendors/carrier_scorecard_q2_partial.xlsx", "new", "XLS"],
        ["policies/sla_policy_q1.pdf", "stale", "PDF"],
        ["policies/sla_policy_april_update.pdf", "new", "PDF"],
        ["reports/weekly_ops_report_draft.docx", "updated", "DOC"],
      ],
      [
        ["emails/customer_complaint_0421.eml", "base", "EML"],
        ["orders/april_exception_shipments.xlsx", "base", "XLS"],
        ["vendors/carrier_scorecard_q2_partial.xlsx", "base", "XLS"],
        ["policies/sla_policy_q1.pdf", "stale", "PDF"],
        ["policies/sla_policy_april_update.pdf", "base", "PDF"],
        ["reports/weekly_ops_report_revised_0421.docx", "final", "DOC"],
        ["drafts/customer_response_draft_0421.docx", "final", "DOC"],
        ["meetings/delay_review_notes_0421.md", "new", "MD"],
      ],
    ],
    timeline: [
      "Observe: 发现 workspace 静态、缺少跨文件更新任务。",
      "Event: 注入承运商延误 + 客户投诉 + 新 SLA 生效。",
      "WorkUnit: 新建 Q2 物流异常复盘，优先级提升为 High。",
      "Artifacts: 生成邮件、异常表、新政策、修订周报和客户回复。",
      "Task: 从依赖子图中采样跨文件更新任务。",
    ],
    graph: [
      { id: "event", label: "Delay Event", detail: "customer + supplier", kind: "event", x: 18, y: 28 },
      { id: "email", label: "Complaint Email", detail: "deadline + demand", kind: "data", x: 154, y: 24 },
      { id: "sheet", label: "Exception Sheet", detail: "17 delayed orders", kind: "data", x: 154, y: 116 },
      { id: "policy", label: "April SLA", detail: "latest authority", kind: "data", x: 154, y: 208 },
      { id: "old", label: "Q1 SLA", detail: "stale decoy", kind: "decoy", x: 292, y: 208 },
      { id: "report", label: "Revised Report", detail: "final artifact", kind: "output", x: 292, y: 74 },
      { id: "reply", label: "Customer Reply", detail: "final artifact", kind: "output", x: 292, y: 152 },
    ],
    edges: [
      ["event", "email"],
      ["event", "sheet"],
      ["event", "policy"],
      ["email", "report"],
      ["sheet", "report"],
      ["policy", "report"],
      ["report", "reply"],
      ["old", "report"],
    ],
    task: {
      title: "更新异常复盘并生成客户回复",
      prompt:
        "请根据客户投诉、供应商延误通知、4 月异常订单表和最新 SLA 政策，更新 weekly_ops_report_revised_0421.docx 中的异常复盘部分，并生成一段客户回复草稿。",
      required: [
        "customer_complaint_0421.eml",
        "supplier_delay_notice_0421.eml",
        "april_exception_shipments.xlsx",
        "sla_policy_april_update.pdf",
      ],
      decoys: ["march_shipments.xlsx", "sla_policy_q1.pdf"],
      rubrics: [
        "使用 4 月异常订单表而不是 3 月订单表",
        "使用最新 SLA 政策而不是 Q1 政策",
        "识别承运商 A 是主要责任方",
        "在周报中写入 17 单延误",
        "生成客户回复草稿且不误改无关文件",
      ],
    },
  },
  researcher: {
    persona: "Researcher",
    tag: "paper / long-term memory",
    summary:
      "维护论文阅读、实验记录、投稿材料和导师反馈。工作区中有 PDF、BibTeX、实验表格、草稿、rebuttal 和会议笔记。",
    env: { deadline: "High", incident: "Medium", policy: "Low" },
    coverage: ["缺少导师反馈驱动的修订链", "缺少旧实验结论干扰", "缺少跨 snapshot 论文任务"],
    event: {
      type: "feedback + deadline",
      title: "导师提前要求提交 rebuttal draft",
      description:
        "导师在组会后要求今晚前整合新实验结果，并把旧 baseline 结论从 rebuttal 中替换掉。",
      source: "advisor + conference deadline",
      workunit: "WU-Rebuttal-Revision",
      effects: ["create meeting notes", "update experiment sheet", "revise rebuttal", "archive stale baseline"],
      difficulty: "memory=high, version_selection=high, artifact_update=medium",
    },
    workunit: {
      name: "Reviewer Rebuttal 修订",
      status: "draft -> revised -> ready",
      owner: "Researcher",
      deadline: "2026-05-26 23:00",
      priority: "High",
      entities: "导师反馈 / 新实验 / 旧 baseline / rebuttal",
    },
    snapshots: [
      [
        ["papers/related_work/agent_benchmarks.bib", "base", "BIB"],
        ["experiments/baseline_results_old.xlsx", "base", "XLS"],
        ["drafts/rebuttal_draft_v1.docx", "base", "DOC"],
        ["notes/reviewer_comments.md", "base", "MD"],
      ],
      [
        ["meetings/advisor_feedback_0526.md", "new", "MD"],
        ["experiments/new_ablation_results.xlsx", "new", "XLS"],
        ["experiments/baseline_results_old.xlsx", "stale", "XLS"],
        ["drafts/rebuttal_draft_v2.docx", "updated", "DOC"],
        ["figures/ablation_chart_updated.png", "new", "PNG"],
      ],
      [
        ["meetings/advisor_feedback_0526.md", "base", "MD"],
        ["experiments/new_ablation_results.xlsx", "base", "XLS"],
        ["drafts/rebuttal_final_0526.docx", "final", "DOC"],
        ["figures/ablation_chart_updated.png", "base", "PNG"],
        ["archive/baseline_results_old_README.md", "new", "MD"],
      ],
    ],
    timeline: [
      "Observe: 旧 baseline 文件和 rebuttal 草稿共存。",
      "Event: 导师反馈要求替换旧实验结论。",
      "WorkUnit: rebuttal 修订进入 urgent 状态。",
      "Artifacts: 新实验表格、反馈笔记、更新图和最终 rebuttal。",
      "Task: 生成需要长期记忆与版本判断的修订任务。",
    ],
    graph: [
      { id: "event", label: "Advisor Feedback", detail: "urgent revision", kind: "event", x: 18, y: 34 },
      { id: "notes", label: "Meeting Notes", detail: "requested changes", kind: "data", x: 154, y: 32 },
      { id: "exp", label: "New Ablation", detail: "latest results", kind: "data", x: 154, y: 124 },
      { id: "old", label: "Old Baseline", detail: "stale decoy", kind: "decoy", x: 154, y: 216 },
      { id: "fig", label: "Updated Chart", detail: "derived artifact", kind: "output", x: 292, y: 80 },
      { id: "paper", label: "Final Rebuttal", detail: "final artifact", kind: "output", x: 292, y: 168 },
    ],
    edges: [
      ["event", "notes"],
      ["notes", "paper"],
      ["exp", "fig"],
      ["exp", "paper"],
      ["old", "paper"],
      ["fig", "paper"],
    ],
    task: {
      title: "根据导师反馈修订 rebuttal",
      prompt:
        "请根据导师反馈和最新 ablation 结果，修订 rebuttal_final_0526.docx，替换旧 baseline 结论并更新图表引用。",
      required: ["advisor_feedback_0526.md", "new_ablation_results.xlsx", "rebuttal_draft_v2.docx"],
      decoys: ["baseline_results_old.xlsx"],
      rubrics: ["使用最新实验结果", "删除旧 baseline 结论", "更新图表引用", "保留 reviewer comment 对应结构"],
    },
  },
  product: {
    persona: "AI Product Manager",
    tag: "roadmap / stakeholder alignment",
    summary:
      "负责 PRD、roadmap、客户反馈和版本计划。工作区包含需求文档、会议纪要、竞品分析、指标表和发布材料。",
    env: { deadline: "Medium", incident: "Medium", policy: "High" },
    coverage: ["缺少客户反馈与 roadmap 冲突", "缺少多方 stakeholder 文件", "缺少版本优先级重排"],
    event: {
      type: "customer feedback + roadmap drift",
      title: "关键客户要求提前上线审计功能",
      description:
        "关键客户在季度回顾中要求将审计日志功能提前到 v1.4，否则会影响续约。",
      source: "key customer + sales",
      workunit: "WU-Audit-Feature-Roadmap-Shift",
      effects: ["create customer meeting note", "update roadmap", "revise PRD", "create tradeoff memo"],
      difficulty: "planning=high, conflict_resolution=high, retrieval=medium",
    },
    workunit: {
      name: "Audit Feature Roadmap Shift",
      status: "planned -> reprioritized -> approved",
      owner: "AI Product Manager",
      deadline: "2026-06-03",
      priority: "High",
      entities: "关键客户 / Sales / v1.4 / 审计日志 / 原路线图",
    },
    snapshots: [
      [
        ["roadmap/q3_product_roadmap.xlsx", "base", "XLS"],
        ["prd/audit_logs_prd_draft.docx", "base", "DOC"],
        ["feedback/customer_requests_q2.csv", "base", "CSV"],
        ["notes/launch_review_old.md", "base", "MD"],
      ],
      [
        ["meetings/key_customer_qbr_0601.md", "new", "MD"],
        ["emails/sales_escalation_0601.eml", "new", "EML"],
        ["roadmap/q3_product_roadmap.xlsx", "updated", "XLS"],
        ["prd/audit_logs_prd_v2.docx", "updated", "DOC"],
        ["notes/launch_review_old.md", "stale", "MD"],
      ],
      [
        ["meetings/key_customer_qbr_0601.md", "base", "MD"],
        ["roadmap/q3_product_roadmap_reprioritized.xlsx", "final", "XLS"],
        ["prd/audit_logs_prd_v3_approved.docx", "final", "DOC"],
        ["memos/audit_feature_tradeoff_memo.docx", "final", "DOC"],
        ["emails/customer_followup_plan.eml", "new", "EML"],
      ],
    ],
    timeline: [
      "Observe: roadmap 与客户反馈缺少明确联系。",
      "Event: 关键客户续约压力触发优先级变化。",
      "WorkUnit: audit feature 从 planned 变为 reprioritized。",
      "Artifacts: 客户纪要、sales escalation、PRD v2/v3 和 tradeoff memo。",
      "Task: 生成需要规划和冲突消解的产品任务。",
    ],
    graph: [
      { id: "event", label: "Customer QBR", detail: "renewal risk", kind: "event", x: 18, y: 42 },
      { id: "meet", label: "Meeting Note", detail: "customer ask", kind: "data", x: 154, y: 32 },
      { id: "sales", label: "Sales Email", detail: "priority pressure", kind: "data", x: 154, y: 124 },
      { id: "old", label: "Old Launch Note", detail: "stale plan", kind: "decoy", x: 154, y: 216 },
      { id: "roadmap", label: "New Roadmap", detail: "reprioritized", kind: "output", x: 292, y: 84 },
      { id: "prd", label: "Approved PRD", detail: "final artifact", kind: "output", x: 292, y: 172 },
    ],
    edges: [
      ["event", "meet"],
      ["event", "sales"],
      ["meet", "roadmap"],
      ["sales", "roadmap"],
      ["roadmap", "prd"],
      ["old", "roadmap"],
    ],
    task: {
      title: "根据客户压力重排 roadmap",
      prompt:
        "请根据关键客户 QBR 纪要和 sales escalation 邮件，更新 Q3 roadmap，并修订 audit logs PRD 的优先级与交付范围。",
      required: ["key_customer_qbr_0601.md", "sales_escalation_0601.eml", "q3_product_roadmap.xlsx"],
      decoys: ["launch_review_old.md"],
      rubrics: ["识别续约风险", "将审计日志提前到 v1.4", "解释 tradeoff", "更新 PRD scope"],
    },
  },
};

const state = {
  personaKey: "logistics",
  eventGenerated: false,
  evolutionStage: 0,
  activeSnapshot: 0,
};

const $ = (id) => document.getElementById(id);

function render() {
  const data = scenarios[state.personaKey];
  renderStage();
  $("deadlineMetric").textContent = data.env.deadline;
  $("incidentMetric").textContent = data.env.incident;
  $("policyMetric").textContent = data.env.policy;
  $("profileCard").innerHTML = `
    <div class="profile-title">
      <strong>${data.persona}</strong>
      <span class="tag">${data.tag}</span>
    </div>
    <p>${data.summary}</p>
  `;
  $("coverageList").innerHTML = data.coverage.map((item) => `<li>${item}</li>`).join("");
  renderEvent(data);
  renderWorkspace(data);
  renderWorkunit(data);
  renderGraph(data);
  renderTask(data);
}

function renderStage() {
  const activeStage = !state.eventGenerated ? 0 : Math.min(3, state.evolutionStage + 1);
  document.querySelectorAll("[data-stage-card]").forEach((card) => {
    const index = Number(card.dataset.stageCard);
    card.classList.toggle("active", index <= activeStage);
  });
}

function renderEvent(data) {
  if (!state.eventGenerated) {
    $("eventCard").className = "event-card empty-state";
    $("eventCard").textContent = "点击 Generate Event 生成一个结构化外部事件。";
    return;
  }

  $("eventCard").className = "event-card";
  $("eventCard").innerHTML = `
    <span class="event-type">${data.event.type}</span>
    <h3>${data.event.title}</h3>
    <p>${data.event.description}</p>
    <div class="json-grid">
      <div class="json-row"><span>source_actor</span><span>${data.event.source}</span></div>
      <div class="json-row"><span>target_workunit</span><span>${data.event.workunit}</span></div>
      <div class="json-row"><span>expected_effects</span><span>${data.event.effects.join(", ")}</span></div>
      <div class="json-row"><span>difficulty</span><span>${data.event.difficulty}</span></div>
    </div>
  `;
}

function renderWorkspace(data) {
  document.querySelectorAll(".tab").forEach((tab) => {
    const index = Number(tab.dataset.snapshot);
    tab.classList.toggle("active", index === state.activeSnapshot);
    tab.disabled = index > state.evolutionStage;
    tab.style.opacity = index > state.evolutionStage ? "0.45" : "1";
  });

  const files = data.snapshots[state.activeSnapshot];
  $("workspaceTree").innerHTML = files
    .map(
      ([path, status, icon]) => `
      <div class="file-row">
        <div class="file-icon">${icon}</div>
        <div class="file-path">${path}</div>
        <div class="status ${status}">${status}</div>
      </div>
    `,
    )
    .join("");
}

function renderWorkunit(data) {
  const opacity = state.eventGenerated ? "1" : "0.48";
  $("workunitCard").style.opacity = opacity;
  $("workunitCard").innerHTML = `
    <h3>${data.workunit.name}</h3>
    <div class="workunit-meta">
      <div class="meta-item"><span>Status</span><strong>${state.eventGenerated ? data.workunit.status : "waiting for event"}</strong></div>
      <div class="meta-item"><span>Priority</span><strong>${state.eventGenerated ? data.workunit.priority : "normal"}</strong></div>
      <div class="meta-item"><span>Deadline</span><strong>${state.eventGenerated ? data.workunit.deadline : "not assigned"}</strong></div>
      <div class="meta-item"><span>Entities</span><strong>${state.eventGenerated ? data.workunit.entities : "not linked"}</strong></div>
    </div>
  `;

  const visibleCount = state.eventGenerated ? Math.min(data.timeline.length, state.evolutionStage + 3) : 1;
  $("timeline").innerHTML = data.timeline
    .slice(0, visibleCount)
    .map(
      (item, index) => `
      <div class="timeline-step">
        <div class="timeline-dot">${index + 1}</div>
        <div class="timeline-text">${item}</div>
      </div>
    `,
    )
    .join("");
}

function renderGraph(data) {
  if (!state.eventGenerated) {
    $("graphCanvas").innerHTML = `<div class="empty-state" style="height:292px;border:0;">生成事件后展示依赖图。</div>`;
    return;
  }

  const visibleNodes = data.graph.filter((node) => state.evolutionStage > 0 || node.id === "event");
  const nodeMap = Object.fromEntries(data.graph.map((node) => [node.id, node]));
  const edges = data.edges
    .filter(([from, to]) => visibleNodes.some((n) => n.id === from) && visibleNodes.some((n) => n.id === to))
    .map(([from, to]) => edgeHtml(nodeMap[from], nodeMap[to]))
    .join("");
  const nodes = visibleNodes
    .map(
      (node) => `
      <div class="graph-node ${node.kind}" style="left:${node.x}px;top:${node.y}px">
        <strong>${node.label}</strong>
        <span>${node.detail}</span>
      </div>
    `,
    )
    .join("");

  $("graphCanvas").innerHTML = `${edges}${nodes}`;
}

function edgeHtml(from, to) {
  const x1 = from.x + 128;
  const y1 = from.y + 24;
  const x2 = to.x;
  const y2 = to.y + 24;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.sqrt(dx * dx + dy * dy);
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  return `<div class="graph-edge" style="left:${x1}px;top:${y1}px;width:${length}px;transform:rotate(${angle}deg)"></div>`;
}

function renderTask(data) {
  if (state.evolutionStage < 2) {
    $("taskCard").innerHTML = `
      <div class="empty-state" style="height:250px;border:0;">
        workspace 演化到 v2 后，Task Agent 会从事件链和依赖图中采样任务。
      </div>
    `;
    return;
  }

  $("taskCard").innerHTML = `
    <h3>${data.task.title}</h3>
    <p>${data.task.prompt}</p>
    <div class="task-columns">
      <div class="task-block">
        <h4>Required Files</h4>
        <ul>${data.task.required.map((x) => `<li>${x}</li>`).join("")}</ul>
      </div>
      <div class="task-block">
        <h4>Decoy / Stale Files</h4>
        <ul>${data.task.decoys.map((x) => `<li>${x}</li>`).join("")}</ul>
      </div>
    </div>
    <div class="task-block" style="margin-top:10px">
      <h4>Rubrics</h4>
      <ul class="rubric-list">${data.task.rubrics.map((x) => `<li>${x}</li>`).join("")}</ul>
    </div>
  `;
}

function resetState() {
  state.eventGenerated = false;
  state.evolutionStage = 0;
  state.activeSnapshot = 0;
  render();
}

$("personaSelect").addEventListener("change", (event) => {
  state.personaKey = event.target.value;
  resetState();
});

$("generateBtn").addEventListener("click", () => {
  state.eventGenerated = true;
  state.evolutionStage = Math.max(state.evolutionStage, 0);
  render();
});

$("evolveBtn").addEventListener("click", () => {
  state.eventGenerated = true;
  state.evolutionStage = Math.min(2, state.evolutionStage + 1);
  state.activeSnapshot = state.evolutionStage;
  render();
});

$("resetBtn").addEventListener("click", resetState);

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    const next = Number(tab.dataset.snapshot);
    if (next <= state.evolutionStage) {
      state.activeSnapshot = next;
      render();
    }
  });
});

render();
