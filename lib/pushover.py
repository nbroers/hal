import requests
import urllib

class PushoverClient():
    def __init__(self, api_token, user_keys):
        self._api_token = api_token
        self._user_keys = user_keys
        
    def send(self, message, url=None, url_title=None, sound=None):  
        url_parameters = {
            "token": self._api_token,
            "message": message,
        }        
        
        if url:
            url_parameters["url"] = url
        if url_title:
            url_parameters["url_title"] = url_title
        if sound:
            url_parameters["sound"] = sound
        
        for user_key in self._user_keys:
            url_parameters["user"] = user_key
            url = 'https://api.pushover.net/1/messages.json/?' + urllib.urlencode(url_parameters)
            response = requests.post(url)

        
