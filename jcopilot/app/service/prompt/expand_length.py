
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
        "1.원문을 그대로 출력하지는 말것 ",
        "2.확장된 결과만 출력할 것 ",
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
    원래 문장의 수를 마침표를 기준으로 세고 
    원래 의도, 톤, 문체, 객관성을 유지하면서 위 <articles>의 길이를 2배의 문장이 되도록 확장해라.   
    확장된 결과만 출력해.
    Let's think step by step.
    """
)

class ExpandLength(BasePrompt):

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
