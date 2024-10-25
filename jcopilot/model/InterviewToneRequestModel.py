
from typing import List
from pydantic import BaseModel, Field

class InterviewToneRequestModel(BaseModel):
    model_name : str = Field("gpt-4o", description="gpt model 기본값 gpt-4o")
    interview_question : List[str] = Field(description="생성된 질의문 리스트 ex) [\"질문1\", \"질문2\", \"질문3\"]")
    interview_tone : str = Field("공식적", description="공식적, 친화적, 비판적, 전문적, 의심적")


    
    
