import signal
import sys
from lib.bootstrap import Bootstrap
import RPi.GPIO as GPIO
import time
 
def signal_term_handler(signal, frame):
    print 'GPIO Cleanup...'
    GPIO.cleanup()
    sys.exit(0)
 
#Catch kill signal so we can do GPIO cleanup
signal.signal(signal.SIGTERM, signal_term_handler)

bootstrap = Bootstrap('default', ['config', 'log'])
registry = bootstrap.bootstrap()

bell_gpio_pin = None
try:
    bell_gpio_pin = registry['config'].getint('gpio.bell', None)
except ValueError:
    #if configured value is not a valid integer
    pass

if not bell_gpio_pin:
    raise Exception('Configuration not set: gpio.bell')
    
light_gpio_pin = None
try:
    light_gpio_pin = registry['config'].getint('gpio.light', None)
except ValueError:
    #if configured value is not a valid integer
    pass

if not light_gpio_pin:
    raise Exception('Configuration not set: gpio.light')

print 'Configured pin values: '
print 'Bell pin: ' + str(bell_gpio_pin)
print 'Light pin: ' + str(light_gpio_pin)
raw_input("Press Enter to continue...")
 
# Use GPIO pin numbering scheme
GPIO.setmode(GPIO.BCM)

try:
    #run indefinitely
    while 1==1:
        #setup the bell GPIO pin as input and enable the pull up resistor
        GPIO.setup(bell_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print 'waiting for button press...'
        
        #blocks until the edge is detected
        GPIO.wait_for_edge(bell_gpio_pin, GPIO.FALLING) 
        
        #processing continues when edge is detected
        print 'button pressed, switching light on'
        
        #set up the light GPIO pin as an output
        GPIO.setup(light_gpio_pin, GPIO.OUT)

        #Switch the light on for 3 seconds
        GPIO.output(light_gpio_pin, GPIO.HIGH)
        time.sleep(3)
        
        print 'switching light off'

        #reset the GPIO pins to safe state       
        GPIO.cleanup()
        

except KeyboardInterrupt:
    print 'User interrupted'
except:
    registry['log'].exception('Caught Exception. ')
finally:
    GPIO.cleanup()
