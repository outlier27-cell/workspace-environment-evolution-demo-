# Workspace-Bench Environment Agent API

This repository includes a callable FastAPI interface for the Workspace-Bench Environment Agent prototype.

Repository:

```text
https://github.com/outlier27-cell/workspace-bench-environment-agent-api
```

Static demo:

```text
https://outlier27-cell.github.io/workspace-bench-environment-agent-api/
```

The static GitHub Pages demo cannot run Python. Deploy this repository to a Python-capable host such as Vercel or Render to expose the callable API.

Current generation status:

- The public interface is backend-driven.
- The default backend is `mock_rule_based`, a deterministic demo backend built from hand-written templates.
- A production non-rule generator should implement `PlanningBackend` and report `generation_mode` as `llm` or `external_provider`.
- Every backend output passes a validation gate before mock state application. Invalid references return HTTP `422` with a structured validation report.

The API models:

```text
user profile + environment profile + workspace state + historical tasks
  -> coverage diagnosis
  -> external event
  -> WorkUnit mutation
  -> artifact/dependency evolution plan
  -> task opportunity
  -> optional mock workspace evolution
```

## Public API Base URL

After deployment, call the API through the deployment domain:

```text
https://<your-api-domain>/api
```

For example:

```text
https://<your-api-domain>/api/health
https://<your-api-domain>/api/docs
https://<your-api-domain>/api/environment-agent/simulate
```

## Deploy Publicly

This repo can be deployed to a Python serverless host such as Vercel.

```bash
vercel
vercel --prod
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
POST /api/environment-agent/step
POST /api/environment-agent/step/from-store
POST /api/environment-agent/simulate
POST /api/environment-agent/manager-payload/from-store
```

## Example: Simulate Workspace Evolution

```bash
curl -X POST "https://<your-api-domain>/api/environment-agent/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_logistics_001",
    "environment_id": "env_peak_logistics",
    "workspace_id": "workspace_logistics_demo",
    "seed": 7,
    "steps": 3,
    "reset_before_run": true
  }'
```

Expected shape:

```json
{
  "workspace_id": "workspace_logistics_demo",
  "steps": [
    {
      "external_event": {
        "event_type": "incident"
      },
      "planner_backend": {
        "name": "mock_rule_based",
        "generation_mode": "mock_rule_based",
        "is_mock": true
      },
      "validation_report": {
        "status": "passed",
        "errors": []
      },
      "evolution_plan": {
        "artifact_plan": []
      },
      "task_opportunities": []
    }
  ],
  "final_workspace_state": {
    "current_snapshot_id": "snap_0004"
  },
  "event_ids": []
}
```

The real response contains full artifact plans, dependency mutations, constraints, task opportunities, and the applied mock workspace state.

## Validation Gate

The API checks backend output before applying workspace evolution or forwarding manager queues. The validation gate checks:

```text
event links
WorkUnit references
artifact dependencies
dependency graph endpoints
task required artifacts
constraint event references
```

If validation fails, the API returns:

```json
{
  "detail": {
    "error": "plan_validation_failed",
    "validation_report": {
      "status": "failed",
      "errors": ["task opportunity 'opp_bad' requires unknown artifact 'art_missing'"]
    }
  }
}
```

## Backend Metadata

Check the active generation backend:

```bash
curl "https://<your-api-domain>/api/environment-agent/backend"
```

Expected default response:

```json
{
  "name": "mock_rule_based",
  "generation_mode": "mock_rule_based",
  "version": "0.1.0",
  "is_mock": true,
  "description": "Deterministic demo backend backed by hand-written event, artifact, dependency, constraint, and task templates."
}
```

## Local Development Only

Use local ports only for development:

```bash
pip install -r requirements.txt
python -m uvicorn api.index:app --reload --port 8765
```

Open:

```text
http://127.0.0.1:8765/api/docs
```

## Integration Contract

Replace the methods in `environment_agent/mock_store.py` with your real system providers:

```text
get_user_profile(user_id)
get_environment_profile(environment_id)
get_workspace_state(workspace_id)
get_historical_tasks(workspace_id)
```

Replace `MockRuleBasedPlanningBackend` with your real `PlanningBackend` implementation when you want non-rule generation. The Environment Agent remains the orchestration layer and validates the returned `PlannedEnvironmentStep` before downstream agents act. A real Workspace Agent should materialize files, a Task Agent should generate benchmark tasks/rubrics, and a Generation Manager should coordinate snapshots and termination.
