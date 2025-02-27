import numpy as np
import librosa
import webrtcvad
import tempfile
import os
import logging
import soundfile as sf
from scipy.signal import butter, lfilter

logger = logging.getLogger(__name__)

class AudioPreprocessor:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
        logger.info(f"Initialized AudioPreprocessor with sample rate {sample_rate}Hz")
    
    def preprocess_file(self, file_path, output_path=None):
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            y = self._normalize_audio(y)
            y = self._reduce_noise(y)
            y = self._trim_silence(y)
        
            # Create output path if not provided
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    output_path = temp_file.name
            
            # Save processed audio
            sf.write(output_path, y, self.sample_rate)
            logger.info(f"Saved preprocessed audio to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise
        
    def _trim_silence(self, y, threshold_db=-40, min_silence_duration=0.5):
        """
        Remove silent parts from audio.
        
        Args:
            y: Audio signal
            threshold_db: Threshold for silence detection in dB
            min_silence_duration: Minimum silence duration in seconds
            
        Returns:
            Trimmed audio signal
        """
        # Convert threshold to linear scale
        threshold = librosa.db_to_amplitude(threshold_db)
        
        # Find non-silent intervals
        intervals = librosa.effects.split(
            y, 
            top_db=-threshold_db,
            frame_length=2048, 
            hop_length=512
        )
        
        # Only keep intervals that are longer than min_silence_duration
        min_samples = int(min_silence_duration * self.sample_rate)
        intervals = [i for i in intervals if (i[1]-i[0]) >= min_samples]
        
        # Concatenate non-silent intervals
        if len(intervals) == 0:
            return y  # Return original if no valid intervals
            
        y_trimmed = np.concatenate([y[start:end] for start, end in intervals])
        
        # Log statistics
        original_duration = len(y) / self.sample_rate
        trimmed_duration = len(y_trimmed) / self.sample_rate
        reduction = 100 * (original_duration - trimmed_duration) / original_duration
        
        logger.info(f"Trimmed silence: {original_duration:.2f}s → {trimmed_duration:.2f}s ({reduction:.1f}% reduction)")
        
        return y_trimmed
        
    def preprocess_bytes(self, audio_bytes):
        try:
            # Save bytes to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_in:
                temp_in_path = temp_in.name
                temp_in.write(audio_bytes)
            
            # Process the file
            temp_out_path = self.preprocess_file(temp_in_path)
            
            # Read the processed file
            with open(temp_out_path, 'rb') as f:
                processed_bytes = f.read()
            
            # Clean up temporary files
            os.unlink(temp_in_path)
            os.unlink(temp_out_path)
            
            return processed_bytes
            
        except Exception as e:
            logger.error(f"Error preprocessing audio bytes: {str(e)}")
            raise
    
    def _normalize_audio(self, y):
        return librosa.util.normalize(y)
    
    def _reduce_noise(self, y):
        noise_sample = y[:min(len(y), self.sample_rate)]
        
        # Compute FFT
        S_full = librosa.stft(y)
        magnitude = np.abs(S_full)
        phase = np.angle(S_full)
        
        # Compute noise profile
        noise_magnitude = np.abs(librosa.stft(noise_sample))
        noise_profile = np.mean(noise_magnitude, axis=1) * 2
        
        # Apply spectral gating
        magnitude_filtered = np.maximum(
            magnitude - noise_profile.reshape(-1, 1), 
            magnitude * 0.1  # Keep at least 10% to avoid artifacts
        )
        
        # Reconstruct signal
        S_filtered = magnitude_filtered * np.exp(1j * phase)
        y_filtered = librosa.istft(S_filtered)
        
        return y_filtered