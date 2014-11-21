import requests
import json
import urllib


class XbmcClient():
    def __init__(self, host, port):
        self._url = "http://" + host + ":" + str(port) + "/jsonrpc"
        self._headers = {'content-type': 'application/json'}
        
    def _get_payload(self, method, params=None):
        payload = {"jsonrpc": "2.0", "id": 1}
        payload["method"] = method
        if params:
            payload["params"] = params
        return payload        
        
    def _do_get_request(self, payload):
        url_param = urllib.urlencode({'request': json.dumps(payload)})
        response = requests.get(self._url + '?' + url_param, 
                                data=json.dumps(payload), 
                                headers=self._headers)
        return json.loads(response.text)
        
    def _do_post_request(self, payload):
        response = requests.post(self._url, data=json.dumps(payload), 
                                 headers=self._headers)
        return json.loads(response.text)

    def get_speed(self, player_id):
        speed = None
        payload = self._get_payload("Player.GetProperties", {"playerid" : player_id, "properties" : ["speed"]})
        data = self._do_get_request(payload)
        if data["result"]:
            speed = data["result"]["speed"]
        return speed 
        
    def pause(self):
        payload = self._get_payload("Player.GetActivePlayers")
        data = self._do_get_request(payload)
        if data['result']:
            speed = self.get_speed(data['result'][0]["playerid"])
            if speed:
                payload = self._get_payload("Player.PlayPause", 
                                            {"playerid": 
                                            data['result'][0]["playerid"]})
                data = self._do_post_request(payload)

    
    def show_notification(self, title, message):
        payload = self._get_payload("GUI.ShowNotification", 
                                    {'title': title, 'message': message})
        self._do_post_request(payload)
    
    def execute_addon(self, addon_id):
        payload = self._get_payload("Addons.ExecuteAddon", {'addonid': addon_id})
        self._do_post_request(payload)
        