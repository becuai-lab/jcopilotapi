
from fastapi import APIRouter, UploadFile, Depends, File, Body, Form
from jcopilot.util.logger import Logger
from jcopilot.app.service.DraftService import DraftService
from jcopilot.model.DraftRequestModel import DraftRequestModel
from jcopilot.model.DraftUpgradeRequestModel import DraftUpgradeRequestModel
from jcopilot.model.DraftQuotesRequestModel import DraftQuotesRequestModel
from jcopilot.model.DraftTitleRequestModel import DraftTitleRequestModel

logger = Logger.getInstance()

router = APIRouter(
    prefix="/jcopilot/draft",
    tags=["기사초안"],
)

service = DraftService()

@router.post(
    path = "/",
    description="기사초안생성 API",
    )
def create_draft(
        input_type : int = Form(1, description="1 : 파일첨부, 2 : 텍스트 입력"),
        input_text : str = Form(None, description="텍스트 입력 시 내용 (100자 이상 입력 필요)"),
        uploaded_file: UploadFile = File(None),
        model_name : str = Form("gpt-4o", description="gpt model"),
        is_retry : bool = Form(description="처음생성 : False, 재생성 : True"),
        file_name : str = Form(None, description="첨부파일 파일명"),
    ):
    
    data = DraftRequestModel(input_type=input_type, input_text=input_text, 
                             model_name=model_name, is_retry=is_retry, file_name=file_name)
    endpoint = '/jcopilot/draft'
    logger.info("기사초안생성 API Endpoint")
    return service.create_draft(uploaded_file, data, endpoint)

@router.post(
    path = "/title",
    description="제목추천 API",
    )
def create_draft_title(data : DraftTitleRequestModel):
    endpoint = '/jcopilot/draft/title'
    logger.info("제목추천 API Endpoint")
    return service.create_draft_title(data, endpoint)

@router.post(
    path = "/summary",
    description="요약문 추출 API",
    )
def create_draft_summary(data : DraftUpgradeRequestModel):
    endpoint = '/jcopilot/draft/summary'
    logger.info("요약문 추출 API Endpoint")
    return service.create_draft_summary(data, endpoint)

@router.post(
    path = "/keyword",
    description="키워드추출 API",
    )
def create_draft_keyword(data : DraftUpgradeRequestModel):
    endpoint = '/jcopilot/draft/keyword'
    logger.info("키워드추출 API Endpoint")
    return service.create_draft_keyword(data, endpoint)

@router.post(
    path = "/expand",
    description="길이 늘리기 API",
    )
def create_draft_expand(data : DraftUpgradeRequestModel):
    endpoint = '/jcopilot/draft/expand'
    logger.info("길이 늘리기 API Endpoint")
    return service.create_draft_expand(data, endpoint)

@router.post(
    path = "/quotation",
    description="인용구 추가 API"
    )
def create_draft_quotation(data : DraftQuotesRequestModel):
    endpoint = '/jcopilot/draft/quotation'
    logger.info("인용구 추가 API Endpoint")
    return service.create_draft_quotation(data, endpoint)

@router.post(
    path = "/upgrade",
    description="문장 업그레이드 API"
    )
def create_draft_upgrade(data : DraftUpgradeRequestModel):
    endpoint = '/jcopilot/draft/upgrade'
    logger.info("문장 업그레이드 API Endpoint")
    return service.create_draft_upgrade(data, endpoint)