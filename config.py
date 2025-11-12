# /config.py
import os

# Pega o diretório base do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configurações base da aplicação."""
    
    # Chave secreta para segurança de sessões e formulários
    # Em produção, use uma variável de ambiente!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'
    
    # Configuração do Banco de Dados SQLite
    # Salva o arquivo 'app.db' na pasta 'instance'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    
    # Desativa um 'signal' do SQLAlchemy que não usaremos
    SQLALCHEMY_TRACK_MODIFICATIONS = False