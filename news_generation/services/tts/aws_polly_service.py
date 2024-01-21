import configparser
from dotenv import load_dotenv
import boto3
import os
from newsX_backend.mappers.language_mapper import Languages

load_dotenv()

config = configparser.ConfigParser()
config.read('.config')

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_POLLY_REGION_NAME = config.get("AWS","AWS_POLLY_REGION_NAME")

class AWSPollyTTS:

    def __init__(self):
        try:
            self.polly_client = boto3.client(
                'polly',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_POLLY_REGION_NAME)
        except Exception as e:
            print(f'*** ERROR :: AWS Polly initialization failed due to: {e} *****')
            raise Exception(e)

    def __tts_english(self, text,output_path):
        try:
            tts_response = self.polly_client.synthesize_speech(Engine='neural',
                                            LanguageCode='en-US',
                                            OutputFormat='mp3',
                                            Text = text,
                                            VoiceId='Kimberly')

            print(tts_response)
            file = open(output_path, 'wb')
            file.write(tts_response['AudioStream'].read())
            file.close()
            return True
        except Exception as e:
            print(f'*** ERROR :: AWS Polly initialization failed due to: {e} *****')
            return False

    def __tts_hindi(self, text,output_path):
        try:
            tts_response = self.polly_client.synthesize_speech(
                Engine='neural',
                LanguageCode='hi-IN',
                OutputFormat='mp3',
                Text = text,
                VoiceId='Kajal')

            print(tts_response)
            file = open(output_path, 'wb')
            file.write(tts_response['AudioStream'].read())
            file.close()
            return True
        except Exception as e:
            print(f'*** ERROR :: AWS Polly initialization failed due to: {e} *****')
            return False

    def __tts_spanish(self, text,output_path):
        try:
            tts_response = self.polly_client.synthesize_speech(
                Engine='neural',
                LanguageCode='es-US',
                OutputFormat='mp3',
                Text = text,
                VoiceId='Lupe')

            print(tts_response)
            file = open(output_path, 'wb')
            file.write(tts_response['AudioStream'].read())
            file.close()
            return True
        except Exception as e:
            print(f'*** ERROR :: AWS Polly initialization failed due to: {e} *****')
            return False
    

    def perform_tts(self, text, language, output_path):
        if language == Languages.ENGLISH:
            return self.__tts_english(text, output_path)
        elif language == Languages.HINDI:
            return self.__tts_hindi(text,output_path)
        elif language ==Languages.SPANISH:
            return self.__tts_spanish(text, output_path)
        else:
            print(f'*** ERROR :: AWS Polly :: TTS failed due to: Langauge {language} not supported in AWS Polly *****')
            return False
