
# coding:utf-8
from typing import List
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from jcopilot.model.InterviewToneRequestModel import InterviewToneRequestModel
from jcopilot.util.logger import Logger
from jcopilot.app.service.InterviewService import InterviewService

logger = Logger.getInstance()

router = APIRouter(
    prefix="/jcopilot/interview",
    tags=["취재질의"],
)

service = InterviewService()

@router.post(path = "/", description="취재질의 생성 API - 최초 생성 / 재생성")
def create_interview(
        model_name : str = Form("gpt-4o", description="gpt model 기본값 gpt-4o"),   
        input_type : int = Form(1, description="사전확보정보 유형 - 파일 : 1, 텍스트 : 2"),
        input_text : str = Form(None, description="사전확보정보 텍스트 내용(input_type = 2인 경우 입력)"),
        interview_purpose : str = Form(description="취재목적"),
        interview_tone : str = Form("공식적", description="질의문톤 - 공식적, 친화적, 비판적, 전문적, 의심적"),
        uploaded_file : UploadFile = File(None, description="사전확보정보 파일(input_type = 1인 경우 입력)"),
        file_name : str = Form(None, description="사전확보정보 파일명")
    ):
    return service.create_interview(
        model_name,
        input_type,
        input_text,
        interview_purpose,
        interview_tone,
        uploaded_file,
        file_name
        )

@router.post(path = "/add", description="취재질의 추가질문 API")
def add_interview(
        model_name : str = Form("gpt-4o", description="gpt model 기본값 gpt-4o"),
        input_type : int = Form(1, description="사전확보정보 유형 - 파일 : 1, 텍스트 : 2"),
        input_text : str = Form(None, description="사전확보정보 텍스트 내용(input_type = 2인 경우 입력)"),
        interview_question : str = Form(description="생성된 질의문 리스트 ex) [\"질문1\", \"질문2\", \"질문3\"]"),
        uploaded_file : UploadFile = File(None, description="사전확보정보 파일(input_type = 1인 경우 입력)"),
        file_name : str = Form(None, description="사전확보정보 파일명")
        ):
    return service.add_interview(
        model_name,
        input_type,
        input_text,     
        interview_question,
        uploaded_file,
        file_name
        )

@router.post(
        path = "/tone", 
        description="취재질의 톤변경 API"
        +"<br>interview_question : 질의문 - [\"질문1\", \"질문2\", \"질문3\"]"
        +"<br>interview_tone : 질의문톤 - 공식적, 친화적, 비판적, 전문적, 의심적"
        )
def add_interview(data : InterviewToneRequestModel = Body()):
    return service.tone_interview(  
        data
        )
