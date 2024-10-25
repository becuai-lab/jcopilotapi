
import tempfile
from turtle import st
from typing import List
from fastapi import UploadFile
from openai import OpenAI
from jcopilot.model.BaseResponseModel import BaseResponseModel
from jcopilot.model.CommonCode import CommonCode
from jcopilot.model.InterviewToneRequestModel import InterviewToneRequestModel
from jcopilot.util.CommonExtractor import CommonExtractor
from jcopilot.util.logger import Logger
import os, json, json, time
from jcopilot.app.service.BaseService import BaseService
from functools import wraps
import json
import pandas as pd
root_dir_path = os.getcwd()

logger = Logger.getInstance()

class InterviewService(BaseService):

    # System message
    system_prompt = "당신은 유명 언론사에 소속된 저널리스트임. 지금부터 취재를 나가기 전에 인터뷰 대상에게 할 질의문을 미리 생성하는 역할을 수행할 것."

    # 질의문 옵션
    condition = {
        "공식적" : {
            "desc" : "격식을 갖춘 정중하고 공손한 표현(톤)을 사용하여", 
            "example" : '''
                - 대통령께서 오늘 국회 연설에서 발표하신 경제 정책에 대한 의견을 말씀해주시겠습니까?
                - 구체적으로 어떤 기대를 하고 계신지, 또 그 기대효과에 대해 말씀 부탁드립니다.
            '''
            },
        "친화적" : {
            "desc" : "편하고 친근한 표현(톤)을 사용하여", 
            "example" :  '''
                - 오늘 대통령님의 국회 연설에서 발표된 경제 정책에 대한 생각을 듣고 싶은데요, 어떤 부분이 가장 인상적이셨는지 여쭤봐도 될까요?
                - 대통령님께서 제시하신 경제 정책, 특히 어떤 부분이 우리 경제에 긍정적인 영향을 줄 것이라고 생각하시는지 궁금합니다.
            '''
            },
        "비판적" :{
            "desc" : "다소 공격적이고 비판적인 표현(톤)을 사용하여", 
            "example" : '''
                - 이번 사건으로 인해 많은 피해가 발생했지만, 정부의 대응은 지지부진하다는 평가를 받고 있습니다. 이에 대해 어떻게 생각하시나요?
                - 대통령께서는 오늘 진행한 국회 연설에서 새로운 경제 정책을 말씀하셨는데, 해당 정책으로 인한 빈부격차에 대해서는 생각해 보셨는지, 또 해당 정책이 경제 성장에 미치는 부정적인 영행에 대해 어떻게 평가하십니까?
                - 작년 ㅇㅇㅇ 정책이 도입되고 경제 성장률이 현저히 낮아졌고, 효과가 낮다는 평에 대해 어떻게 생각하십니까? 
                - 이 정책이 장기적으로 지속 가능하다고 보십니까? 만약 그렇지 않다면, 어떤 대안을 고려하고 계신가요?
                - 정부의 '지지부진한' 대응이라는 표현은 너무 부드럽군요. 마치 아무 일도 없었다는 듯이 시간만 끌고 있는 것 아닙니까?
            '''
            },
        "전문적" : {
            "desc" : "지적이고 전문적인 표현(톤)을 사용하여", 
            "example" : '''
                - 해당 정책의 도입이 경제 성장에 미치는 영향과 장기적인 경제 성장 가능성에 대해 한말씀 부탁드립니다.
                - 해당 문제의 해결을 위한 정부의 정책적 대안은 무엇이며, 그 실행 과정에서 예상되는 주요 제약 조건은 무엇인지 구체적으로 설명해 주십시오.
                - 제시된 문제에 대한 정부의 해결 방안은 이론적 근거를 바탕으로 얼마나 타당하며, 실제 정책 실행 시 예상되는 현실적인 어려움은 무엇이라고 생각하십니까?
                - 본 문제의 복합적인 성격을 고려할 때, 정부의 해결 방안은 다양한 분야의 전문가 의견을 종합하여 마련되었는지, 그리고 예상되는 어려움에 대한 사전적인 대비책은 마련되어 있는지 궁금합니다.
                - 유사한 문제를 해결한 다른 국가의 사례를 참고하여, 우리 정부의 해결 방안이 얼마나 효과적일 것으로 예상하며, 시사점은 무엇이라고 생각하십니까?
                - 장기적인 관점에서 볼 때, 정부의 해결 방안이 문제의 근본적인 원인을 해결할 수 있을지 의문이며, 향후 발생할 수 있는 유사한 문제에 대한 예방책은 마련되어 있는지 설명해주시기 바랍니다.
            '''
            },
        "의심적" : {
            "desc" : "의심하거나 믿지 않는 듯한 표현(톤)을 사용하여", 
            "example" : '''
                - 작년 경제정책 발표 후 경제 성장률에 영향을 주지 않는 것으로 보아 해당 정책이 효과가 있을지 미지수라 생각되는데, 이번 경제 정책은 어떻게 보십니까?
                - 대통령꼐서 오늘 국회 연설에서 발표한 새로운 경제정책은, 작년에 발표하신 경제 정책과 비슷하다고 판단되는데, 작년에 발표하신 경제정책 도입에 따른 경제성장률을 고려하시고 발표하시는 건지 궁금합니다.
                - 정책 시행 후 관련 데이터가 공개되지 않고 있습니다. 해당 정책이 직접적으로 긍정적 영향이 있었는지 궁금합니다.
                - 과연 이번 사건으로 인해 많은 피해가 발생했다는 주장이 얼마나 신빙성이 있을까요? 또, 정부의 대응이 지지부진하다는 평가는 어떤 근거에 기반한 것인지 궁금합니다.
                - 이번 사건에 대한 피해 규모나 정부의 대응에 대한 평가는 객관적인 데이터를 바탕으로 이루어진 것일까요? 아니면 주관적인 판단이 개입된 것일까요?
                - 정부의 대응이 지지부진해 보이는 대응에 다른 어떤 이유가 있는 것일까요? 예를 들어, 문제의 복잡성이나 예상치 못한 변수 등이 존재할 가능성은 고려해 보지 않으셨나요?
                - '많은 피해'라는 표현은 다소 과장되어 보일 수 있어보입니다. 구체적인 피해 규모와 내용을 명확히 제시해 주실 수 있나요?
            '''
            }
    }
    
    def __init__(self):
        super().__init__()
        
    def create_interview(
            self,
            model_name,  
            input_type,
            input_text,
            interview_purpose : str,
            interview_tone : str,
            uploaded_file : UploadFile,
            file_name,
            ):

        result = "" 
        
        try:   
            # 최초 프롬프트
            prompt = '''         
질의문은 총 5개 생성할 것이며, 질의문은 모두 {TON} 질의문을 생성할 것.

질의문을 생성할 때 아래 지시사항을 만족하기 위해 최선의 노력을 다할 것.
- "{PURPOSE}" 라는 취재 목적에 적합한 수준 높은 한국어 질의문을 생성할 것
- 본 취재와 관련하여 질의문 생성에 도움이 될만한 정보는 아래의 [사전 확보 정보]를 참고하고, 해당 내용에서 확인할 수 있는 사항은 질의문을 생성하지 말 것
- [사전 확보 정보]
{INFORMATION}
- 생성한 질의문은 반드시 아래 JSON 파일과 동일한 형식을 사용하여 작성할 것. 마크다운 코드 블록 구문(```)을 사용하지 않고 직접 텍스트로만 출력 할 것
{{"question":["질문1","질문2","질문3","질문4","질문5"]}}
            '''

            # 프롬프트 취재목적
            purpose = interview_purpose     

            # 프롬프트 질의톤
            if interview_tone == "":
                tone = self.condition['공식적']['desc']
            elif interview_tone in self.condition:
                tone = self.condition[interview_tone]['desc']           
            else:
                return BaseResponseModel(CommonCode.INTERVIEW_CHK_TONE)

            # 프롬프트 사전확보정보
            information = ""
            if input_type == 2:
                information = input_text

            elif input_type == 1:
                if not uploaded_file:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILE)
                
                file_data = uploaded_file.file.read()

                if len(file_data) > 512 * 1024 * 1024:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILESIZE)
                
                # 텍스트 추출
                if file_name.endswith(".hwp"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.hwp') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    information = CommonExtractor.extract_text_from_hwp(temp_file_path)
                elif file_name.endswith(".hwpx"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.hwpx') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    information = CommonExtractor.extract_text_from_hwpx(temp_file_path)
                elif uploaded_file.content_type == "application/pdf":
                    information = CommonExtractor.extract_text_from_pdf(file_data)
                elif file_name.endswith(".txt"):
                    information = file_data.decode("utf-8")  # txt 파일은 일반적으로 UTF-8로 인코딩됨
                else:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILETYPE)

                if information == "" or information == None:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILEREAD) 

                if len(information) >= 10000:
                    return BaseResponseModel(CommonCode.COMMON_CHK_EXTRACTLEN)  

            else:
                return BaseResponseModel(CommonCode.INTERVIEW_CHK_INFOTYPE)

            # 호출
            prompt = prompt.format(TON=tone, PURPOSE=purpose, INFORMATION=information)       
            response = self.call_chat(model_name, prompt)    
            completion = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
                
            # 응답
            json_string = completion.strip().strip("```json").strip("```").strip("")
            json_data = json.loads(json_string)
            if 'question' in json_data:
                result = json_data['question']
            else:
                return BaseResponseModel(CommonCode.INTERVIEW_RES_FAIL)          

        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, result)

    

    def add_interview(
            self,
            model_name, 
            input_type,
            input_text,
            interview_question : str,
            uploaded_file : UploadFile, 
            file_name
            ):
        
        result = []

        try:

            # 최초 프롬프트 
            prompt = '''
아래 [질의문] 목록과 [사전 확보 정보]의 내용에 기반한 질문 1개를 더 추가해줘. 
다른 질의문의 톤과 동일하게 유지할 것.
생성한 질의문은 반드시 구분자("-"), 줄바꿈 구문("\\n")을 사용하지 않고 단일 문장으로만 출력 할 것
생성한 질의문은 반드시 [질의문] 목록 중 동일한 질의문이 절대 없어야 할 것
    
[질의문]
{QUESTION}

[사전 확보 정보]
{INFORMATION}    
            '''

            # 프롬프트 질의문 
            question = ""
            interview_question = eval(interview_question)
            for i in range(len(interview_question)):
                question += f"- {interview_question[i]}\n" 

            # 프롬프트 사전확보정보
            information = ""       
            if input_type == 2:
                information = input_text

            elif input_type == 1:
                if not uploaded_file:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILE)
                
                file_data = uploaded_file.file.read()

                if len(file_data) > 512 * 1024 * 1024:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILESIZE)
                
                # 텍스트 추출
                if file_name.endswith(".hwp"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.hwp') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    information = CommonExtractor.extract_text_from_hwp(temp_file_path)
                elif file_name.endswith(".hwpx"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.hwpx') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    information = CommonExtractor.extract_text_from_hwpx(temp_file_path)
                elif uploaded_file.content_type == "application/pdf":
                    information = CommonExtractor.extract_text_from_pdf(file_data)
                elif file_name.endswith(".txt"):
                    information = file_data.decode("utf-8")  # txt 파일은 일반적으로 UTF-8로 인코딩됨
                else:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILETYPE)

                if information == "" or information == None:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILEREAD)     

                if len(information) >= 10000:
                    return BaseResponseModel(CommonCode.COMMON_CHK_EXTRACTLEN)               
            else:
                return BaseResponseModel(CommonCode.INTERVIEW_CHK_INFOTYPE)

            # 호출
            prompt = prompt.format(QUESTION=question, INFORMATION=information)
            response = self.call_chat(model_name, prompt)       
            completion = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

            # 응답
            result = completion.strip("[질의문]").strip("\\n")

        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, result)

    def tone_interview(
            self, 
            data : InterviewToneRequestModel
            ):
        
        result = []

        try:  

            # 최초 프롬프트
            prompt = '''
제시된 모든 [질의문]의 톤을  {TONE}을 사용한 {TYPE}으로 변경할 것. 아래의 [질문 문체 예시]를 참고해서 변경할 것.
생성한 질의문은 반드시 구분자("-"), 줄바꿈 구문("\\n")을 사용하지 않을 것
생성한 질의문은 반드시 아래 JSON 파일과 동일한 형식을 사용하여 작성할 것. 마크다운 코드 블록 구문(```)을 사용하지 않고 직접 텍스트로만 출력 할 것
{{"question":["질문1","질문2","질문3","질문4","질문5",...]}}

[질문 문체 예시] 
{EXAM}

[질의문]
{QUESTION}          
            '''

            # 프롬프트 질의문톤    
            interview_tone = data.interview_tone
            if interview_tone == "":
                tone = self.condition['공식적']['desc']
                example = self.condition['공식적']['example']
            elif interview_tone in self.condition:
                tone = self.condition[interview_tone]['desc']   
                example = self.condition[interview_tone]['example']        
            else:
                return BaseResponseModel(CommonCode.INTERVIEW_CHK_TONE)
            
            # 프롬프트 질의문 
            question = ""
            interview_question = data.interview_question
            for i in range(len(interview_question)):
                question += f"- {interview_question[i]}\n"
            
            # 호출
            prompt = prompt.format(QUESTION=question, TONE=tone, TYPE=interview_tone, EXAM=example)
            response = self.call_chat(data.model_name, prompt)
            completion = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens      

            # 응답
            json_string = completion.strip().strip("```json").strip("```").strip("")
            json_data = json.loads(json_string)
            if 'question' in json_data:
                result = json_data['question']
            else:
                return BaseResponseModel(CommonCode.INTERVIEW_RES_FAIL) 
        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, result)
    
    # Open AI 호출
    def call_chat(self, model_name : str, prompt : str):
        openai_key = self.get_openai_key()
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": self.system_prompt},                   
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},                   
                    ],
                }
            ],
            max_tokens=4096,
            n=1,  # 1개의 답변생성
        )
        return response

        
