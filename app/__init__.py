# /app/__init__.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Cria as extensões "vazias"
db = SQLAlchemy()
login = LoginManager()

# --- ALTERAÇÕES AQUI ---
# Aponta o Flask-Login para a sua rota de login
login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'
# ------------------------


def create_app(config_class=Config):
    app = Flask(__name__)

    # --- ALTERAÇÃO AQUI ---
    # Garante que a pasta 'instance' (onde o app.db fica) exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # ------------------------

    app.config.from_object(config_class)

    # Inicializa as extensões com o app
    db.init_app(app)
    login.init_app(app)

    # Registra o seu blueprint principal
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # --- ALTERAÇÃO AQUI ---
    # Registra o blueprint de autenticação
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    # ------------------------
    
    with app.app_context():
        # (Não é mais necessário manter o 'pass' aqui)
        pass

    return app