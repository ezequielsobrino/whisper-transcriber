from flask import Flask, render_template, request, jsonify
import whisper
import yt_dlp
import os
import logging
from werkzeug.exceptions import InternalServerError
import time
import threading

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cargar el modelo de Whisper
logger.info("Cargando el modelo de Whisper...")
model = whisper.load_model("base")
logger.info("Modelo de Whisper cargado exitosamente.")

# Tiempos estimados de transcripción por modelo (en segundos por minuto de video)
TRANSCRIPTION_TIMES = {
    "base": 10,
    "medium": 5,
    "large": 3
}

# Variable global para almacenar el progreso
transcription_progress = 0


@app.route('/')
def index():
    return render_template('index.html')


def update_progress(duration, model_type):
    global transcription_progress
    estimated_time = duration * TRANSCRIPTION_TIMES[model_type] / 60
    for i in range(100):
        time.sleep(estimated_time / 100)
        transcription_progress = i + 1


@app.route('/transcribe', methods=['POST'])
def transcribe():
    global transcription_progress
    transcription_progress = 0

    url = request.json['url']
    model_type = request.json.get('model_type', 'base')
    logger.info(f"Iniciando transcripción para URL: {url} con modelo: {model_type}")

    try:
        # Configurar yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'audio.%(ext)s',
            'verbose': True,
            'no_warnings': False,
            'ignoreerrors': False,
            'quiet': False
        }

        # Descargar el audio del video
        logger.info("Descargando audio del video...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.debug(f"Opciones de yt-dlp: {ydl_opts}")
            try:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    raise ValueError("No se pudo extraer la información del video")
                logger.debug(f"Información extraída: {info}")
                duration = info['duration']
            except yt_dlp.DownloadError as e:
                logger.error(f"Error al descargar: {str(e)}")
                return jsonify({'error': str(e), 'status': 'error'}), 500
        logger.info("Audio descargado exitosamente.")

        # Verificar si el archivo de audio existe
        audio_file = next((f for f in os.listdir('.') if f.startswith('audio') and f.endswith('.mp3')), None)
        if not audio_file:
            raise FileNotFoundError("El archivo de audio no se descargó correctamente.")

        # Iniciar thread para actualizar el progreso
        progress_thread = threading.Thread(target=update_progress, args=(duration, model_type))
        progress_thread.start()

        # Transcribir el audio
        logger.info(f"Iniciando transcripción del audio: {audio_file}")
        result = model.transcribe(audio_file, verbose=True)
        logger.info("Transcripción completada.")

        # Asegurar que el progreso llegue al 100%
        transcription_progress = 100

        # Eliminar el archivo de audio descargado
        os.remove(audio_file)
        logger.info(f"Archivo de audio temporal eliminado: {audio_file}")

        return jsonify({'transcription': result["text"], 'status': 'success'})
    except Exception as e:
        logger.exception(f"Error durante la transcripción: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/progress')
def get_progress():
    return jsonify({'progress': transcription_progress})


@app.errorhandler(Exception)
def handle_exception(e):
    # Registrar el error
    app.logger.exception(f"Unhandled exception: {str(e)}")

    # Crear una respuesta JSON
    response = jsonify({
        "status": "error",
        "message": "An unexpected error occurred on the server.",
        "details": str(e)
    })

    # Si es un error HTTP conocido, usar su código de estado
    if isinstance(e, InternalServerError):
        response.status_code = 500
    else:
        response.status_code = 500  # 500 Internal Server Error por defecto

    return response


if __name__ == '__main__':
    app.run(debug=True)
