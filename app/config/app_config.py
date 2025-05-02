import os
from typing import TypedDict, Literal

class BattleVerifierServerConfig():
    protocol: str
    host: str
    port: int

class OpenAIConfig(TypedDict, total=False):
    api_key: str | None

class GeminiConfig(TypedDict, total=False):
    api_key: str | None

class ClaudeConfig(TypedDict, total=False):
    api_key: str | None

class AppConfig(TypedDict):
    battle_verifier: BattleVerifierServerConfig
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
        "api_key": ""
    },
    "gemini": {
        "api_key": ""
    },
    "claude": {
        "api_key": ""
    }
}

def load_config() -> AppConfig:
    """설정을 로드합니다."""
    config = DEFAULT_CONFIG.copy()
    
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

    # Gemini 설정
    if "GOOGLE_API_KEY" in os.environ:
        config["gemini"]["api_key"] = os.environ["GOOGLE_API_KEY"]

    # Claude 설정
    if "ANTHROPIC_API_KEY" in os.environ:
        config["claude"]["api_key"] = os.environ["ANTHROPIC_API_KEY"]
    
    return config

# 전역 설정 객체
app_config = load_config() 