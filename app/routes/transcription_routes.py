from flask import Blueprint, jsonify, request, current_app, render_template
import logging

from app.services.transcription_service import VideoTranscriptionService

logger = logging.getLogger(__name__)

bp = Blueprint('transcription', __name__, url_prefix='/transcription')
service = VideoTranscriptionService()

def init_app(app):
    service.init_app(app)

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
    
    logger.info(f"Añadiendo a la cola de transcripción - URL: {url}, Modelo: {model_type}, English Only: {english_only}")
    
    try:
        task_id = service.queue_service.add_task(url, model_type, english_only)
        logger.info(f"Tarea añadida a la cola con ID: {task_id}")
        return jsonify({'task_id': task_id, 'status': 'queued'})
    except Exception as e:
        logger.error(f"Error al añadir la tarea a la cola: {str(e)}")
        return jsonify({'error': 'Error al procesar la solicitud', 'status': 'error'}), 500

@bp.route('/status/<task_id>')
def get_status(task_id):
    status = service.queue_service.get_task_status(task_id)
    if status:
        return jsonify(status)
    return jsonify({'error': 'Tarea no encontrada', 'status': 'error'}), 404

@bp.route('/queue')
def get_queue():
    tasks = service.queue_service.get_all_tasks()
    return jsonify(tasks)

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