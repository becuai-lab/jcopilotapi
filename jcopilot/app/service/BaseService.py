
import os
from jcopilot.util.logger import Logger
class BaseService:
    logger = None
    calculator = None
    
    def __init__(self):
        self.logger = Logger.getInstance() 
        
    def get_openai_key(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        return openai_key
    