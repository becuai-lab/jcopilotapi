

from unicodedata import normalize
from fastapi import UploadFile
from jcopilot.util.logger import Logger
import os, json, json, time
from jcopilot.app.service.BaseService import BaseService
from jcopilot.model.BaseResponseModel import BaseResponseModel
from jcopilot.model.DraftRequestModel import DraftRequestModel
from jcopilot.model.DraftUpgradeRequestModel import DraftUpgradeRequestModel
from jcopilot.model.DraftQuotesRequestModel import DraftQuotesRequestModel
from jcopilot.model.DraftTitleRequestModel import DraftTitleRequestModel
from jcopilot.model.CommonCode import CommonCode
from jcopilot.app.service.prompt.suggest_titles import SuggestTitles
from jcopilot.app.service.prompt.sentencesKeywords import SentencesKeywords
from jcopilot.app.service.prompt.sentencesSummary import SentencesSummary
from jcopilot.app.service.prompt.writngByguideChatbotBefore2Step import DraftArticle
from jcopilot.app.service.prompt.add_quotes import AddQuotes
from jcopilot.app.service.prompt.upgrade_sentences import UpgradeSentences
from jcopilot.app.service.prompt.expand_length import ExpandLength
from functools import wraps
import json
import tempfile
from jcopilot.util.CommonExtractor import CommonExtractor

root_dir_path = os.getcwd()

