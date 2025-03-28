from pydantic import BaseModel

class PingRequest(BaseModel):
    pass

class AnalysisRequest(BaseModel):
    elk_id: str
    ai_model: str
    battle_data: dict
    
class ChatRequest(BaseModel):
    query: str