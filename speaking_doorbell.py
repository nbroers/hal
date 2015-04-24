from lib.bootstrap import Bootstrap
from lib import xbmc, mail, camera, pushover
import RPi.GPIO as GPIO
import requests
from concurrent.futures import ThreadPoolExecutor

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

email_client = mail.EmailClient(registry["config"].get('email.host'), registry["config"].get('email.port'), 
                                 registry["config"].get('email.username'), registry["config"].get('email.password'),
                                 registry["config"].get('email.from_address'))

email_recipients = registry["config"].get('email.recipients')

camera_client = camera.CameraClient(registry["config"].get('frontdoor_camera.snapshot.url'), 
                                    registry["config"].get('frontdoor_camera.snapshot_directory'))

pushover_client = pushover.PushoverClient(registry['config'].get('pushover.api_token'), 
                                          registry['config'].get('pushover.user_keys'))

text = 'There is a visitor at the front door'

#We'll use a thread pool so that we can process multiple requests in parallel
thread_pool = ThreadPoolExecutor(20)

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

                thread_pool.submit(xbmc_client.pause)
                thread_pool.submit(xbmc_client.show_notification, 'Ding dong!', text)
                thread_pool.submit(xbmc_client.execute_addon, "script.frontdoorcam")
                
            for host_details in text_to_speech_hosts:
                host, port = host_details.split(':')
                url = 'http://' + host + ':' + str(port) + '/text_to_speech'
                payload = {"text": text}
                thread_pool.submit(requests.post, url, payload)
       
            thread_pool.submit(pushover_client.send, 'There is a visitor at the front door!', None, None, "bike")
                
            try:
                snapshot_path = camera_client.take_snapshot()
            except:
                registry['log'].exception('Caught Exception while taking snapshot. ')
                snapshot_path = None
                
            if snapshot_path:
                try:
                    email_client.send(email_recipients, 'There is someone at the front door', '', snapshot_path)
                except:
                    registry['log'].exception('Caught Exception while emailing snapshot. ')
                    
        except:
            registry['log'].exception('Caught exception in main loop. ')
        
        #reset the GPIO pins to safe state       
        GPIO.cleanup()

except KeyboardInterrupt:
    print 'User interrupted'
except:
    registry['log'].exception('Caught Exception. ')
finally:
    GPIO.cleanup()