logger = Logger.getInstance()
class DraftService(BaseService):
    redis = None
    database = None
    
    def __init__(self):
        super().__init__()

    def create_draft(self, uploaded_file: UploadFile, data : DraftRequestModel, endpoint):
        
        res = {            
            "result_data":"",
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0
        }
                                        
        # 추출 텍스트
        article_text = ""
        
        try:        
        
            # 1: 파일, 2: 텍스트
            input_type = data.input_type
            if input_type == 1:                           
                if not uploaded_file:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILE)
                           
                file_name = normalize('NFC', data.file_name)
                file_data = uploaded_file.file.read()
                
                if len(file_data) > 512 * 1024 * 1024:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILESIZE)
                
                if file_name.endswith(".hwp"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.hwp') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    article_text = CommonExtractor.extract_text_from_hwp(temp_file_path)
                elif file_name.endswith(".hwpx"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.hwpx') as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                    article_text = CommonExtractor.extract_text_from_hwpx(temp_file_path)
                elif uploaded_file.content_type == "application/pdf":
                    article_text = CommonExtractor.extract_text_from_pdf(file_data)
                elif file_name.endswith(".txt"):
                    article_text = file_data.decode("utf-8")  # txt 파일은 일반적으로 UTF-8로 인코딩됨
                else:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILETYPE)
                
                if not article_text:
                    return BaseResponseModel(CommonCode.COMMON_CHK_FILEREAD)   
                
                if len(article_text) >= 10000:
                    return BaseResponseModel(CommonCode.COMMON_CHK_EXTRACTLEN)                   
                
            elif input_type == 2:
                # 텍스트 방식
                article_text = data.input_text
                if not article_text:
                    return BaseResponseModel(CommonCode.COMMON_CHK_CONTENT)
                
            else:
                return BaseResponseModel(CommonCode.COMMON_CHK_TYPE)

            openai_key = self.get_openai_key()
            rule_module = DraftArticle(openai_key, data.model_name)
                            
            # prompt 호출
            if data.is_retry:
                callback, results, final_prompt = rule_module.apply_rules_retry(article_text)
            else:
                callback, results, final_prompt = rule_module.apply_rules_first(article_text)
                
            final_output = results[-1]
            final_output = rule_module.replace_special_characters(final_output)
            
            
            res['result_data'] = final_output
            res['prompt_tokens'] = callback.prompt_tokens
            res['completion_tokens'] = callback.completion_tokens
            res['total_tokens'] = callback.total_tokens            
       
        except Exception as e:
            logger.error(f"Exception Error : {e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)
    
    def create_draft_title(self, data : DraftTitleRequestModel, endpoint):
        
        res = {
            "result_data":{},
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0,
        }                
        
        try:
            openai_key = self.get_openai_key()
            rule_module = SuggestTitles(openai_key, data.model_name)
            
            response, final_prompt = rule_module.summarize_text(data.article_text, data.retry_type)
            summary_text = response.choices[0].message.content.strip()
            res['prompt_tokens'] = response.usage.prompt_tokens
            res['completion_tokens'] = response.usage.completion_tokens
            res['total_tokens'] = response.usage.total_tokens
             
            # JSON 파싱 전에 summary_text가 JSON 형식인지 확인
            summary_text = summary_text.strip()  # 앞뒤 공백 제거
            if summary_text.startswith("{") and summary_text.endswith("}"):  #json 형식 확인
                summary_json = json.loads(summary_text)
                
                res['result_data']['title'] = summary_json.get("title", "제목 없음")
                # 부제목 string 으로 변경
                sub_list = summary_json.get("subtitles", ["부제목 없음"])
                if sub_list:
                    subtitle = "\n".join(sub_list)
                    res['result_data']['subtitle'] = subtitle
                else:
                    res['result_data']['subtitle'] = None
            else:
                logger.info("JSON 형식이 아닌 응답을 받았습니다.")
                return BaseResponseModel(CommonCode.COMMON_CHK_JSON_FORMAT)
            
            
        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)
    
    def create_draft_summary(self, data : DraftUpgradeRequestModel, endpoint):
            
        res = {
            "result_data":"",
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0,
        }                
        
        try:
            openai_key = self.get_openai_key()
            rule_module = SentencesSummary(openai_key, data.model_name)
                        
            response, final_prompt = rule_module.summarize_text(data.article_text)
            
            result_data = response.choices[0].message.content.strip()
            res['result_data'] = result_data
            res['prompt_tokens'] = response.usage.prompt_tokens
            res['completion_tokens'] = response.usage.completion_tokens
            res['total_tokens'] = response.usage.total_tokens                   
            
        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)
        
    def create_draft_keyword(self, data : DraftUpgradeRequestModel, endpoint):
        
        res = {
            "result_data":{},
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0,
        }                
        
        try:            
            
            openai_key = self.get_openai_key()
            rule_module = SentencesKeywords(openai_key, data.model_name) 
            
            response, final_prompt = rule_module.summarize_text(data.article_text)
            
            result_data = response.choices[0].message.content.strip()
            res['result_data'] = result_data
            res['prompt_tokens'] = response.usage.prompt_tokens
            res['completion_tokens'] = response.usage.completion_tokens
            res['total_tokens'] = response.usage.total_tokens       
             
            # JSON 파싱 전에 result_data JSON 형식인지 확인
            result_data = result_data.strip()  # 앞뒤 공백 제거
            if result_data.startswith("{") and result_data.endswith("}"):  #json 형식 확인
                result_data_json = json.loads(result_data)
                res['result_data'] = result_data_json
            else:
                logger.info("JSON 형식이 아닌 응답을 받았습니다.")
                return BaseResponseModel(CommonCode.COMMON_CHK_JSON_FORMAT)
            
        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)
  
    def create_draft_expand(self, data : DraftUpgradeRequestModel, endpoint):
        res = {
            "result_data":"",
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0,
        }                
        
        try:
            openai_key = self.get_openai_key()
            rule_module = ExpandLength(data.article_text, data.model_name, openai_key)
            
            callback, results, final_prompt = rule_module.apply_rules()
            
            final_output = results[-1]
                        
            diff_text = rule_module.compare_texts(final_output)
            
            # 원본 값
            res['final_output'] = final_output
            if diff_text:
                # <b> 태그 붙은 값
                res['result_data'] = diff_text
            else:
                return BaseResponseModel(CommonCode.JCOPILOT_DIFF_RETRY)
            
            res['prompt_tokens'] = callback.prompt_tokens
            res['completion_tokens'] = callback.completion_tokens
            res['total_tokens'] = callback.total_tokens

        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)

    def create_draft_quotation(self, data : DraftQuotesRequestModel, endpoint):
        res = {
            "result_data":"",
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0,
        }                
        
        try:
                        
            if 30 <= len(data.quote) <= 300:
                pass
            else:
                return BaseResponseModel(CommonCode.COMMON_CHK_STRLEN)
            
            
            openai_key = self.get_openai_key()
            rule_module = AddQuotes(openai_key, data.model_name)
            
            callback, results, final_prompt = rule_module.apply_rules(data.article_text, data.quote, data.speaker)
            
            final_output = results[-1]
            
            diff_text = rule_module.compare_texts(data.article_text, final_output)
            
            # 원본 값
            res['final_output'] = final_output
            if diff_text:
                # <b> 태그 붙은 값
                res['result_data'] = diff_text
            else:
                return BaseResponseModel(CommonCode.JCOPILOT_DIFF_RETRY)
            
            res['prompt_tokens'] = callback.prompt_tokens
            res['completion_tokens'] = callback.completion_tokens
            res['total_tokens'] = callback.total_tokens                    
            
        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)
    
    def create_draft_upgrade(self, data : DraftUpgradeRequestModel, endpoint):
        res = {
            "result_data":"",
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0,
        }                
        
        try:
            
            openai_key = self.get_openai_key()
            rule_module = UpgradeSentences(data.article_text, data.model_name, openai_key)
            
            callback, results, final_prompt = rule_module.apply_rules()
            
            final_output = results[-1]
                        
            diff_text = rule_module.compare_texts(final_output)            
            
            # 원본 값
            res['final_output'] = final_output
            if diff_text:
                # <b> 태그 붙은 값
                res['result_data'] = diff_text
            else:
                return BaseResponseModel(CommonCode.JCOPILOT_DIFF_RETRY)
            
            res['prompt_tokens'] = callback.prompt_tokens
            res['completion_tokens'] = callback.completion_tokens
            res['total_tokens'] = callback.total_tokens               
            
        except Exception as e:
            logger.info(f"Exception Error:{e}")
            return BaseResponseModel(CommonCode.COMMON_FAIL, e)
        return BaseResponseModel(CommonCode.COMMON_SUCCESS, res)
