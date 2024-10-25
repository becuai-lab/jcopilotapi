from enum import Enum


class CommonCode(Enum):
    # 공통
    COMMON_SUCCESS = ("0000", "성공")
    COMMON_FAIL = ("9999", "시스템 에러입니다. 관리자에게 문의해 주세요.")

    # 시스템 에러
    SYS_DB_ERROR = ("9000", "DB 오류가 발생했습니다.")
    SYS_DB_ERROR_OPER = ("9001", "DB 연결 및 운영 오류가 발생했습니다.")

    # 기타
    COMMON_CHK_MID = ("0010", "미디어ID 정보가 없습니다. 다시 확인해주세요.")
    COMMON_DATA_NONE = ("0020", "데이터가 존재하지 않습니다.")
    COMMON_CHK_FILETYPE = ("0021", "올바른 파일 형식이 아닙니다.")
    COMMON_CHK_FILESIZE = ("0022", "입력 가능 크기를 초과하였습니다.")
    COMMON_CHK_JSON_FORMAT = ("0023", "JSON 형식이 아닌 응답을 받았습니다.")
    COMMON_CHK_JSON_PARSING = ("0024", "JSON 파싱 중 오류가 발생했습니다.")
    COMMON_CHK_TYPE = ("0025", "올바른 타입이 아닙니다.")
    COMMON_CHK_FILEREAD = ("0026", "파일 읽기 실패")
    COMMON_CHK_CONTENT = ("0027", "내용이 존재하지 않습니다.")
    COMMON_CHK_FILE = ("0027", "파일이 존재하지 않습니다.")
    COMMON_CHK_STRLEN = ("0028", "문자열의 길이가 제한 범위를 벗어났습니다.")    
    COMMON_CHK_EXTRACTLEN = ("0029", "첨부파일 내 텍스트 길이가 제한 범위를 벗어났습니다. (10000자 이내)")    
    
    # Jcopilot 
    JCOPILOT_CHK_ENDPOINT = ("0900", "엔드포인트가 존재하지 않습니다.")
    JCOPILOT_DIFF_RETRY = ("0901", "비교 처리 중 오류가 발생했습니다. 다시 시도해 주세요.")
    
    # 질의생성
    INTERVIEW_CHK_INFOTYPE = ("1001", "사전확보정보 분류가 올바르지 않습니다")
    INTERVIEW_CHK_TONE = ("1002", "질의톤이 일치하지 않습니다")
    INTERVIEW_RES_FAIL = ("1999", "결과값에 문제가 있습니다. 원본데이터를 확인해주세요.")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg