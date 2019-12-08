from logging import Handler
from loggingbackend import LoggingBackend as LoggingBackend
class LogHandler(Handler):
    level=0
    def __init__(self):
        Handler.__init__(self)
        super(LogHandler,self).__init__()
        _levels = ('debug', 'info', 'warning', 'error', 'critical')
        
    def emit(self,record):
        db=LoggingBackend()
        try:
           db.logevent(record)
        except Exception as e:
            print(e)