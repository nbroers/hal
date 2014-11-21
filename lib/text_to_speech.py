from lib import handler
import pyttsx

class TextToSpeechHandler(handler.Handler):
    def post(self):
        text = self.get_argument('text')
        
        engine = pyttsx.init()
        
        engine.setProperty('rate', self._registry['config'].getint(
                    'text_to_speech.rate'))
                    
        engine.setProperty('volume', self._registry['config'].getfloat(
                    'text_to_speech.volume'))
                    
        voices = engine.getProperty('voices')
        for voice in voices:
            if voice.id.lower().find(self._registry['config'].get(
                    'text_to_speech.voice').lower()) != -1:
                engine.setProperty('voice', voice.id)

        engine.say(text)        
        engine.runAndWait()