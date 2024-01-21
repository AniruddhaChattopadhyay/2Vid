
from firebase_admin import credentials, initialize_app, storage
import os
import configparser

config = configparser.ConfigParser()
config.read('.config')

FIREBASE_UPLOAD_ACTIVE = config.getboolean('FIREBASE', 'FIREBASE_UPLOAD_ACTIVE')

cred = credentials.Certificate("keys/newsx-201-firebase-adminsdk-trruk-b130fed6be.json")
GENERATED_VIDEO_PATH = 'newsx-201.appspot.com'




initialize_app(cred, {'storageBucket': GENERATED_VIDEO_PATH})

class UploadVideo():
    
    def __init__(self) -> None:    
        self.bucket = storage.bucket()

    def upload_video_to_storage(self, file_path):
        if FIREBASE_UPLOAD_ACTIVE:
            blob = self.bucket.blob(file_path)
            blob.upload_from_filename(file_path)
            blob.make_public()
            return blob.public_url
        else:
            return 'https://www.w3.org/Provider/Style/dummy.html'