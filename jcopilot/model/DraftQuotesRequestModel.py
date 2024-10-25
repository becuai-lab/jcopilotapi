'''
Author: GimTaeGyun gtgyun@bflysoft.com
Date: 2024-08-07 16:16:33
LastEditors: GimTaeGyun gtgyun@bflysoft.com
LastEditTime: 2024-09-12 17:21:08
'''
from pydantic import BaseModel, Field

class DraftQuotesRequestModel(BaseModel):
    
    speaker : str = Field("빌게이츠", description="인용문 대상")
    quote : str = Field("그의 자녀들이 이 유산을 이어가는 것은 매우 의미 있는 일입니다.", description="인용문 내용")
    article_text : str = Field("세계적인 투자자 워런 버핏(93) 버크셔 해서웨이 회장이 사후 재산의 대부분을 세 자녀가 공동 관리하는 공익 신탁에 기부할 것이라고 밝혔다. ", description="텍스트 입력 시 내용")
    model_name : str = Field("gpt-4o", description="gpt model")