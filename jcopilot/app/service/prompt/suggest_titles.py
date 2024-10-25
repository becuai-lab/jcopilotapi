
import os
from openai import OpenAI
import time
import json

class SuggestTitles:    
    
    def __init__(self, openai_key, model_name):
        self.client = OpenAI(api_key=openai_key)
        self.model_name = model_name
    
    def summarize_text(self, input_text, retry_type):
        
        
        start_time = time.time()  # 시작 시간 기록
        prompt = f"""You are a skilled editor or journalist.
                """ 
                    
        req_title = 'T'
        req_subtitle = 'S'
        
        if retry_type == req_title:
            first_prompt = '<news_article>의 기사를 바탕으로 주목을 끄는 제목 1개를 제안해라.'
            
            example_summaries = """ 
                { "title": "생성된 제목", "subtitles": null }
            """                
        elif retry_type == req_subtitle:
            first_prompt = '<news_article>의 기사를 바탕으로  핵심 정보를 담은 부제목 4개를 제안해라.'
            example_summaries = """ 
                { "title": null, "subtitles": [ "생성된 부제목1", "생성된 부제목2", "생성된 부제목3", "생성된 부제목4" ] }
            """                     
        else:
            # 제목 처음 생성 시 제목 + 부제목 동시 생성
            first_prompt = '<news_article>의 기사를 바탕으로 주목을 끄는 제목 1개와 핵심 정보를 담은 부제목 4개를 제안해라.'
            example_summaries = """ 
                { "title": "생성된 제목", "subtitles": [ "생성된 부제목1", "생성된 부제목2", "생성된 부제목3", "생성된 부제목4" ] }
            """
        
        user_message = f""" 
    {first_prompt}
    <example>의 형식과 동일하게 줄 바꾸지 말고 결과만 출력해. 

    제목 요구사항:
    - 뉴스의 핵심 메시지를 간결하게 전달할 것
    - 독자의 관심을 끌 수 있는 흥미로운 표현 사용
    - 명확한 동사적 의미를 포함하고, 능동형 동사를 선호
    - 독자가 쉽게 이해할 수 있도록 간단한 표현을 사용
    - 기사 성격에 따라 이성적 또는 감성적으로 접근
    - 가능한 한 어휘를 압축해 표현

    부제목 요구사항:
    - 각 부제목은 제목을 보완하는 추가 정보 제공
    - 뉴스의 주요 사실이나 인용구 활용

    Let's think step by step.
    
        <news_article>
        ---------------------------------------------------------------------------------------
        {input_text}
        ---------------------------------------------------------------------------------------
        </news_article>
        
        <example>
        {example_summaries}
        </example>
        """

        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": prompt},                   
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},                   
                    ],
                }
            ],
            max_tokens=4096,
            n=1,  # 1개의 답변 생성
            top_p=0.5, 
            stop=None,
            temperature=1,  
        )
        
        final_prompt = f"{prompt}\n {user_message}"
        
        return response, final_prompt
