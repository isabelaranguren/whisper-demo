from io import BytesIO
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
    
    def preprocess_file(self, file_path, output_path):
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            y = self._normalize_audio(y)
            y = self._apply_vad(y)
            y = self._trim_silence(y)
            y = self._reduce_noise(y)
            
            sf.write(output_path, y, self.sample_rate)
            logger.info(f"Saved preprocessed audio to: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise
    
    def preprocess_bytes(self, audio_bytes):
        try:
            audio_in = BytesIO(audio_bytes)
            y, sr = sf.read(audio_in, dtype='float32')
            
            y = self._normalize_audio(y)
            y = self._apply_vad(y)
            y = self._trim_silence(y)
            y = self._reduce_noise(y)
            
            audio_out = BytesIO()
            sf.write(audio_out, y, self.sample_rate, format="WAV")
            return audio_out.getvalue()
        except Exception as e:
            logger.error(f"Error preprocessing audio bytes: {str(e)}")
            raise
    
    def _apply_vad(self, y, frame_duration_ms=30):
        frame_size = int(self.sample_rate * frame_duration_ms / 1000)
        frames = [y[i:i+frame_size] for i in range(0, len(y), frame_size)]
        
        speech_frames = [f for f in frames if self.vad.is_speech(f.tobytes(), self.sample_rate)]
        
        return np.concatenate(speech_frames) if speech_frames else y
    
    def _trim_silence(self, y, threshold_db=-40):
        threshold = librosa.db_to_amplitude(threshold_db)
        intervals = librosa.effects.split(y, top_db=abs(threshold_db))
        
        if len(intervals) == 0:
            return y
        
        y_trimmed = np.concatenate([y[start:end] for start, end in intervals])
        
        original_duration = len(y) / self.sample_rate
        trimmed_duration = len(y_trimmed) / self.sample_rate
        reduction = 100 * (original_duration - trimmed_duration) / original_duration
        
        logger.info(f"Trimmed silence: {original_duration:.2f}s → {trimmed_duration:.2f}s ({reduction:.1f}% reduction)")
        
        return y_trimmed
    
    def _normalize_audio(self, y):
        return librosa.util.normalize(y)
    
    def _reduce_noise(self, y):
        noise_sample = y[:min(len(y), self.sample_rate)]
        
        S_full = librosa.stft(y)
        magnitude = np.abs(S_full)
        phase = np.angle(S_full)
        
        noise_magnitude = np.abs(librosa.stft(noise_sample))
        noise_profile = np.mean(noise_magnitude, axis=1) * 2
        
        magnitude_filtered = np.exp(np.log1p(magnitude) - np.log1p(noise_profile.reshape(-1, 1)))
        
        S_filtered = magnitude_filtered * np.exp(1j * phase)
        y_filtered = librosa.istft(S_filtered)
        
        return y_filtered
