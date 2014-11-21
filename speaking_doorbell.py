from lib.bootstrap import Bootstrap
from lib import xbmc
import signal
import sys
import RPi.GPIO as GPIO
import requests

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

xbmc_hosts = registry["config"].get('xbmc.hosts')
text_to_speech_hosts = registry["config"].get('text_to_speech.hosts')

text = 'There is a visitor at the front door'

# Use GPIO pin numbering scheme
GPIO.setmode(GPIO.BCM)

try:
    #run indefinitely
    while 1==1:
        #setup the bell GPIO pin as input and enable the pull up resistor
        GPIO.setup(bell_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        #blocks until the edge is detected
        GPIO.wait_for_edge(bell_gpio_pin, GPIO.FALLING) 

        try:
            for host_details in xbmc_hosts:
                host, port = host_details.split(':')
                xbmc_client = xbmc.XbmcClient(host, port)
                try:
                    xbmc_client.pause()
                    xbmc_client.show_notification('Ding dong!', text)
                    xbmc_client.execute_addon("script.frontdoorcam")
                except:
                    #Do not stop processing if XBMC is not running
                    pass
                
            for host_details in text_to_speech_hosts:
                host, port = host_details.split(':')
                url = 'http://' + host + ':' + str(port) + '/text_to_speech'
                payload = {"text": text}
                requests.post(url, payload)
        except:
            registry['log'].exception('Caught Exception while pausing xbmc and playing sound. ')
        
        #reset the GPIO pins to safe state       
        GPIO.cleanup()

except KeyboardInterrupt:
    print 'User interrupted'
except:
    registry['log'].exception('Caught Exception. ')
finally:
    GPIO.cleanup()