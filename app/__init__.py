from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Instancia as extensões
db = SQLAlchemy()
login = LoginManager()
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

    # --- REGISTRO DOS BLUEPRINTS (AQUI ESTAVA O PROBLEMA) ---
    
    # 1. Blueprint Principal (Dashboard, Index, Relatórios)
    # Não usamos url_prefix para que ele assuma a raiz '/'
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # 2. Blueprint de Autenticação (Login, Register)
    # Usamos url_prefix para organizar as URLs como /auth/login
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # --- CRIAÇÃO DO BANCO DE DADOS (ESSENCIAL PARA VERCEL) ---
    with app.app_context():
        # Isso cria as tabelas (User, ExpenseReport, etc) se não existirem.
        # Sem isso, o login falha porque a tabela 'user' não existe.
        db.create_all()

    return app