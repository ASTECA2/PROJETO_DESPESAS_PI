from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect # <--- IMPORT NOVO
import os

# Instancia as extensões
db = SQLAlchemy()
login = LoginManager()
csrf = CSRFProtect() # <--- EXTENSÃO NOVA

login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)

    # Garante que a configuração seja carregada
    app.config.from_object(config_class)

    # Garante que a pasta 'instance' exista para o SQLite
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicializa as extensões
    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app) # <--- INICIALIZAÇÃO NOVA

    # --- REGISTRO DOS BLUEPRINTS ---
    
    # 1. Blueprint Principal
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # 2. Blueprint de Autenticação
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # --- CRIAÇÃO DO BANCO DE DADOS ---
    with app.app_context():
        db.create_all()

    return app