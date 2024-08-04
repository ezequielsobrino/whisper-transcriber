import os
import re
import whisper
import yt_dlp
import logging
from flask import current_app, jsonify

logger = logging.getLogger(__name__)

# Cargar el modelo de Whisper
logger.info("Cargando el modelo de Whisper...")
model = whisper.load_model("base")
logger.info("Modelo de Whisper cargado exitosamente.")


def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '_', filename)


def transcribe_video(url, model_type='base'):
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
                video_title = info['title']
            except yt_dlp.DownloadError as e:
                logger.error(f"Error al descargar: {str(e)}")
                return jsonify({'error': str(e), 'status': 'error'}), 500
        logger.info("Audio descargado exitosamente.")

        # Verificar si el archivo de audio existe
        audio_file = next((f for f in os.listdir('.') if f.startswith('audio') and f.endswith('.mp3')), None)
        if not audio_file:
            raise FileNotFoundError("El archivo de audio no se descargó correctamente.")

        # Transcribir el audio
        logger.info(f"Iniciando transcripción del audio: {audio_file}")
        result = model.transcribe(audio_file, verbose=True)
        logger.info("Transcripción completada.")

        # Crear la carpeta 'transcriptions' si no existe
        transcriptions_folder = current_app.config['TRANSCRIPTIONS_FOLDER']
        os.makedirs(transcriptions_folder, exist_ok=True)

        # Sanitizar el nombre del video para usarlo como nombre de archivo
        safe_filename = sanitize_filename(video_title)
        transcription_file = os.path.join(transcriptions_folder, f"{safe_filename}.txt")

        # Guardar la transcripción en un archivo
        with open(transcription_file, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        logger.info(f"Transcripción guardada en: {transcription_file}")

        # Eliminar el archivo de audio descargado
        os.remove(audio_file)
        logger.info(f"Archivo de audio temporal eliminado: {audio_file}")

        return jsonify({'transcription': result["text"], 'status': 'success', 'file': transcription_file})
    except Exception as e:
        logger.exception(f"Error durante la transcripción: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


def get_transcription_files():
    transcriptions_folder = current_app.config['TRANSCRIPTIONS_FOLDER']
    files = [f for f in os.listdir(transcriptions_folder) if f.endswith('.txt')]
    return sorted(files, key=lambda x: os.path.getmtime(os.path.join(transcriptions_folder, x)), reverse=True)


def get_transcription_content(filename):
    transcriptions_folder = current_app.config['TRANSCRIPTIONS_FOLDER']
    file_path = os.path.join(transcriptions_folder, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    return "Transcripción no encontrada"