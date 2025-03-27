import os
from typing import TypedDict, Literal

class ElasticsearchConfig(TypedDict):
    url: str
    index: str

class AppConfig(TypedDict):
    elasticsearch: ElasticsearchConfig
    model_type: Literal["local", "openai", "gemini", "claude"]
    openai_api_key: str | None
    google_api_key: str | None
    anthropic_api_key: str | None
    pdf_output_dir: str

# 기본 설정값
DEFAULT_CONFIG: AppConfig = {
    "elasticsearch": {
        "url": "http://10.10.20.187:9200",
        "index": "epic7*"
    },
    "model_type": "local",
    "openai_api_key": None,
    "google_api_key": None,
    "anthropic_api_key": None,
    "pdf_output_dir": "reports"
}

def load_config() -> AppConfig:
    """
    환경 변수에서 설정을 로드하고, 없는 경우 기본값을 사용합니다.
    
    Returns:
        AppConfig: 로드된 설정
    """
    config = DEFAULT_CONFIG.copy()
    
    # Elasticsearch 설정
    if "ELASTICSEARCH_URL" in os.environ:
        config["elasticsearch"]["url"] = os.environ["ELASTICSEARCH_URL"]
    if "ELASTICSEARCH_INDEX" in os.environ:
        config["elasticsearch"]["index"] = os.environ["ELASTICSEARCH_INDEX"]
    
    # 모델 설정
    if "MODEL_TYPE" in os.environ:
        model_type = os.environ["MODEL_TYPE"]
        if model_type in ["local", "openai", "gemini", "claude"]:
            config["model_type"] = model_type
    
    # API 키 설정
    if "OPENAI_API_KEY" in os.environ:
        config["openai_api_key"] = os.environ["OPENAI_API_KEY"]
    if "GOOGLE_API_KEY" in os.environ:
        config["google_api_key"] = os.environ["GOOGLE_API_KEY"]
    if "ANTHROPIC_API_KEY" in os.environ:
        config["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]
    
    # PDF 출력 디렉토리 설정
    if "PDF_OUTPUT_DIR" in os.environ:
        config["pdf_output_dir"] = os.environ["PDF_OUTPUT_DIR"]
    
    return config

# 전역 설정 객체
app_config = load_config() 