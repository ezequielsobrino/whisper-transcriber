from flask import Flask

from .config import Config
from .routes import main_routes, transcription_routes
import logging


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configurar logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Registrar blueprints
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(transcription_routes.bp, url_prefix='/transcription')

    # Ruta de prueba
    @app.route('/test')
    def test_route():
        return 'La aplicación está funcionando correctamente.'

    logger.info('Aplicación inicializada correctamente.')

    return app
