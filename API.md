# Environment Agent API

This repository includes a callable FastAPI interface for the Workspace-Bench Environment Agent prototype.

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

## Run Locally

```bash
pip install -r requirements.txt
python -m uvicorn api.index:app --reload --port 8765
```

Open:

```text
http://127.0.0.1:8765/docs
```

## Deploy Publicly

This repo can be deployed to a Python serverless host such as Vercel.

```bash
vercel
vercel --prod
```

After deployment, call:

```text
https://<your-deployment-domain>/api/health
https://<your-deployment-domain>/api/docs
```

GitHub Pages can still serve the static visual demo, but it cannot run the Python API by itself.

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
POST /api/environment-agent/diagnose
POST /api/environment-agent/step
POST /api/environment-agent/step/from-store
POST /api/environment-agent/simulate
POST /api/environment-agent/manager-payload/from-store
```

When running directly with `uvicorn`, the same endpoints also work without the `/api` prefix.

## Example: Simulate Workspace Evolution

```bash
curl -X POST "http://127.0.0.1:8765/environment-agent/simulate" \
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

## Integration Contract

Replace the methods in `environment_agent/mock_store.py` with your real system providers:

```text
get_user_profile(user_id)
get_environment_profile(environment_id)
get_workspace_state(workspace_id)
get_historical_tasks(workspace_id)
```

The Environment Agent remains the decision layer. It decides what happened and how the workspace should evolve. A real Workspace Agent should materialize files, a Task Agent should generate benchmark tasks/rubrics, and a Generation Manager should coordinate snapshots and termination.

