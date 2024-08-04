from flask import Blueprint, jsonify, request, current_app, render_template
from ..services.transcription_service import transcribe_video, get_transcription_files, get_transcription_content

bp = Blueprint('transcription', __name__, url_prefix='/transcription')

@bp.route('/transcribe', methods=['POST'])
def transcribe():
    url = request.json['url']
    model_type = request.json.get('model_type', 'base')
    return transcribe_video(url, model_type)

@bp.route('/files')
def list_files():
    files = get_transcription_files()
    return render_template('transcriptions.html', files=files)

@bp.route('/content/<filename>')
def get_content(filename):
    content = get_transcription_content(filename)
    return jsonify({'content': content})

@bp.route('/progress')
def get_progress():
    # Implementar la lógica para obtener el progreso
    return jsonify({'progress': 0})  # Placeholder