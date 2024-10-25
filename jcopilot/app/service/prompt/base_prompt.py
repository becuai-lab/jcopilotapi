
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  
import time   
import difflib
import pandas as pd

from langchain.callbacks import get_openai_callback

class BasePrompt:    
    
    def __init__(self, input_text, model_name, openai_key):
        self.input_text = input_text
        self.model_name = model_name
        self.openai_key = openai_key
    
    def apply_rules(self, rule_template, rules, temperature, top_p):    
        
        text = self.input_text
        
        #Set up the language model
        llm = ChatOpenAI(model=self.model_name, temperature=temperature, model_kwargs={"top_p": top_p}, api_key=self.openai_key)
        
        # Define the chain
        chain = LLMChain(llm=llm, prompt=rule_template)
        
        start_time = time.time()  # Start time
        list_prompt = []   
        results = []
        with get_openai_callback() as callback: 
            for i, rule_set in enumerate(rules):
                formatted_rules = "\n".join([f"{i+1}. {rule}" for i, rule in enumerate(rule_set)])
                result = chain.run(rules=formatted_rules, text=text)
                results.append(result)
                # final_prompt
                prompt = rule_template.format(rules=formatted_rules, text=text)
                list_prompt.append(prompt)
                text = result  # Update text with the latest result
        end_time = time.time()  # End time
        execution_time = end_time - start_time  # Calculate execution time
        
        final_prompt = "\n".join(list_prompt)
        return callback, results, final_prompt
    
    # 변경 사항 태그 추가
    def compare_texts(self, initial_text, final_text):
        diff = difflib.ndiff(initial_text, final_text)
        diff_text = []
        # 변경된 글자가 연속한 경우 제일 앞,뒤만 <b> 태그를 붙인다.
        chg_tag_flag = False  
        
        for line in diff:
            if line.startswith('?'):
                continue
            elif line.startswith('+'):
                if not chg_tag_flag:
                    diff_text.append("<b>") # 연속된 변경의 시작점에 <b> 추가
                    chg_tag_flag = True                
                diff_text.append(line[2:])
            elif line.startswith('-'):
                continue
            else:
                if chg_tag_flag:
                    diff_text.append("</b>") # 연속된 변경의 끝점에 </b> 추가
                    chg_tag_flag = False
                diff_text.append(line[2:])
                
        if chg_tag_flag:
            diff_text.append("</b>")  # 마지막으로 닫히지 않은 <b> 태그 처리
            
        return ''.join(diff_text)