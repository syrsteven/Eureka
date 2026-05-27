"""Configurator module."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

import click
from colorama import Back, Fore, Style

from eureka import utils
from eureka.config import Config
from eureka.config.config import (
    DEEPSEEK_R1_MODEL,
    DEEPSEEK_V3_MODEL,
    DEEPSEEK_V4_FLASH_MODEL,
    DEEPSEEK_V4_PRO_MODEL,
    GPT_3_MODEL,
    GPT_4_MODEL,
    GPT_4o_MODEL,
    GPT_5_4_MINI_MODEL,
    GPT_5_4_MODEL,
    GPT_5_5_MODEL,
)
from eureka.llm.api_manager import ApiManager
from eureka.logs.config import LogFormatName
from eureka.logs.helpers import request_user_double_check
from eureka.memory.vector import get_supported_memory_backends

if TYPE_CHECKING:
    from eureka.core.resource.model_providers.openai import OpenAICredentials

logger = logging.getLogger(__name__)


def apply_overrides_to_config(
    config: Config,
    continuous: bool = False,
    continuous_limit: Optional[int] = None,
    ai_settings_file: Optional[Path] = None,
    prompt_settings_file: Optional[Path] = None,
    skip_reprompt: bool = False,
    speak: bool = False,
    debug: bool = False,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file_format: Optional[str] = None,
    gpt3only: bool = False,
    gpt4only: bool = False,
    gpt4o_only: bool = False,
    gpt5_5: bool = False,
    gpt5_4: bool = False,
    gpt5_4_mini: bool = False,
    deepseek_r1: bool = False,
    deepseek_v3: bool = False,
    deepseek_v4_flash: bool = False,
    deepseek_v4_pro: bool = False,
    memory_type: Optional[str] = None,
    browser_name: Optional[str] = None,
    allow_downloads: bool = False,
    skip_news: bool = False,
) -> None:
    """Updates the config object with the given arguments.

    Args:
        config (Config): The config object to update.
        continuous (bool): Whether to run in continuous mode.
        continuous_limit (int): The number of times to run in continuous mode.
        ai_settings_file (Path): The path to the ai_settings.yaml file.
        prompt_settings_file (Path): The path to the prompt_settings.yaml file.
        skip_reprompt (bool): Whether to skip the re-prompting messages on start.
        speak (bool): Whether to enable speak mode.
        debug (bool): Whether to enable debug mode.
        log_level (int): The global log level for the application.
        log_format (str): The format for the log(s).
        log_file_format (str): Override the format for the log file.
        gpt3only (bool): Whether to enable GPT3.5 only mode.
        gpt4only (bool): Whether to enable GPT4 only mode.
        gpt4o_only (bool): Whether to enable GPT-4O only mode.
        gpt5_5 (bool): Whether to enable GPT-5.5 only mode.
        gpt5_4 (bool): Whether to enable GPT-5.4 only mode.
        gpt5_4_mini (bool): Whether to enable GPT-5.4 mini only mode.
        deepseek_r1 (bool): Whether to enable deepseek-r1 Only Mode.
        deepseek_v3 (bool): Whether to enable deepseek-v3 Only Mode.
        deepseek_v4_flash (bool): Whether to enable deepseek-v4-flash Only Mode.
        deepseek_v4_pro (bool): Whether to enable deepseek-v4-pro Only Mode.

        memory_type (str): The type of memory backend to use.
        browser_name (str): The name of the browser to use for scraping the web.
        allow_downloads (bool): Whether to allow Eureka to download files natively.
        skips_news (bool): Whether to suppress the output of latest news on startup.
    """
    config.continuous_mode = False
    config.tts_config.speak_mode = False

    # Set log level
    if debug:
        config.logging.level = logging.DEBUG
    elif log_level and type(_level := logging.getLevelName(log_level.upper())) is int:
        config.logging.level = _level

    # Set log format
    if log_format and log_format in LogFormatName._value2member_map_:
        config.logging.log_format = LogFormatName(log_format)
    if log_file_format and log_file_format in LogFormatName._value2member_map_:
        config.logging.log_file_format = LogFormatName(log_file_format)

    if continuous:
        logger.warning(
            "Continuous mode is not recommended. It is potentially dangerous and may"
            " cause your AI to run forever or carry out actions you would not usually"
            " authorise. Use at your own risk.",
        )
        config.continuous_mode = True

        if continuous_limit:
            config.continuous_limit = continuous_limit

    # Check if continuous limit is used without continuous mode
    if continuous_limit and not continuous:
        raise click.UsageError("--continuous-limit can only be used with --continuous")

    if speak:
        config.tts_config.speak_mode = True

    # Set the default LLM models
    if gpt3only:
        # --gpt3only should always use gpt-3.5-turbo, despite user's FAST_LLM config
        config.fast_llm = GPT_3_MODEL
        config.smart_llm = GPT_3_MODEL
    elif (
        gpt4only
        and check_model(
            GPT_4_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == GPT_4_MODEL
    ):
        # --gpt4only should always use gpt-4, despite user's SMART_LLM config
        config.fast_llm = GPT_4_MODEL
        config.smart_llm = GPT_4_MODEL
    elif (
        gpt4o_only
        and check_model(
            GPT_4o_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == GPT_4o_MODEL
    ):
        # --gpt4o_only should always use gpt-4, despite user's SMART_LLM config
        config.fast_llm = GPT_4o_MODEL
        config.smart_llm = GPT_4o_MODEL
    elif (
        gpt5_5
        and check_model(
            GPT_5_5_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == GPT_5_5_MODEL
    ):
        config.fast_llm = GPT_5_5_MODEL
        config.smart_llm = GPT_5_5_MODEL
    elif (
        gpt5_4
        and check_model(
            GPT_5_4_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == GPT_5_4_MODEL
    ):
        config.fast_llm = GPT_5_4_MODEL
        config.smart_llm = GPT_5_4_MODEL
    elif (
        gpt5_4_mini
        and check_model(
            GPT_5_4_MINI_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == GPT_5_4_MINI_MODEL
    ):
        config.fast_llm = GPT_5_4_MINI_MODEL
        config.smart_llm = GPT_5_4_MINI_MODEL
    elif (
        deepseek_v4_flash
        and check_model(
            DEEPSEEK_V4_FLASH_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == DEEPSEEK_V4_FLASH_MODEL
    ):
        config.fast_llm = DEEPSEEK_V4_FLASH_MODEL
        config.smart_llm = DEEPSEEK_V4_FLASH_MODEL
    elif (
        deepseek_v4_pro
        and check_model(
            DEEPSEEK_V4_PRO_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == DEEPSEEK_V4_PRO_MODEL
    ):
        config.fast_llm = DEEPSEEK_V4_PRO_MODEL
        config.smart_llm = DEEPSEEK_V4_PRO_MODEL
    elif (
        deepseek_r1
        and check_model(
            DEEPSEEK_R1_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == DEEPSEEK_R1_MODEL
    ):
        # --deepseek_r1 should always use deepseek_r1, despite user's SMART_LLM config
        config.fast_llm = DEEPSEEK_R1_MODEL
        config.smart_llm = DEEPSEEK_R1_MODEL
    elif (
        deepseek_v3
        and check_model(
            DEEPSEEK_V3_MODEL,
            model_type="smart_llm",
            api_credentials=config.openai_credentials,
        )
        == DEEPSEEK_V3_MODEL
    ):
        # --deepseek_v3 should always use deepseek_v3, despite user's SMART_LLM config
        config.fast_llm = DEEPSEEK_V3_MODEL
        config.smart_llm = DEEPSEEK_V3_MODEL
    else:
        config.fast_llm = check_model(
            config.fast_llm, "fast_llm", api_credentials=config.openai_credentials
        )
        config.smart_llm = check_model(
            config.smart_llm, "smart_llm", api_credentials=config.openai_credentials
        )

    if memory_type:
        supported_memory = get_supported_memory_backends()
        chosen = memory_type
        if chosen not in supported_memory:
            logger.warning(
                extra={
                    "title": "ONLY THE FOLLOWING MEMORY BACKENDS ARE SUPPORTED:",
                    "title_color": Fore.RED,
                },
                msg=f"{supported_memory}",
            )
        else:
            config.memory_backend = chosen

    if skip_reprompt:
        config.skip_reprompt = True

    if ai_settings_file:
        file = ai_settings_file

        # Validate file
        (validated, message) = utils.validate_yaml_file(file)
        if not validated:
            logger.fatal(extra={"title": "FAILED FILE VALIDATION:"}, msg=message)
            request_user_double_check()
            exit(1)

        config.ai_settings_file = config.project_root / file
        config.skip_reprompt = True

    if prompt_settings_file:
        file = prompt_settings_file

        # Validate file
        (validated, message) = utils.validate_yaml_file(file)
        if not validated:
            logger.fatal(extra={"title": "FAILED FILE VALIDATION:"}, msg=message)
            request_user_double_check()
            exit(1)

        config.prompt_settings_file = config.project_root / file

    if browser_name:
        config.selenium_web_browser = browser_name

    if allow_downloads:
        logger.warning(
            msg=f"{Back.LIGHTYELLOW_EX}"
            "Eureka will now be able to download and save files to your machine."
            f"{Back.RESET}"
            " It is recommended that you monitor any files it downloads carefully.",
        )
        logger.warning(
            msg=f"{Back.RED + Style.BRIGHT}"
            "NEVER OPEN FILES YOU AREN'T SURE OF!"
            f"{Style.RESET_ALL}",
        )
        config.allow_downloads = True

    if skip_news:
        config.skip_news = True


def check_model(
    model_name: str,
    model_type: Literal["smart_llm", "fast_llm"],
    api_credentials: OpenAICredentials,
) -> str:
    """Check if model is available for use. If not, return gpt-3.5-turbo."""
    api_manager = ApiManager()
    models = api_manager.get_models(api_credentials)

    model_ids = {m.get("id", "") if isinstance(m, dict) else m.id for m in models}
    if model_name in model_ids:
        return model_name

    if model_name.startswith("deepseek"):
        return model_name

    logger.warning(
        f"You don't have access to {model_name}. Setting {model_type} to gpt-3.5-turbo."
    )
    return "gpt-3.5-turbo"
