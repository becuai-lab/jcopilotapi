# JcopilotAPI

JCopilot - API 

# openai API KEY발급방법
```
https://platform.openai.com/api-keys
위 사이트 접근 후 우측 상단 Create new secret key 클릭후 나오는 key 복사하여
프로젝트 내 .env의 OPENAI_API_KEY 값으로 붙여넣기
```

## 실행 방법
```
[Windows]
uvicorn main:app --reload main:app --host=0.0.0.0 --port=8000 --workers=1
[Linux]
gunicorn --bind 0:8000 main:app --worker-class uvicorn.workers.UvicornWorker --workers 1
```

## API 호출 방법
* Swagger URL : http://[IP]:8000/docs

## VSCODE 실행 및 디버깅 방법
* .vscode > launch.json 파일 생성 후 아래 명시
```
{
    "name": "Python: FastAPI",
    "type": "python",
    "request": "launch",
    "module": "uvicorn",
    "args": ["main:app", "--reload", "--host=0.0.0.0", "--workers=1"],
    "jinja": true,
    "justMyCode": true
}
```
