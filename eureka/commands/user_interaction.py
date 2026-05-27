"""Commands to interact with the user"""

from __future__ import annotations

from eureka.agents.agent import Agent
from eureka.app.utils import clean_input
from eureka.command_decorator import command
from eureka.core.utils.json_schema import JSONSchema

COMMAND_CATEGORY = "user_interaction"
COMMAND_CATEGORY_TITLE = "User Interaction"


@command(
    "ask_user",
    (
        "If you need more details or information regarding the given goals,"
        " you can ask the user for input"
    ),
    {
        "question": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The question or prompt to the user",
            required=True,
        )
    },
    enabled=lambda config: not config.noninteractive_mode,
)
async def ask_user(question: str, agent: Agent) -> str:
    print(f"\nQ: {question}")
    resp = clean_input(agent.legacy_config, "A:")
    return f"The user's answer: '{resp}'"
