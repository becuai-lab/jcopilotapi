from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  
import time   

from langchain.callbacks import get_openai_callback


# Define all rules
rules = [      
    [
        """
        첫 문장은 다음 사항들을 고려하여 매력적인 리드문을 반드시 추가한 후 시작해야 한다.
        리드문은 기사 가장 앞에 나오며, 행위 주체에 대한 언급을 제외하고 중복되지 않는 문장으로 구성한다.
        5W1H (누가, 무엇을, 어디서, 언제, 왜, 어떻게)의 원칙을 적용하여 핵심 정보를 포함한다.
        기사의 가장 중요하고 핵심적인 내용을 한개의 문장으로 작성한다.
        간결하고 명확한 문장으로 작성하되, 독자의 호기심을 자극할 수 있도록 한다.
        독자가 리드만 읽어도 기사의 전체 내용을 대략적으로 파악할 수 있어야 한다.
        독자의 관심을 끌 수 있는 흥미로운 요소를 포함하되 사실에 근거해야 한다.
        전체 기사 내용의 톤과 스타일에 맞는 어조를 사용한다.
        리드문은 별도 문단으로 생성한다.

        아래의 기사성격에 따라 적절한 리드 스타일을 선택한다.
         -스트레이트 기사: 직접적이고 사실적인 직접 리드
         -연성 기사 (문화, 스포츠 등): 간접 리드 (명령어, 청유형, 관용어, 격언, 속담 등 활용 가능)    
        """
    ]
]



rule_template = PromptTemplate(
    input_variables=["rules", "text"],
    template="""
    interview:
    \n\n
    \{text}\
    \n\n
    <Rules to apply>
    \n\n{rules}\n\n
    </Rules to apply>

    --------------
    You are a skilled journalist who writes articles accurately according to the rules. 	
    According to the <Rules to apply> above, rewrite the interview as an article.
    Don't write the title.
    Ensure that each rule has been actually applied to the rewritten article.
    원문의 담당부서 정보는 새로 작성된 기사에 넣지 않는다.
    원문에 인용문이 있는 경우 해당 부분은 반드시 살려야 한다.   
    마지막 문단은 핵심 내용을 요약하고 결론을 제시하며 독자에게 영향을 줄 수 있는 강력한 문단이어야 하고 객관적인 내용이어야 한다.
    원문에 '▲' 이런 문장 부호가 있다면 재작성 시 그대로 유지해.
    의미가 중복되는 문장이 또 생기지 않도록 해.
    [붙임] 항목의 이하는 생략해.
    보도 일시가 기사의 날짜로 표기 되도록해. 
            예) 한국소비자원 보도자료 보도 일시 2024. 9. 6.(금) 06:00   -> 6일 한국소비자원이 발표한 자료에 따르면
                교육부 보도자료 보도 배포 2024. 8. 27 ->  교육부는 ....했다고 27일 밝혔다
    Let's think about it step by step.   
    """
) 
 
class DraftArticle:
    def __init__(self, openai_key, model_name):
        self.openai_key = openai_key
        self.model_name = model_name

    def apply_rules_first(self, text):
        temperature=0
        top_p=0.1
        return self.apply_rules(text, temperature, top_p)
        
    def apply_rules_retry(self, text):
        temperature=0.6
        top_p=0.3
        return self.apply_rules(text, temperature, top_p)


    def get_final_prompt(self, list_prompt : list, formatted_rules : str, text : str):
        prompt = rule_template.format(rules=formatted_rules, text=text)
        list_prompt.append(prompt)
        return list_prompt

    def apply_rules(self, text, temperature, top_p):
        
        # env에 OPENAI_API_KEY 설정해두면 자동으로 세팅
        llm = ChatOpenAI(temperature=temperature,               # 창의성 (0.0 ~ 2.0) 
                        model_name=self.model_name,  # 모델명
                        model_kwargs={"top_p": top_p},
                        api_key=self.openai_key,
                        )
        
        chain = LLMChain(llm=llm, prompt=rule_template)
        
        results = []
        list_prompt = []                      
        final_prompt = ''
        with get_openai_callback() as callback: 

            for i, rule_set in enumerate(rules):                        
                
                formatted_rules = "\n".join([f"{j+1}. {rule}" for j, rule in enumerate(rule_set)])                        
                result = chain.run(rules=formatted_rules, text=text)
                results.append(result)             
                self.get_final_prompt(list_prompt, formatted_rules, text)
                text = result
                
        final_prompt = "\n".join(list_prompt)
        return callback, results, final_prompt

    # 스트림 처리 중 기호 대체를 위한 함수
    def replace_special_characters(self, text):  
        # '/'를 '·'로 변경
        text = text.replace('/', '·')    
        # ', ▲'를 '▲'로 변경
        text = text.replace(', ▲', '▲')    
        return text
    
    
  