"""The command system provides a way to extend the functionality of the AI agent."""
from eureka.core.ability.base import Ability, AbilityConfiguration, AbilityRegistry
from eureka.core.ability.schema import AbilityResult
from eureka.core.ability.simple import (
    AbilityRegistryConfiguration,
    AbilityRegistrySettings,
    SimpleAbilityRegistry,
)

__all__ = [
    "Ability",
    "AbilityConfiguration",
    "AbilityRegistry",
    "AbilityResult",
    "AbilityRegistryConfiguration",
    "AbilityRegistrySettings",
    "SimpleAbilityRegistry",
]
