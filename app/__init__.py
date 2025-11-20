from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Instancia as extensões
db = SQLAlchemy()
login = LoginManager()
csrf = CSRFProtect()

login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)

    # Registra Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # --- O SEGREDO ESTÁ AQUI ---
    with app.app_context():
        # Importa os modelos para o SQLAlchemy conhecer as tabelas
        from app import models  # <--- ESSA LINHA É OBRIGATÓRIA
        
        # Agora sim, cria as tabelas (User, ExpenseReport, etc)
        db.create_all()
    # ---------------------------

    return app