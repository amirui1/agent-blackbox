# agent-blackbox

A minimal, container-ready agent service for Arena-style runners.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Check it:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/get_action \
  -H 'content-type: application/json' \
  -d '{"observation":{"task":"demo"}}'
```

## Arena integration

`arena.config.json` declares `server:app` as the HTTP entrypoint and documents
both `/get_action` and `/invoke`. Point the Arena deployment at this repository
(or build the included `Dockerfile`) and set `ARENA_API_KEY` if the deployment
requires authentication. When that variable is set, requests must include
`Authorization: Bearer <key>`.

The request supports:

```json
{"observation": {}, "config": {}, "state": null}
```

For multi-agent tasks, send `observations` instead of `observation`; the
response contains an `actions` object with the same agent IDs. Replace
`Agent.act()` in `agent.py` with the actual policy. Keep returned values JSON
serializable.

## Important assumption

“Arena” has multiple agent platforms with different registration APIs. This
repository provides a platform-neutral HTTP contract and explicit metadata so
it can be wrapped by an Arena adapter. If your Arena deployment specifies a
 different endpoint or payload schema, update `server.py` and
`arena.config.json` in one place without changing the policy in `agent.py`.
