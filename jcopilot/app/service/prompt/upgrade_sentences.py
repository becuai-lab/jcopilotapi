
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  
import time   
import difflib
import pandas as pd

from langchain.callbacks import get_openai_callback
from jcopilot.app.service.prompt.base_prompt import BasePrompt

# Define all rules
rules = [      
    [
        "1.원문을 그대로 출력하지는 말 것",
        "2.원문의 명사는 그대로 사용할 것",
    ]  
]

# Define the initial prompt template
rule_template = PromptTemplate(
    input_variables=["rules", "text"],
    template="""
    
    <articles>:
    \n\n
    \"{text}\" 
    \n\n
    </articles>
    \n\n
    <Rules to apply>
    \n\n{rules}\n\n
    </Rules to apply>

    --------------
    You are an experienced journalist and editor. 
    위<articles>의 원래 의미와 구조를 유지하면서 문장을 더 자연스럽고 명확하게 다듬어. 
    모호한 표현은 구체화하고 전체적인 내용과 톤은 그대로 유지해.
    원문의 내용 변경은 최소화 하고 원문의 본질적인 메시지는 변경하면 안된다.    
    """
)

class UpgradeSentences(BasePrompt):

    def __init__(self, input_text, model_name, openai_key):
        super().__init__(input_text, model_name, openai_key)

    def apply_rules(self):
        temperature=0.6
        top_p=0.3
        return super().apply_rules(rule_template, rules, temperature, top_p)

    def compare_texts(self, final_text):
        return super().compare_texts(self.input_text, final_text)

    def split_text(text):
        pre_text, bracket_text, post_text = "", "", ""
        if '[' in text and ']' in text:
            pre_text = text.split('[')[0]
            bracket_text = text.split('[')[1].split(']')[0]
            post_text = text.split(']')[1]
        else:
            pre_text = text
        return pre_text, bracket_text, post_text

