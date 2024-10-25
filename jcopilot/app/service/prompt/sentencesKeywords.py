import os
from openai import OpenAI
import time

class SentencesKeywords:

    def __init__(self, openai_key, model_name):
        self.client = OpenAI(api_key=openai_key)
        self.model_name = model_name

    def summarize_text(self, input_text):
        start_time = time.time()  # Start time
        prompt = f"""You are a skilled editor or journalist. Your main role is to capture the key facts and information from the given  <news_article>  and concisely extract and summarize them in a report format.Subjective interpretations or opinions are prohibited. Based solely on the objective facts and data presented in the article, including dates, statistics, and specific details, ensure that no important information is omitted.Without any external background knowledge, compress the essence using only the words from the content of the <news_article>, summarizing in an objective and neutral tone.
                """ 
               
        example_summaries = """ 
            { "keywords": [ "키워드1", "키워드2", "키워드3", "키워드4", "키워드5" ] }
        """               

        user_message = f""" 
    <news_article>의 핵심 키워드 5개를 제시해야 한다. 
    <example>의 형식과 동일하게 줄 바꾸지 말고 결과만 출력해. 
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
            n=1,  # 1개의 답변생성
            top_p=0.5, # 일관된 답변 생성
            stop=None,
            temperature=1,  # 요약문이 정확하고 일관되게
        )
        
        final_prompt = f"{prompt}\n {user_message}"      

        return response, final_prompt

