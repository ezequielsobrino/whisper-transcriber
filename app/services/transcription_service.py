import os
import re
import json
import whisper
import yt_dlp
import logging
from flask import current_app, jsonify

from app.config import Config
from app.services.queue_service import QueueService

class VideoTranscriptionService:
    def __init__(self, app=None):
        self.logger = logging.getLogger(__name__)
        self.AVAILABLE_MODELS = {
            "tiny": ["tiny", "tiny.en"],
            "base": ["base", "base.en"],
            "small": ["small", "small.en"],
            "medium": ["medium", "medium.en"],
            "large": ["large"]
        }
        self.app = app
        self.transcriptions_folder = None
        if app is not None:
            self.init_app(app)
        self.queue_service = QueueService(self)

    def init_app(self, app):
        self.app = app

    def get_transcriptions_folder(self):
        config = Config()
        return config.TRANSCRIPTIONS_FOLDER

    def load_whisper_model(self, model_name):
        self.logger.info(f"Cargando el modelo de Whisper: {model_name}")
        model = whisper.load_model(model_name)
        self.logger.info(f"Modelo de Whisper {model_name} cargado exitosamente.")
        return model

    def sanitize_filename(self, filename):
        return re.sub(r'[^\w\-_\. ]', '_', filename)

    def transcribe_video(self, url, model_type='base', english_only=False):
        self.logger.info(f"Iniciando transcripción para URL: {url} con modelo: {model_type}, English only: {english_only}")

        try:
            if english_only and model_type != "large":
                model_name = f"{model_type}.en"
            else:
                model_name = model_type

            if model_name not in [m for models in self.AVAILABLE_MODELS.values() for m in models]:
                raise ValueError(f"Modelo no válido: {model_name}")

            model = self.load_whisper_model(model_name)

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

            self.logger.info("Descargando audio del video...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.debug(f"Opciones de yt-dlp: {ydl_opts}")
                try:
                    info = ydl.extract_info(url, download=True)
                    if info is None:
                        raise ValueError("No se pudo extraer la información del video")
                    self.logger.debug(f"Información extraída: {info}")
                    video_info = {
                        'title': info['title'],
                        'channel': info['channel'],
                        'url': url,
                        'description': info.get('description', 'No hay descripción disponible'),
                        'model': model_name,
                        'english_only': english_only
                    }
                except yt_dlp.DownloadError as e:
                    self.logger.error(f"Error al descargar: {str(e)}")
                    return jsonify({'error': str(e), 'status': 'error'}), 500
            self.logger.info("Audio descargado exitosamente.")

            audio_file = next((f for f in os.listdir('.') if f.startswith('audio') and f.endswith('.mp3')), None)
            if not audio_file:
                raise FileNotFoundError("El archivo de audio no se descargó correctamente.")

            self.logger.info(f"Iniciando transcripción del audio: {audio_file}")
            result = model.transcribe(audio_file, verbose=True)
            self.logger.info("Transcripción completada.")

            transcriptions_folder = self.get_transcriptions_folder()
            os.makedirs(transcriptions_folder, exist_ok=True)

            safe_filename = self.sanitize_filename(video_info['title'])
            transcription_file = os.path.join(transcriptions_folder, f"{safe_filename}_{model_name}.txt")

            # Guardar la información del video
            info_file = os.path.join(transcriptions_folder, f"{safe_filename}_{model_name}_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(video_info, f, ensure_ascii=False, indent=4)

            with open(transcription_file, 'w', encoding='utf-8') as f:
                f.write(result["text"])
            self.logger.info(f"Transcripción guardada en: {transcription_file}")

            os.remove(audio_file)
            self.logger.info(f"Archivo de audio temporal eliminado: {audio_file}")

            return {
                'transcription': result["text"],
                'status': 'success',
                'file': transcription_file,
                'video_info': video_info
            }
        except Exception as e:
            self.logger.exception(f"Error durante la transcripción: {str(e)}")
            return jsonify({'error': str(e), 'status': 'error'}), 500  

    def get_transcription_files(self):
        transcriptions_folder = current_app.config['TRANSCRIPTIONS_FOLDER']
        files = [f for f in os.listdir(transcriptions_folder) if f.endswith('.txt')]
        return sorted(files, key=lambda x: os.path.getmtime(os.path.join(transcriptions_folder, x)), reverse=True)

    def get_transcription_content(self, filename):
        transcriptions_folder = current_app.config['TRANSCRIPTIONS_FOLDER']
        file_path = os.path.join(transcriptions_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Obtener la información del video
            info_file_path = file_path.rsplit('.', 1)[0] + '_info.json'
            if os.path.exists(info_file_path):
                with open(info_file_path, 'r', encoding='utf-8') as info_file:
                    video_info = json.load(info_file)
            else:
                video_info = {
                    'title': 'Información no disponible',
                    'channel': 'Desconocido',
                    'url': '#',
                    'description': 'No hay descripción disponible'
                }
            
            return content, video_info
        return "Transcripción no encontrada", {}