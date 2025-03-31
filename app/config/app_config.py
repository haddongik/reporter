import os
from typing import TypedDict, Literal

class BattleVerifierServerConfig():
    protocol: str
    host: str
    port: int

class OpenAIConfig(TypedDict, total=False):
    api_key: str | None
    model: str
    temperature: float

class GeminiConfig(TypedDict, total=False):
    api_key: str | None
    model: str
    temperature: float

class ClaudeConfig(TypedDict, total=False):
    api_key: str | None
    model: str
    temperature: float

class AppConfig(TypedDict):
    openai: OpenAIConfig
    gemini: GeminiConfig
    claude: ClaudeConfig

DEFAULT_CONFIG: AppConfig = {
    "battle_verifier": {
        "protocol": "http",
        "host": "localhost",
        "port": 3000,
    },
    "openai": {
        "api_key": "",
        "model": "gpt-4o", #gpt-4.5-preview
        "temperature": 0.7,
    },
    "gemini": {
        "api_key": "",
        "model": "gemini-2.0-flash", #gemini-2.5-pro-exp-03-25
        "temperature": 0.7,
    },
    "claude": {
        "api_key": "",
        "model": "claude-3-7-sonnet-max",
        "temperature": 0.7,
    }
}

def load_config() -> AppConfig:
    config = DEFAULT_CONFIG.copy()
    config["battle_verifier"] = config["battle_verifier"].copy()
    config["openai"] = config["openai"].copy()
    config["gemini"] = config["gemini"].copy()
    config["claude"] = config["claude"].copy()

    # Battle Verifier 설정
    if "BATTLE_VERIFIER_PROTOCOL" in os.environ:
        config["battle_verifier"]["protocol"] = os.environ["BATTLE_VERIFIER_PROTOCOL"]
    if "BATTLE_VERIFIER_HOST" in os.environ:
        config["battle_verifier"]["host"] = os.environ["BATTLE_VERIFIER_HOST"]
    if "BATTLE_VERIFIER_PORT" in os.environ:
        config["battle_verifier"]["port"] = int(os.environ["BATTLE_VERIFIER_PORT"])

    # OpenAI 설정
    if "OPENAI_API_KEY" in os.environ:
        config["openai"]["api_key"] = os.environ["OPENAI_API_KEY"]
    if "OPENAI_MODEL" in os.environ:
        config["openai"]["model"] = os.environ["OPENAI_MODEL"]
    if "OPENAI_TEMPERATURE" in os.environ:
        config["openai"]["temperature"] = float(os.environ["OPENAI_TEMPERATURE"])

    # Gemini 설정
    if "GOOGLE_API_KEY" in os.environ:
        config["gemini"]["api_key"] = os.environ["GOOGLE_API_KEY"]
    if "GEMINI_MODEL" in os.environ:
        config["gemini"]["model"] = os.environ["GEMINI_MODEL"]
    if "GEMINI_TEMPERATURE" in os.environ:
        config["gemini"]["model"] = os.environ["GEMINI_TEMPERATURE"]

    # Claude 설정
    if "ANTHROPIC_API_KEY" in os.environ:
        config["claude"]["api_key"] = os.environ["ANTHROPIC_API_KEY"]
    if "CLAUDE_MODEL" in os.environ:
        config["claude"]["model"] = os.environ["CLAUDE_MODEL"]
    if "CLAUDE_TEMPERATURE" in os.environ:
        config["claude"]["model"] = os.environ["CLAUDE_TEMPERATURE"]

    return config

# 전역 설정 객체
app_config = load_config() 