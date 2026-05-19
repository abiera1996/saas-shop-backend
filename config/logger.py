import json, logging
from logging import handlers

class CustomFileHandler(handlers.RotatingFileHandler):

    def emit(self, record): 
        if type(record.msg).__name__ == "dict":
            try:
                record.msg = f' -_- {json.dumps(record.msg)}'
            except:
                pass
        try:
            if self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except Exception:
            
            self.handleError(record)

        return record