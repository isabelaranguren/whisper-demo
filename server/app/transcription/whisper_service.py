import os
import tempfile
import time
import logging
import whisper
import torch
from app.audio.audio_preprocessor import AudioPreprocessor
from app.config import Config

logger = logging.getLogger(__name__)

class WhisperService:
    """
    Service for transcribing audio using the open-source Whisper model.
    Includes audio preprocessing but no caching for simplicity.
    """
    
    # Class variable to store loaded models
    _loaded_models = {}
    
    def __init__(self, model_key=None):
        """Initialize the WhisperService with a specified model."""
        # Use default model if none specified
        self.model_key = model_key or Config.DEFAULT_WHISPER_MODEL
        
        # Check if the model key is valid
        if self.model_key not in Config.WHISPER_MODELS:
            logger.warning(f"Invalid model key: {self.model_key}. Using default model instead.")
            self.model_key = Config.DEFAULT_WHISPER_MODEL
            
        # Get model info
        self.model_info = Config.WHISPER_MODELS[self.model_key]
        logger.info(f"Using Whisper model: {self.model_info['name']}")
        
        # Load the model
        self.model = self._get_model(self.model_key)
        
        # Initialize audio preprocessor
        self.preprocessor = AudioPreprocessor(sample_rate=16000)
        
        # Load preprocessing settings from config
        self.enable_preprocessing = Config.ENABLE_AUDIO_PREPROCESSING
        self.enable_vad = Config.ENABLE_VAD
        
        logger.info(f"Audio preprocessing: {'Enabled' if self.enable_preprocessing else 'Disabled'}")
        logger.info(f"Voice activity detection: {'Enabled' if self.enable_vad else 'Disabled'}")
    
    @classmethod
    def _get_model(cls, model_key):
        """
        Get or load a model. Caches models to avoid reloading.
        
        Args:
            model_key (str): Key of the model to load
            
        Returns:
            whisper.Whisper: Loaded model
        """
        # Check if we've already loaded this model
        if model_key in cls._loaded_models:
            logger.info(f"Using cached model: {model_key}")
            return cls._loaded_models[model_key]
        
        # Check for CUDA availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Get model info
        model_info = Config.WHISPER_MODELS[model_key]
        
        # Determine actual model name to load (with .en suffix if needed)
        load_name = model_key
        if model_info['english_only'] and Config.WHISPER_ENGLISH_ONLY:
            load_name = f"{model_key}.en"
            
        # Load the model
        logger.info(f"Loading Whisper model: {load_name}")
        start_time = time.time()
        model = whisper.load_model(load_name, device=device)
        logger.info(f"Model loaded in {time.time() - start_time:.2f} seconds")
        
        # Cache the model
        cls._loaded_models[model_key] = model
        
        return model
    
    def transcribe_audio_file(self, file_path):
        """
        Transcribe an audio file with optional preprocessing.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            start_time = time.time()
            logger.info(f"Starting transcription for: {file_path}")
            
            # Apply preprocessing if enabled
            if self.enable_preprocessing:
                processed_path = self.preprocessor.preprocess_file(file_path)
                file_path_to_use = processed_path
                logger.info(f"Preprocessing completed in {time.time() - start_time:.2f}s")
            else:
                file_path_to_use = file_path
            
            # Apply VAD if enabled
            if self.enable_vad:
                # Read the file
                with open(file_path_to_use, 'rb') as f:
                    audio_bytes = f.read()
                
                # Detect speech segments
                segments = self.preprocessor.detect_voice_activity(audio_bytes)
                
                if segments:
                    logger.info(f"Detected {len(segments)} speech segments")
                    
                    # Prepare to collect transcriptions from each segment
                    segment_transcriptions = []
                    
                    for i, (start, end) in enumerate(segments):
                        logger.info(f"Transcribing segment {i+1}/{len(segments)}: {start:.2f}s to {end:.2f}s")
                        
                        # Use Whisper's built-in timestamp feature
                        options = {
                            "language": "en" if Config.WHISPER_ENGLISH_ONLY else None,
                            "task": "transcribe",
                            "fp16": torch.cuda.is_available(),
                            "time_stamps": True,  # Request timestamps in output
                        }
                        
                        result = self.model.transcribe(file_path_to_use, **options)
                        
                        # Filter to segments within our VAD bounds
                        filtered_segments = [
                            seg for seg in result["segments"] 
                            if (seg["start"] >= start and seg["end"] <= end) or
                               (seg["start"] <= end and seg["end"] >= start)
                        ]
                        
                        segment_text = " ".join([seg["text"] for seg in filtered_segments])
                        segment_transcriptions.append(segment_text)
                    
                    # Combine all segment transcriptions
                    transcription = " ".join(segment_transcriptions)
                else:
                    logger.warning("No speech segments detected, falling back to full transcription")
                    options = {
                        "language": "en" if Config.WHISPER_ENGLISH_ONLY else None,
                        "task": "transcribe",
                        "fp16": torch.cuda.is_available()
                    }
                    result = self.model.transcribe(file_path_to_use, **options)
                    transcription = result["text"]
            else:
                # Standard transcription without VAD
                options = {
                    "language": "en" if Config.WHISPER_ENGLISH_ONLY else None,
                    "task": "transcribe",
                    "fp16": torch.cuda.is_available()
                }
                result = self.model.transcribe(file_path_to_use, **options)
                transcription = result["text"]
            
            # Clean up temporary file if we created one
            if self.enable_preprocessing and file_path_to_use != file_path:
                os.unlink(file_path_to_use)
            
            # Log timing information
            total_time = time.time() - start_time
            logger.info(f"Transcription completed in {total_time:.2f}s")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    def transcribe_audio_chunk(self, audio_chunk, temp_format="wav"):
        try:
            if self.enable_preprocessing:
                processed_bytes = self.preprocessor.preprocess_bytes(audio_chunk)
                chunk_to_use = processed_bytes
            else:
                chunk_to_use = audio_chunk
            
            with tempfile.NamedTemporaryFile(suffix=f".{temp_format}", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(chunk_to_use)
            
            # Transcribe the file
            transcription = self.transcribe_audio_file(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio chunk: {str(e)}")
            raise
    
    def transcribe_from_url(self, url):
        try:
            logger.info(f"Downloading audio from URL: {url}")
            
            # Download the file with timeout
            import requests
            response = requests.get(
                url, 
                stream=True, 
                timeout=300  # 5 minutes timeout
            )
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
            
            # Transcribe the downloaded file
            transcription = self.transcribe_audio_file(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing from URL: {str(e)}")
            raise
    
    def process_real_time_audio(self, audio_stream, chunk_size=1024, sample_rate=16000):

        # Buffer to accumulate audio chunks
        buffer = []
        buffer_duration_ms = 0
        target_duration_ms = Config.AUDIO_CHUNK_DURATION * 1000  # Convert to milliseconds
        
        for chunk in audio_stream:
            buffer.append(chunk)
            
            # Calculate approximate duration
            chunk_duration_ms = (len(chunk) / 2) * 1000 / sample_rate
            buffer_duration_ms += chunk_duration_ms
            
            if buffer_duration_ms >= target_duration_ms:
                logger.info(f"Processing real-time audio chunk: {buffer_duration_ms/1000:.2f}s")
                
                # Concatenate chunks
                audio_data = b''.join(buffer)
                
                # Create a temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(audio_data)
                
                # Transcribe the temporary file
                try:
                    transcription = self.transcribe_audio_file(temp_path)
                    yield transcription
                except Exception as e:
                    logger.error(f"Error in real-time transcription: {str(e)}")
                    yield ""
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_path)
                
                # Reset buffer
                buffer = []
                buffer_duration_ms = 0
    
    @classmethod
    def get_available_models(cls):
        """Get information about available models."""
        return Config.WHISPER_MODELS