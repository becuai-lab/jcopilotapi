import os
import platform
import logging
from logging import handlers
from datetime import datetime

class Logger :

    __instance = None
    __logwriter = None

    def __init__(self) :

        pass

    @classmethod
    def getInstance(cls) :

        if not cls.__instance :
            cls.__instance = Logger()

        return cls.__instance

    def setPath(self, logpath) :
            
        self.__logwriter = logging.getLogger(__name__)
        
        if "Windows" == platform.system() :
            
            if not os.path.exists(logpath + "\\log") :
                os.makedirs(logpath + "\\log")

            logfile = logpath + "\\log\\agent.log"
        else :

            if not os.path.exists(logpath + "/log") :
                os.makedirs(logpath + "/log")

            logfile = logpath + "/log/agent.log"

        streamhandler = logging.StreamHandler()
        filehandler = handlers.TimedRotatingFileHandler(filename=logfile, when="midnight", interval=1, encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] %(message)s")
       
        streamhandler.setFormatter(formatter)
        filehandler.setFormatter(formatter)
        filehandler.suffix = "%Y-%m-%d"
        
        self.__logwriter.addHandler(streamhandler)
        self.__logwriter.addHandler(filehandler)

        self.__logwriter.setLevel(level=logging.INFO)

    def info(self, log) :

        try :
            self.__logwriter.info(log)
        except :
            pass
        
    def error(self, log) :
        
        try :
            self.__logwriter.error(log)
        except :
            pass
    def debug(self, log) :
        
        try :
            self.__logwriter.debug(log)
        except :
            pass
        
    def warning(self, log) :
    
        try :
            self.__logwriter.warning(log)
        except :
            pass

    