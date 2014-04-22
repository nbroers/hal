from lib import handler

class AlarmStatusHandler(handler.Handler):
    def get(self):
        self.write({'armed': True})