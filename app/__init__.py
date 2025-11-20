# /app/__init__.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)

    # Garante que a pasta instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    # Adicione url_prefix para organizar, se quiser, mas opcional
    app.register_blueprint(auth_bp, url_prefix='/auth') 

    # --- CORREÇÃO CRÍTICA PARA SQLITE NA VERCEL ---
    with app.app_context():
        # Isso cria o arquivo app.db vazio se ele não existir
        db.create_all()
    # ----------------------------------------------

    return app