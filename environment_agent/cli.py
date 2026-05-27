from __future__ import annotations

import json

from environment_agent.agent import EnvironmentAgent
from environment_agent.mock_store import MockEnvironmentStore
from environment_agent.schemas import AgentStepRequest


def main() -> None:
    store = MockEnvironmentStore()
    request = AgentStepRequest(
        user_profile=store.get_user_profile("user_logistics_001"),
        environment_profile=store.get_environment_profile("env_peak_logistics"),
        workspace_state=store.get_workspace_state("workspace_logistics_demo"),
        historical_tasks=store.get_historical_tasks("workspace_logistics_demo"),
        seed=7,
        apply_to_mock_state=True,
    )
    response = EnvironmentAgent().step(request)
    print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
