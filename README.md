# Environment-Driven Workspace Evolution Demo

An independent demo for illustrating and calling an Environment Agent that drives Workspace-Bench-style dynamic workspace generation.

## Core Idea

```text
persona + environment -> events -> WorkUnits -> artifact ecology -> dependency-aware tasks
```

The static page shows structured external event sampling, WorkUnit lifecycle changes, workspace snapshots, artifact state changes, dependency graph construction, and task/rubric generation.

The Python API exposes the same Environment Agent flow as callable HTTP endpoints.

## Run Static Demo Locally

```bash
python -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765
```

## Run API Locally

```bash
pip install -r requirements.txt
python -m uvicorn api.index:app --reload --port 8765
```

Open:

```text
http://127.0.0.1:8765/docs
```

Example:

```bash
curl -X POST "http://127.0.0.1:8765/environment-agent/simulate" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_logistics_001","environment_id":"env_peak_logistics","workspace_id":"workspace_logistics_demo","seed":7,"steps":3,"reset_before_run":true}'
```

For the full API contract, see [API.md](./API.md).

## Files

- `index.html`: page structure
- `styles.css`: visual design
- `app.js`: scenario data and interaction logic
- `environment_agent/`: Environment Agent implementation
- `api/index.py`: FastAPI serverless entrypoint
- `API.md`: callable API contract

## Deployment

The static demo can be deployed with GitHub Pages, Vercel, Netlify, or any static host.

The API needs a Python runtime. Deploy this repo to Vercel, Render, or another Python-capable host. On Vercel, the callable endpoints are available under `/api/...`, for example:

```text
https://<your-domain>/api/health
https://<your-domain>/api/environment-agent/simulate
```
