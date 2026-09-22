"""Minimal Arena-compatible agent service.

The service exposes a small HTTP contract that can be adapted to Arena runners:
- GET  /health
- POST /get_action
- POST /invoke (alias)

Replace ``Agent.act`` with your agent logic. The implementation deliberately
keeps the request and response JSON-serializable so it can run locally,
in Docker, or behind a hosted Arena adapter.
"""

from __future__ import annotations

from typing import Any


class Agent:
    """Stateless baseline agent.

    Arena can send either ``observation`` directly or an ``observations`` map
    for multi-agent tasks. Override ``act`` to implement the real policy.
    """

    name = "agent-blackbox"
    version = "0.1.0"

    def act(
        self,
        observation: Any,
        config: dict[str, Any] | None = None,
        state: Any = None,
    ) -> Any:
        """Return an action for one observation.

        The default action is intentionally explicit and safe. It makes the
        repository runnable immediately while providing a clear integration
        point for a real Arena policy.
        """
        del config, state
        if isinstance(observation, dict) and "action" in observation:
            return observation["action"]
        return {"type": "noop"}

    def get_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        observation = payload.get("observation", payload.get("observations"))
        config = payload.get("config")
        state = payload.get("state")

        if "observations" in payload and isinstance(observation, dict):
            actions = {
                agent_id: self.act(item, config=config, state=state)
                for agent_id, item in observation.items()
            }
            return {"actions": actions, "state": state}

        return {"action": self.act(observation, config=config, state=state), "state": state}


agent = Agent()
