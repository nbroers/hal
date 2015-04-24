import smtplib
from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os


class EmailClient():
    def __init__(self, host, port, username, password, from_address):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_address = from_address
        
    def send(self, recipients, subject, message, image=None):       
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self._from_address
        
        text = MIMEText(message)
        msg.attach(text)
               
        if image:
            img_data = open(image, 'rb').read()
            
            image_data = MIMEImage(img_data, name=os.path.basename(image))
            msg.attach(image_data)
       
        server = smtplib.SMTP(self._host, self._port, None, 10) 
        server.ehlo()
        server.starttls()
        server.login(self._username, self._password)
        server.sendmail(self._from_address, recipients, msg.as_string())
        server.close()
          