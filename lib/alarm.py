from lib import handler

class AlarmStatusHandler(handler.Handler):
    def get(self):
        gpio_pin = None
        try:
            gpio_pin = self._registry['config'].getint('gpio.alarm.armed.read')
        except ValueError:
            pass
        
        if not gpio_pin:
            raise Exception('Configuration not set: gpio.alarm.armed.read')
            
        self.write({'armed': True})