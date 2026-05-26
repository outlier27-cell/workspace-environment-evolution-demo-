# Environment-Driven Workspace Evolution Demo

An independent static demo for illustrating how an Environment Agent can drive Workspace-Bench-style dynamic workspace generation.

## Core Idea

```text
persona + environment -> events -> WorkUnits -> artifact ecology -> dependency-aware tasks
```

The demo shows structured external event sampling, WorkUnit lifecycle changes, workspace snapshots, artifact state changes, dependency graph construction, and task/rubric generation.

## Run Locally

```bash
python -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765
```

## Files

- `index.html`: page structure
- `styles.css`: visual design
- `app.js`: scenario data and interaction logic

## Deployment

This is a static site. It can be deployed with GitHub Pages, Vercel, Netlify, or any static host.
