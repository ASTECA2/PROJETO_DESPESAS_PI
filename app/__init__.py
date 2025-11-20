from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Cria as extensões
db = SQLAlchemy()
login = LoginManager()
csrf = CSRFProtect()

login.login_view = 'auth.login'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Cria a pasta temporária se não existir
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicia as extensões
    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)

    # Registra os Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # --- FORÇA A CRIAÇÃO DO BANCO ---
    with app.app_context():
        # Importa os modelos AQUI para garantir que o SQLAlchemy os veja
        from app import models  
        
        # Imprime no log para sabermos que tentou criar
        print("Tentando criar tabelas no banco de dados...")
        db.create_all()
        print("Tabelas criadas com sucesso!")
    # --------------------------------

    return app