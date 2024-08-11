from flask import Blueprint, jsonify, request, current_app, render_template
import logging

from app.services.transcription_service import VideoTranscriptionService

logger = logging.getLogger(__name__)

bp = Blueprint('transcription', __name__, url_prefix='/transcription')
service = VideoTranscriptionService()

@bp.route('/transcribe', methods=['POST'])
def transcribe():
    logger.info("Solicitud de transcripción recibida")
    data = request.json
    logger.debug(f"Datos recibidos: {data}")
    
    if not data or 'url' not in data:
        logger.error("URL no proporcionada")
        return jsonify({'error': 'URL no proporcionada', 'status': 'error'}), 400
    
    url = data['url']
    model_type = data.get('model_type', 'base')
    english_only = data.get('english_only', False)
    
    logger.info(f"Transcribiendo URL: {url}, Modelo: {model_type}, English Only: {english_only}")
    
    if model_type not in service.AVAILABLE_MODELS:
        logger.error(f"Modelo no válido: {model_type}")
        return jsonify({'error': 'Modelo no válido', 'status': 'error'}), 400
    
    if english_only and model_type == 'large':
        logger.error("El modelo 'large' no tiene versión 'English only'")
        return jsonify({'error': 'El modelo "large" no tiene versión "English only"', 'status': 'error'}), 400
    
    return service.transcribe_video(url, model_type, english_only)

@bp.route('/files')
def list_files():
    files = service.get_transcription_files()
    return render_template('transcriptions.html', files=files)

@bp.route('/content/<filename>')
def get_content(filename):
    content, video_info = service.get_transcription_content(filename)
    return jsonify({
        'content': content,
        'video_info': video_info
    })

@bp.route('/progress')
def get_progress():
    # Implementar la lógica para obtener el progreso
    return jsonify({'progress': 0})  # Placeholder