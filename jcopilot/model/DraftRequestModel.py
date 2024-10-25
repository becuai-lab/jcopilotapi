'''
Author: GimTaeGyun gtgyun@bflysoft.com
Date: 2024-08-07 16:16:33
LastEditors: GimTaeGyun gtgyun@bflysoft.com
LastEditTime: 2024-09-27 10:12:34
'''
from pydantic import BaseModel, Field

class DraftRequestModel(BaseModel):
  
    input_type : int = Field(1, description="1 : 파일첨부, 2 : 텍스트 입력")
    input_text : str = Field(None, description="텍스트 입력 시 내용 (100자 이상 입력 필요)")
    model_name : str = Field("gpt-4o", description="gpt model")
    is_retry : bool = Field(description="처음생성 : False, 재생성 : True")
    file_name : str = Field(None, description="첨부파일 파일명")