'''
Author: GimTaeGyun gtgyun@bflysoft.com
Date: 2024-08-22 15:53:27
LastEditors: GimTaeGyun gtgyun@bflysoft.com
LastEditTime: 2024-09-12 11:36:47
'''
from typing import Generic, Type, TypeVar
from jcopilot.util.logger import Logger
from jcopilot.model.CommonCode import CommonCode

from sqlalchemy.exc import OperationalError, DatabaseError
import json

logger = Logger.getInstance()

T = TypeVar('T')

class BaseResponseModel(Generic[T]):

    def __init__(self, code : CommonCode, result : T = None):
        
        if isinstance(result, Exception):
            self.handle_exception(code, result)
        else:
            if result != None:
                self.code = code.code
                self.msg = code.msg
                self.result = result
            else:
                self.code = code.code
                self.msg = code.msg

    def handle_exception(self, code : CommonCode, e : Exception):
        self.code = code.code
        self.msg = code.msg
        if isinstance(e, DatabaseError):
            self.set_system_code(CommonCode.SYS_DB_ERROR, e)
        elif isinstance(e, OperationalError):
            self.set_system_code(CommonCode.SYS_DB_ERROR_OPER, e)
        elif isinstance(e, json.JSONDecodeError):            
            self.set_system_code(CommonCode.COMMON_CHK_JSON_PARSING, e)
        else:
            self.set_system_code(CommonCode.COMMON_FAIL, e)
    
    def set_system_code(self, code : CommonCode, e : Exception):
        self.sys_code = code.code
        self.sys_msg = f"{code.msg}:" + str(e)
        logger.info(self.sys_msg)