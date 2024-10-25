'''
Author: GimTaeGyun gtgyun@bflysoft.com
Date: 2024-08-07 16:16:33
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2024-10-23 16:51:23
'''
from pydantic import BaseModel, Field

class DraftTitleRequestModel(BaseModel):
    
    article_text : str = Field(None, description="텍스트 입력 시 내용")
    model_name : str = Field("gpt-4o", description="gpt model") 
    retry_type : str = Field(None, description="T : 제목 재생성, S : 부제목 재생성")