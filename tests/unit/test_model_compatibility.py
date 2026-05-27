import logging

from pydantic import SecretStr
from openai.pagination import SyncPage
from openai.types import Model

from eureka.core.resource.model_providers.openai import (
    DEFAULT_DEEPSEEK_API_BASE_URL,
    OPEN_AI_CHAT_MODELS,
    OpenAICredentials,
    OpenAIProvider,
    _chat_completions_create_accepts_kwarg,
)
from eureka.core.resource.model_providers.schema import ChatMessage
from eureka.llm.api_manager import ApiManager


class DummyTokenizer:
    def encode(self, value: str) -> list[int]:
        return [1] * len(str(value).split())


def make_provider_for_kwargs() -> OpenAIProvider:
    provider = object.__new__(OpenAIProvider)
    provider._credentials = OpenAICredentials(api_key=SecretStr("sk-test"))
    provider._configuration = OpenAIProvider.default_settings.configuration.copy()
    return provider


def test_model_registry_includes_current_openai_and_deepseek_models():
    expected_models = {
        "gpt-5",
        "gpt-5.5",
        "gpt-5.4",
        "gpt-5.4-mini",
        "gpt-4o-mini",
        "deepseek-v4-flash",
        "deepseek-v4-pro",
        "deepseek-chat",
        "deepseek-reasoner",
    }

    assert expected_models <= set(OPEN_AI_CHAT_MODELS)
    assert OPEN_AI_CHAT_MODELS["gpt-5.5"].has_function_call_api is True
    assert OPEN_AI_CHAT_MODELS["deepseek-v4-flash"].has_function_call_api is True


def test_gpt5_message_token_count_uses_fallback_tokenizer(mocker):
    mocker.patch.object(OpenAIProvider, "get_tokenizer", return_value=DummyTokenizer())

    tokens = OpenAIProvider.count_message_tokens(
        ChatMessage.user("hello from eureka"),
        model_name="gpt-5.5",
    )

    assert tokens > 0


def test_known_gpt5_tokenizer_alias_does_not_warn(caplog):
    caplog.set_level(logging.WARNING)

    tokens = OpenAIProvider.count_message_tokens(
        ChatMessage.user("hello from eureka"),
        model_name="gpt-5.5",
    )

    assert tokens > 0
    assert "Tokenizer for model gpt-5.5 was not found" not in caplog.text


def test_gpt5_chat_kwargs_use_sdk_compatible_max_completion_tokens(mocker):
    provider = make_provider_for_kwargs()
    mocker.patch(
        "eureka.core.resource.model_providers.openai._chat_completions_create_accepts_kwarg",
        return_value=False,
    )

    kwargs = provider._get_completion_kwargs(
        model_name="gpt-5.5",
        temperature=0.5,
        max_tokens=500,
    )

    assert kwargs["model"] == "gpt-5.5"
    assert kwargs["extra_body"]["max_completion_tokens"] == 500
    assert "max_completion_tokens" not in kwargs
    assert "max_tokens" not in kwargs


def test_gpt5_chat_kwargs_use_native_max_completion_tokens_on_new_sdk(mocker):
    provider = make_provider_for_kwargs()
    mocker.patch(
        "eureka.core.resource.model_providers.openai._chat_completions_create_accepts_kwarg",
        return_value=True,
    )

    kwargs = provider._get_completion_kwargs(
        model_name="gpt-5.5",
        temperature=0.5,
        max_tokens=500,
    )

    assert kwargs["model"] == "gpt-5.5"
    assert kwargs["max_completion_tokens"] == 500
    assert "max_tokens" not in kwargs


def test_current_sdk_needs_extra_body_for_max_completion_tokens():
    assert _chat_completions_create_accepts_kwarg("extra_body") is True


def test_deepseek_chat_kwargs_keep_max_tokens():
    provider = make_provider_for_kwargs()

    kwargs = provider._get_completion_kwargs(
        model_name="deepseek-v4-pro",
        temperature=0.5,
        max_tokens=500,
    )

    assert kwargs["model"] == "deepseek-v4-pro"
    assert kwargs["max_tokens"] == 500
    assert "max_completion_tokens" not in kwargs


def test_deepseek_credentials_can_be_loaded_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE_URL", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_BASE_URL", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek")

    credentials = OpenAICredentials.from_env()

    assert credentials.api_key.get_secret_value() == "sk-deepseek"
    assert credentials.api_base.get_secret_value() == DEFAULT_DEEPSEEK_API_BASE_URL


def test_api_manager_keeps_openai_reasoning_and_deepseek_models(mocker):
    api_manager = ApiManager()
    api_manager.reset()
    mocker.patch(
        "openai.resources.models.Models.list",
        return_value=SyncPage(
            data=[
                Model(id="gpt-5.5", created=0, object="model", owned_by="openai"),
                Model(id="o4-mini", created=0, object="model", owned_by="openai"),
                Model(
                    id="deepseek-v4-pro",
                    created=0,
                    object="model",
                    owned_by="deepseek",
                ),
                Model(
                    id="text-embedding-3-small",
                    created=0,
                    object="model",
                    owned_by="openai",
                ),
            ],
            object="list",
        ),
    )

    models = api_manager.get_models(
        OpenAICredentials(api_key=SecretStr("sk-test-models"))
    )
    model_ids = {model.id for model in models}

    assert {"gpt-5.5", "o4-mini", "deepseek-v4-pro"} <= model_ids
    assert "text-embedding-3-small" not in model_ids
