import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.transcription.whisper_service import WhisperService
from app.config import Config

def test_basic_transcription():
    """Test basic audio file transcription."""
    print("Creating WhisperService with 'tiny' model for faster testing...")
    service = WhisperService("tiny")
    
    # You'll need a test audio file - create or download a short one
    test_file = "message.mp3"  # Put a short audio file in your project folder
    
    if not os.path.exists(test_file):
        print(f"Error: Test file {test_file} not found")
        return
    
    print(f"Transcribing file: {test_file}")
    try:
        result = service.transcribe_audio_file(test_file)
        print("Transcription successful!")
        print("Result:", result)
    except Exception as e:
        print(f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    test_basic_transcription()