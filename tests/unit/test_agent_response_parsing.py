import json

import pytest

from eureka.agents.agent import Agent
from eureka.agents.utils.exceptions import DuplicateOperationError
from eureka.core.resource.model_providers import AssistantChatMessage
from eureka.models.action_history import (
    Action,
    ActionInterruptedByHuman,
    ActionSuccessResult,
)


def _assistant_response(command_name: str, command_args: dict[str, str]):
    return AssistantChatMessage(
        content=json.dumps(
            {
                "thoughts": {
                    "text": "Done.",
                    "reasoning": "The task is complete.",
                    "self_criticism": "None.",
                    "plan": "- Finish",
                    "speak": "Done.",
                },
                "command": {
                    "name": command_name,
                    "args": command_args,
                },
            }
        )
    )


def test_repeated_finish_command_is_allowed(agent: Agent) -> None:
    command_args = {"reason": "Identity inquiry has been addressed."}
    agent.event_history.register_action(
        Action(name="finish", args=command_args, reasoning="The task is complete.")
    )
    agent.event_history.register_result(
        ActionInterruptedByHuman(feedback="Please finish.")
    )

    command_name, arguments, _ = agent.parse_and_process_response(
        _assistant_response("finish", command_args)
    )

    assert command_name == "finish"
    assert arguments == command_args


def test_repeated_open_file_command_is_allowed(agent: Agent) -> None:
    command_args = {"file_path": "train_cnn_model.py"}
    agent.event_history.register_action(
        Action(name="open_file", args=command_args, reasoning="Inspect the file.")
    )
    agent.event_history.register_result(
        ActionSuccessResult(outputs="File train_cnn_model.py has been opened.")
    )

    command_name, arguments, _ = agent.parse_and_process_response(
        _assistant_response("open_file", command_args)
    )

    assert command_name == "open_file"
    assert arguments == command_args


def test_repeated_non_terminal_command_is_rejected(agent: Agent) -> None:
    command_args = {"reason": "same operation"}
    agent.event_history.register_action(
        Action(name="some_command", args=command_args, reasoning="Try once.")
    )
    agent.event_history.register_result(ActionSuccessResult(outputs="done"))

    with pytest.raises(DuplicateOperationError):
        agent.parse_and_process_response(_assistant_response("some_command", command_args))
