import os 
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from app.config import Config
from app.routes.api import api as api_blueprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app, resources={r"/*": {"origins": "*"}})

    socketio.init_app(app)
    
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'Meeting API is running'
        })

    return app  # Ensure the app instance is returned




app = create_app()  # Create the app instance using the create_app function

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on_error()  # Handles the default namespace
def handle_error(e):
    pass

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
    recording_id = data.get('recording_id', 'unknown')
    logger.info(f"Received audio chunk for meeting: {recording_id}")

    socketio.emit('transcription_update', {
        'recording_id': recording_id,
        'status': 'processing',
        'message': 'Audio chunk received. Real-time transcription not yet implemented.'
    })

if __name__ == '__main__':
    logger.info('Starting Transcription API server')
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

    
    
