from lib import handler
import RPi.GPIO as GPIO

class AlarmStatusHandler(handler.Handler):
    def get(self):
        gpio_pin = None
        try:
            gpio_pin = self._registry['config'].getint('gpio.alarm.armed.read')
        except ValueError:
            pass
        
        if not gpio_pin:
            raise Exception('Configuration not set: gpio.alarm.armed.read')
            
        # use P1 header pin numbering convention
        GPIO.setmode(GPIO.BOARD)
        
        # Set up the GPIO channel
        GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # IS alarm armed
        is_armed = GPIO.input(gpio_pin)
        
        GPIO.cleanup()

        self.write({'armed': is_armed})