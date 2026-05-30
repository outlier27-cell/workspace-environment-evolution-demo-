# Workspace-Bench Environment Agent API

An independent demo and callable API for the Workspace-Bench Environment Agent, which drives dynamic workspace evolution from user/environment profiles, workspace state, and historical tasks.

Current generation status:

- The API is framework/backend-driven: `EnvironmentAgent` diagnoses the workspace, calls a pluggable planning backend, and optionally applies the returned plan to mock workspace state.
- The default backend is `mock_rule_based`. It uses deterministic hand-written templates for demos, tests, and integration debugging.
- Real non-rule generation should be connected by implementing a `PlanningBackend` with `generation_mode="llm"` or `generation_mode="external_provider"`.
- Backend output is validated before workspace evolution. Invalid event-plan-task references return a structured `422 plan_validation_failed` response.
- Unknown mock-store resource IDs return a structured `404 store_resource_not_found` response instead of an internal server error.

## Links

- GitHub repository: <https://github.com/outlier27-cell/workspace-bench-environment-agent-api>
- Static GitHub Pages demo: <https://outlier27-cell.github.io/workspace-bench-environment-agent-api/>
- API documentation: [API.md](./API.md)

GitHub Pages hosts the visual demo only. It does not run Python services. To expose the callable API publicly, deploy this same repository to a Python-capable host such as Vercel or Render.

## Core Idea

```text
persona + environment -> events -> WorkUnits -> artifact ecology -> dependency-aware tasks
```

The static page shows structured external event sampling, WorkUnit lifecycle changes, workspace snapshots, artifact state changes, dependency graph construction, and task/rubric generation.

The Python API exposes the same Environment Agent flow as callable HTTP endpoints.

## Public API Usage

After deploying the repository to Vercel or another Python host, use the deployment domain directly over HTTPS. No local port is needed.

```text
https://<your-api-domain>/api/health
https://<your-api-domain>/api/docs
https://<your-api-domain>/api/environment-agent/simulate
```

Example request:

```bash
curl -X POST "https://<your-api-domain>/api/environment-agent/simulate" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_logistics_001","environment_id":"env_peak_logistics","workspace_id":"workspace_logistics_demo","seed":7,"steps":3,"reset_before_run":true}'
```

Expected high-level result:

```json
{
  "workspace_id": "workspace_logistics_demo",
  "event_ids": [
    "evt_workspace_logistics_demo_incident_0001_0007",
    "evt_workspace_logistics_demo_policy_change_0002_0008",
    "evt_workspace_logistics_demo_collaboration_0003_0009"
  ],
  "final_workspace_state": {
    "current_snapshot_id": "snap_0004"
  }
}
```

## Main Endpoints

```text
GET  /api/health
GET  /api/profiles/user/{user_id}
GET  /api/profiles/environment/{environment_id}
GET  /api/workspace/{workspace_id}/state
GET  /api/workspace/{workspace_id}/tasks/history
GET  /api/workspace/{workspace_id}/events
GET  /api/workspace/{workspace_id}/inspect
GET  /api/workspace/{workspace_id}/quality
POST /api/workspace/{workspace_id}/reset
GET  /api/environment-agent/backend
POST /api/environment-agent/diagnose
POST /api/environment-agent/step/from-store
POST /api/environment-agent/simulate
POST /api/environment-agent/manager-payload/from-store
```

## Deployment

Static demo:

- GitHub Pages deploys from `.github/workflows/pages.yml`.
- The static page is served at `https://outlier27-cell.github.io/workspace-bench-environment-agent-api/`.

Callable API:

- Deploy the same repository to Vercel, Render, or another Python-capable host.
- Vercel uses `api/index.py` and `vercel.json`.
- Public API routes are served under `/api/...`.

## Files

- `index.html`: page structure
- `styles.css`: visual design
- `app.js`: scenario data and interaction logic
- `environment_agent/`: Environment Agent implementation
- `environment_agent/planning_backend.py`: default mock backend and backend boundary
- `api/index.py`: FastAPI serverless entrypoint
- `API.md`: callable API contract

## Local Development Only

Use local ports only when developing or debugging on your machine:

```bash
pip install -r requirements.txt
python -m uvicorn api.index:app --reload --port 8765
```

Then open `http://127.0.0.1:8765/api/docs`.
