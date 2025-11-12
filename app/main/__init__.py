# /app/main/__init__.py
from flask import Blueprint

bp = Blueprint('main', __name__)

# Importar as rotas no final para evitar importações circulares
from app.main import routes