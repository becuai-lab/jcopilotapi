import os
from openai import OpenAI
import time

class SentencesSummary:
    
    def __init__(self, openai_key, model_name):
        self.client = OpenAI(api_key=openai_key)
        self.model_name = model_name

    def summarize_text(self, input_text):
        start_time = time.time()  # Start time
        prompt = f"""You are a skilled editor or journalist. Your main role is to capture the key facts and information from the given  <news_article>  and concisely extract and summarize them in a report format.Subjective interpretations or opinions are prohibited. Based solely on the objective facts and data presented in the article, including dates, statistics, and specific details, ensure that no important information is omitted.Without any external background knowledge, compress the essence using only the words from the content of the <news_article>, summarizing in an objective and neutral tone.
                """ 
                
        example_summaries = f""" 
    정부의 의대 증원 정책에 반발한 전공의들이 집단 사직 후 복귀하지 않자, 전문의 배출에 차질이 우려된다. 정부는 전공의들에게 복귀를 촉구하면서도 수련 기간 일부를 인정할 가능성을 시사했다. 의대 교수들은 정부의 적극적인 대처를 요구하고 있다.

        """               

        user_message = f""" 
    <news_article>의 핵심 내용을 3문장으로 간략하게 요약해야 한다. 요약문은 <example>의  문장 형식과 동일하게 "~했다." 와 같이 동사로 끝나는 형식으로 작성해라.    
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