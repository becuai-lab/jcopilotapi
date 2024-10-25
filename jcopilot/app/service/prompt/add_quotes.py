from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  
import time   
import difflib
import pandas as pd

from langchain.callbacks import get_openai_callback

# Define all rules
rules = [      
    [
        "1. 다시 작성한 내용에서는 인용구만 큰 따옴표로 감싸야 한다.",
        "2. 인용문이 있는 단락에 어울리는 객관적이고 긍정적인 문장을 인용구 뒤에 추가하여 단락을 더 풍부하게 만들어.",        
        "3. 결과만 출력해.",
    ]  
]

# Define the initial prompt template
rule_template = PromptTemplate(
    input_variables=["rules", "text", "quote", "speaker"],
    template="""
    <articles>:
    \n\n
    "{text}"
    \n\n
    추가된 인용구: "{quote}"
    \n\n
    발언자: "{speaker}"
    \n\n
    </articles>
    \n\n
    <Rules to apply>
    \n\n{rules}\n\n
    </Rules to apply>

    --------------
    You are an experienced journalist and editor.
    위 <articles>에 인용구와 발언자를 추가하여 전체 내용을 다시 작성해. 
    발언자는 인용구 앞에 명확히 추가하고 
    인용구는 문맥에 맞게 적절한 위치에 삽입해. 
    필요하다면 기존 문장을 수정해라.    
    단계적으로 생각해보자.
    """
)

class AddQuotes:

    def __init__(self, openai_key, model_name):
        self.openai_key = openai_key
        self.model_name = model_name

    # Function to apply rules in sequence
    def apply_rules(self, text, quote, speaker):
        
        #Set up the language model
        llm = ChatOpenAI(model=self.model_name, temperature=0.6, model_kwargs={"top_p": 0.3}, api_key=self.openai_key)
        
        # Define the chain
        chain = LLMChain(llm=llm, prompt=rule_template)
        
        start_time = time.time()  # Start time
        list_prompt = []
        results = []
        with get_openai_callback() as callback: 
            for i, rule_set in enumerate(rules):
                formatted_rules = "\n".join([f"{i+1}. {rule}" for i, rule in enumerate(rule_set)])
                result = chain.run(rules=formatted_rules, text=text, quote=quote, speaker=speaker)
                results.append(result)
                # final_prompt
                prompt = rule_template.format(rules=formatted_rules, text=text, quote=quote, speaker=speaker)
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

    def split_text(text):
        pre_text, bracket_text, post_text = "", "", ""
        if '[' in text and ']' in text:
            pre_text = text.split('[')[0]
            bracket_text = text.split('[')[1].split(']')[0]
            post_text = text.split(']')[1]
        else:
            pre_text = text
        return pre_text, bracket_text, post_text
