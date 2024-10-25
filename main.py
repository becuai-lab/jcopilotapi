
import os, json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), encoding="utf-8")
from jcopilot.util.logger import Logger
logger = Logger.getInstance()
logger.setPath(os.getcwd())
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware

from jcopilot.app.domain import DraftController, InterviewController
from pyctuator.pyctuator import Pyctuator

import warnings
warnings.filterwarnings("ignore")
app = FastAPI(
    title="JCopilot API", # Swagger Title 설정
    description="JCopilot API", # Swagger Description 설정
    version=os.getenv("CONST_APP_VERSION"), # Program Version
    openapi_url="/jcopilot-openapi.json",
    docs_url='/jcopilot/docs',
    redoc_url='/jcopilot/redoc'    
    )  # FastAPI 객체 생성

origins = [
    "*",  # 모든 origin 허용
]

app.add_middleware(
    CORSMiddleware,  # CORS 미들웨어 추가
    allow_origins=origins,  # 모든 origin 허용
    allow_credentials=True,  # 자격증명 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.router.redirect_slashes = False # '/'때문에 redirect되는 부분 해제하는 코드
logger.info(f"App started")  # 로그 출력: "App started"
app.include_router(DraftController.router)  # segmentation 라우터 추가
app.include_router(InterviewController.router)  # segmentation 라우터 추가

pyctuator = Pyctuator(
    app,
    app_name="jcopilot-api",
    app_url=None,
    pyctuator_endpoint_url="/pyctuator",
    registration_url=None
)