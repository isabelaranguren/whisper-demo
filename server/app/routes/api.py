import logging 
import os 
from app.config import Config
from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.utils import secure_filename
from app.transcription.whisper_service import WhisperService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

whisper_service = None

@api.before_request
def start_services():
    global whisper_service
    
    model_key = session.get('selected_model', Config.DEFAULT_WHISPER_MODEL)
    
    if whisper_service is None or whisper_service.model_key != model_key:
        whisper_service = WhisperService(model_key)
        
@api.route('/models', methods=['GET'])
def get_models():
    models = WhisperService.get_available_models()
    curr_model = session.get('selected_model', Config.DEFAULT_WHISPER_MODEL)
    return jsonify({
        'models': models,
        'current_model': curr_model
    })

@api.route('/test', methods=['GET'])
def test_api():
    return jsonify({"message": "API is working!"})
    
@api.route('/models/select', methods=['POST'])
def select_model():
    data = request.get_json()
    model_key = data.get('model')
    if not model_key:
        return jsonify({'error':'no model specified'}), 400
    
    available_models = WhisperService.get_available_models()
    if model_key not in available_models:
        return jsonify({'error': 'Invalid model specified'}), 400
    
    session['selected_model'] = model_key
    
    global whisper_service
    whisper_service = None
    
    return jsonify({
        'success': True, 
        'model': model_key,
    })
    
@api.route('/settings', methods=['GET'])
def get_settings():

    settings = {
        'enablePreprocessing': Config.ENABLE_AUDIO_PREPROCESSING,
        'enableVAD': Config.ENABLE_VAD
    }
    
    return jsonify({
        'settings': settings
    })
    

@api.route('/settings', methods=['POST'])
def update_settings():
    
    data = request.get_json()
    settings = data.get('settings', {})
    
    if 'enablePreprocessing' in settings:
        Config.ENABLE_VAD = settings['enabled']
        
    global whisper_service
    whisper_service = None
    
    return jsonify({
        'success': True,
        'message': 'Settings updated successfully',
        'settings': {
            'enablePreprocessing': Config.ENABLE_AUDIO_PREPROCESSING,
            'enableVAD': Config.ENABLE_VAD
        }
    })
    


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@api.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio using the selected Whisper model.
    Handles various audio sources: file upload, URL, or microphone data.
    """
    start_services()
    
    # Check source type
    source_type = request.form.get('source_type')
    
    try:
        if source_type == Config.AUDIO_SOURCES['FILE_UPLOAD']:
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Ensure the upload folder exists
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            
            # Save to temporary file and transcribe
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Transcribe the file
            transcription = whisper_service.transcribe_audio_file(file_path)
            
            # Remove temporary file
            os.remove(file_path)
            
        elif source_type == Config.AUDIO_SOURCES['URL']:
            # Handle URL
            url = request.form.get('url')
            if not url:
                return jsonify({'error': 'No URL provided'}), 400
                
            transcription = whisper_service.transcribe_from_url(url)
            
        elif source_type == Config.AUDIO_SOURCES['MICROPHONE']:
            # Handle microphone data
            if 'audio_data' not in request.files:
                return jsonify({'error': 'No audio data provided'}), 400
                
            audio_data = request.files['audio_data'].read()
            transcription = whisper_service.transcribe_from_microphone(audio_data)
            
        else:
            return jsonify({'error': 'Invalid source type'}), 400
            
        # Return the transcription
        return jsonify({
            'transcription': transcription,
            'model_used': whisper_service.model_key
        })
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return jsonify({'error': f'Error transcribing audio: {str(e)}'}), 500


@api.route('/analyze', methods=['POST'])
def analyze_transcript():
    """
    Analyze a transcript using GPT to extract key points, action items, and summary.
    This is a placeholder for future implementation.
    """
    data = request.get_json()
    transcript = data.get('transcript')
    
    if not transcript:
        return jsonify({'error': 'No transcript provided'}), 400
    
    # For now, return a simple analysis
    # In a complete implementation, this would call a GPT service
    return jsonify({
        'summary': 'GPT analysis not yet implemented. This would provide a summary of the transcript.',
        'key_points': ['This is a placeholder for key points extracted from the transcript.'],
        'action_items': ['This is a placeholder for action items extracted from the transcript.']
    })

    
    


    