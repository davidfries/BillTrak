from logging import Handler
from backend import BTBackend
class LogHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        
    def emit(self,record):
        db=BTBackend()
        try:
           db.logevent(record)
        except Exception as e:
            print(e)