import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    WHISPER_MODELS = {
        'tiny': {
            'name': 'Tiny',
            'description': 'Fastest, lowest accuracy (good for testing)',
            'size': '~75MB',
            'speed': 'Very Fast (32x real-time)',
            'english_only': True
        },
        'base': {
            'name': 'Base',
            'description': 'Good balance of speed and accuracy',
            'size': '~150MB',
            'speed': 'Fast (16x real-time)',
            'english_only': True
        },
        'small': {
            'name': 'Small',
            'description': 'Better accuracy, slower speed',
            'size': '~500MB',
            'speed': 'Medium (6x real-time)',
            'english_only': True
        },
        'medium': {
            'name': 'Medium',
            'description': 'High accuracy, significantly slower',
            'size': '~1.5GB',
            'speed': 'Slow (2x real-time)',
            'english_only': True
        },
        'large': {
            'name': 'Large',
            'description': 'Highest accuracy, slowest speed',
            'size': '~3GB',
            'speed': 'Very Slow (1x real-time)',
            'english_only': False
        }
    }
    
    DEFAULT_WHISPER_MODEL = os.getenv('DEFAULT_WHISPER_MODEL', 'base')
    WHISPER_ENGLISH_ONLY = os.getenv('WHISPER_ENGLISH_ONLY', 'True') == 'True'
    
     # Audio preprocessing settings
    ENABLE_AUDIO_PREPROCESSING = os.getenv('ENABLE_AUDIO_PREPROCESSING', 'True') == 'True'
    ENABLE_VAD = os.getenv('ENABLE_VAD', 'True') == 'True'
    VAD_AGGRESSIVENESS = int(os.getenv('VAD_AGGRESSIVENESS', '3'))  # 0-3, higher is more aggressive
    
    GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-3.5-turbo')
    
    AUDIO_CHUNK_DURATION = int(os.getenv('AUDIO_CHUNK_DURATION', '10'))  # in seconds
    
    AUDIO_SOURCES = {
        'MICROPHONE': 'microphone',
        'FILE_UPLOAD': 'file_upload',
        'URL': 'url'
    }
    
    MICROPHONE_SAMPLE_RATE = int(os.getenv('MICROPHONE_SAMPLE_RATE', '16000'))  # Hz
    MICROPHONE_CHANNELS = int(os.getenv('MICROPHONE_CHANNELS', '1'))  # Mono
    
    ALLOWED_URL_DOMAINS = os.getenv('ALLOWED_URL_DOMAINS', 'youtube.com,vimeo.com,drive.google.com').split(',')
    MAX_URL_DOWNLOAD_SIZE = int(os.getenv('MAX_URL_DOWNLOAD_SIZE', '100')) * 1024 * 1024  # 100 MB
    URL_DOWNLOAD_TIMEOUT = int(os.getenv('URL_DOWNLOAD_TIMEOUT', '300'))  # seconds
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'webm', 'm4a'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB