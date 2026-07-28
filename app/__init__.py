from flask import Flask, render_template
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from .models import *
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env') # carrega o .env pra dentro das variáveis de ambiente do sistema

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    Migrate(app, db)

    from .main import main_bp
    from .chamado import chamado_bp
    from .usuario import usuario_bp
    from .setor import setor_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(chamado_bp)
    app.register_blueprint(setor_bp)

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def erro_servidor(erro):
        return render_template('500.html'), 500

    return app