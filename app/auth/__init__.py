# /app/auth/__init__.py
from flask import Blueprint

# Cria o Blueprint.
# 'auth' é o nome
# template_folder='../templates/auth' diz onde procurar os HTMLs
bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# Importa as rotas no final para evitar dependência circular
from app.auth import routes