from pydantic import BaseModel, Field

class DraftUpgradeRequestModel(BaseModel):    
            
    article_text : str = Field(description="텍스트 입력 시 내용")
    model_name : str = Field("gpt-4o", description="gpt model")