from lib import handler

try:
    #only available on the Raspberry Pi. 
    import RPi.GPIO as GPIO
except:
    #Rather let the GPIO code fail if called. 
    pass

class AlarmStatusHandler(handler.Handler):
    def get(self):
        gpio_pin = None
        try:
            gpio_pin = self._registry['config'].getint('gpio.alarm.armed.read')
        except ValueError:
            pass
        
        if not gpio_pin:
            raise Exception('Configuration not set: gpio.alarm.armed.read')
            
        # Use GPIO pin numbering scheme
        GPIO.setmode(GPIO.BCM)
        
        # Set up the GPIO channel
        GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # IS the alarm armed. Because of pull up resistor, a high value (1) 
        # means the alarm is armed and a low (0) value indicates it is not 
        is_armed = GPIO.input(gpio_pin) == 0
        
        GPIO.cleanup()

        self.write({'armed': is_armed})