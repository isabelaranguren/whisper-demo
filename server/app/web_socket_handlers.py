import base64
import logging
from flask_socketio import emit
from app import socketio
from app.transcription import whisper_service

logger = logging.getLogger(__name__)

@socketio.on('start_recording')
def handle_start_recording(data):
    recording_id = data.get('recording_id', 'unknown')
    logger.info(f'Start recording: {recording_id}')
    socketio.emit('recording_started', {'status': 'success', 'recording_id': recording_id})

@socketio.on('stop_recording')
def handle_stop_recording(data):
    recording_id = data.get('recording_id', 'unknown')
    logger.info(f'Stop recording: {recording_id}')
    socketio.emit('recording_stopped', {'status': 'success', 'recording_id': recording_id})

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """
    Receives audio chunks from WebSocket, processes them with Whisper, and returns transcription.
    """
    try:
        audio_bytes = base64.b64decode(data["audio"])
        transcription = whisper_service.transcribe_audio_chunk(audio_bytes)
        emit("transcription_result", {"text": transcription})
    
    except Exception as e:
        logging.error(f"Error processing audio chunk: {e}")
        emit("transcription_result", {"error": str(e)})