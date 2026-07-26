"""Provider registry — OpenCode-style: config-driven, user-attachable.

Every provider is described by data, not code. Adding a new OpenAI-compatible
provider is one dict entry. Users attach their own key per account (BYOK);
the server env config is only the fallback.
"""

PROVIDERS: dict[str, dict] = {
    "groq": {
        "label": "Groq",
        "kind": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "keys_url": "https://console.groq.com/keys",
        "free_tier": True,
    },
    "openrouter": {
        "label": "OpenRouter",
        "kind": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
        "keys_url": "https://openrouter.ai/settings/keys",
        "free_tier": True,
    },
    "gemini": {
        "label": "Google Gemini",
        "kind": "openai",  # Gemini exposes an OpenAI-compatible endpoint
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "default_model": "gemini-2.0-flash",
        "keys_url": "https://aistudio.google.com/apikey",
        "free_tier": True,
    },
    "cerebras": {
        "label": "Cerebras",
        "kind": "openai",
        "base_url": "https://api.cerebras.ai/v1",
        "default_model": "llama-3.3-70b",
        "keys_url": "https://cloud.cerebras.ai/",
        "free_tier": True,
    },
    "openai": {
        "label": "OpenAI",
        "kind": "openai",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "keys_url": "https://platform.openai.com/api-keys",
        "free_tier": False,
    },
    "sarvam": {
        "label": "Sarvam",
        "kind": "openai",
        "base_url": "https://api.sarvam.ai/v1",
        "default_model": "sarvam-m",
        "keys_url": "https://dashboard.sarvam.ai/",
        "free_tier": True,
    },
    "anthropic": {
        "label": "Anthropic",
        "kind": "anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-sonnet-5",
        "keys_url": "https://console.anthropic.com/settings/keys",
        "free_tier": False,
    },
}


def public_catalog() -> list[dict]:
    """Provider list safe to expose to the frontend."""
    return [
        {
            "name": name,
            "label": p["label"],
            "default_model": p["default_model"],
            "keys_url": p["keys_url"],
            "free_tier": p["free_tier"],
        }
        for name, p in PROVIDERS.items()
    ]
