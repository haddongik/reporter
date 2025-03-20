from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    original_text: str
    comparison_text: str
    
class ChatRequest(BaseModel):
    query: str 