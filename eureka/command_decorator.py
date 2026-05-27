from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, ParamSpec, TypeVar

if TYPE_CHECKING:
    from eureka.agents.base import BaseAgent
    from eureka.config import Config

from eureka.core.utils.json_schema import JSONSchema
from eureka.models.command import Command, CommandOutput, CommandParameter

# Unique identifier for Eureka commands
EUREKA_COMMAND_IDENTIFIER = "eureka_command"

P = ParamSpec("P")
CO = TypeVar("CO", bound=CommandOutput)


def command(
    name: str,
    description: str,
    parameters: dict[str, JSONSchema],
    enabled: Literal[True] | Callable[[Config], bool] = True,
    disabled_reason: Optional[str] = None,
    aliases: list[str] = [],
    available: bool | Callable[[BaseAgent], bool] = True,
) -> Callable[[Callable[P, CO]], Callable[P, CO]]:
    """
    The command decorator is used to create Command objects from ordinary functions.
    """

    def decorator(func: Callable[P, CO]) -> Callable[P, CO]:
        typed_parameters = [
            CommandParameter(
                name=param_name,
                spec=spec,
            )
            for param_name, spec in parameters.items()
        ]
        cmd = Command(
            name=name,
            description=description,
            method=func,
            parameters=typed_parameters,
            enabled=enabled,
            disabled_reason=disabled_reason,
            aliases=aliases,
            available=available,
        )

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                return await func(*args, **kwargs)

        else:

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                return func(*args, **kwargs)

        setattr(wrapper, "command", cmd)
        setattr(wrapper, EUREKA_COMMAND_IDENTIFIER, True)

        return wrapper

    return decorator
