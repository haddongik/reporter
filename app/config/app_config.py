import os
from typing import TypedDict, Literal

class BattleVerifierServerConfig():
    protocol: str
    host: str
    port: int

class OpenAIConfig(TypedDict, total=False):
    api_key: str | None

class GoogleConfig(TypedDict, total=False):
    api_key: str | None

class AnthropicConfig(TypedDict, total=False):
    api_key: str | None

class AppConfig(TypedDict):
    battle_verifier: BattleVerifierServerConfig
    openai: OpenAIConfig
    google: GoogleConfig
    anthropic: AnthropicConfig

DEFAULT_CONFIG: AppConfig = {
    "battle_verifier": {
        "protocol": "http",
        "host": "localhost",
        "port": 3000,
    },
    "openai": {
        "api_key": ""
    },
    "google": {
        "api_key": ""
    },
    "anthropic": {
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

    # Google 설정
    if "GOOGLE_API_KEY" in os.environ:
        config["google"]["api_key"] = os.environ["GOOGLE_API_KEY"]

    # Anthropic 설정
    if "ANTHROPIC_API_KEY" in os.environ:
        config["anthropic"]["api_key"] = os.environ["ANTHROPIC_API_KEY"]
    
    return config

# 전역 설정 객체
app_config = load_config() 