from __future__ import annotations

import os
import secrets
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from agent import agent

app = FastAPI(title="agent-blackbox", version=agent.version)


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    observation: Any = None
    observations: dict[str, Any] | None = None
    config: dict[str, Any] | None = None
    state: Any = None


class ActionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    action: Any | None = None
    actions: dict[str, Any] | None = None
    state: Any = None


def authorize(authorization: str | None = Header(default=None)) -> None:
    """Require ARENA_API_KEY when configured; remain convenient for local runs."""
    expected = os.getenv("ARENA_API_KEY")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    supplied = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": agent.name, "version": agent.version}


@app.post("/get_action", response_model=ActionResponse, dependencies=[Depends(authorize)])
def get_action(request: ActionRequest) -> dict[str, Any]:
    return agent.get_action(request.model_dump(exclude_none=True))


@app.post("/invoke", response_model=ActionResponse, dependencies=[Depends(authorize)])
def invoke(request: ActionRequest) -> dict[str, Any]:
    """Alias used by Arena adapters that call agents through /invoke."""
    return agent.get_action(request.model_dump(exclude_none=True))
