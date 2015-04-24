import requests
from datetime import datetime

class CameraClient():
    def __init__(self, snapshot_url, destination_directory):
        self._snapshot_url = snapshot_url
        self._destination_directory = destination_directory
        
    def take_snapshot(self):
        response = requests.get(self._snapshot_url, stream=True, timeout=2)
        if not response.status_code == 200:
            raise Exception('Camera snapshot request returned error response code: ' \
                    + str(response.status_code))
        
        file_path = self._destination_directory + '/' + datetime.now().strftime('%Y%m%d_%H%M%S.jpg')
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content():
                f.write(chunk)
        return file_path
          