"""Provider factory — OpenCode-style resolution order:

1. The user's own attached provider (BYOK, key stored encrypted per account)
2. The server's env-configured provider (LLM_PROVIDER/LLM_API_KEY)
3. The offline mock (never fails, no key needed)
"""
from app.core.config import settings
from app.core.crypto import decrypt_secret
from app.llm.base import LLMProvider
from app.llm.mock import MockProvider
from app.llm.registry import PROVIDERS


def build_provider(name: str, model: str | None, api_key: str) -> LLMProvider | None:
    spec = PROVIDERS.get(name)
    if spec is None or not api_key:
        return None
    resolved_model = model or spec["default_model"]
    if spec["kind"] == "anthropic":
        from app.llm.remote import AnthropicProvider

        return AnthropicProvider(model=resolved_model, api_key=api_key)
    from app.llm.remote import OpenAICompatProvider

    return OpenAICompatProvider(name=name, base_url=spec["base_url"], model=resolved_model, api_key=api_key)


def get_llm(user=None) -> LLMProvider:
    """Resolve the provider for a request. Pass the User (or any object with
    llm_provider/llm_model/llm_api_key_enc) to honor their attached provider."""
    if user is not None and getattr(user, "llm_provider", None) and getattr(user, "llm_api_key_enc", None):
        key = decrypt_secret(user.llm_api_key_enc)
        if key:
            provider = build_provider(user.llm_provider, getattr(user, "llm_model", None), key)
            if provider is not None:
                return provider
    env_provider = build_provider(settings.LLM_PROVIDER.lower(), settings.LLM_MODEL or None, settings.LLM_API_KEY)
    return env_provider if env_provider is not None else MockProvider()
