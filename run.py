# /run.py
from app import create_app, db
from app.models import User, ExpenseReport, Expense, Log # Importe seus modelos

# Cria a aplicação usando a "Factory Function"
app = create_app()

# Este contexto 'shell' facilita testar no terminal
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'ExpenseReport': ExpenseReport, 'Expense': Expense, 'Log': Log}

if __name__ == '__main__':
    # Inicia o servidor em modo 'debug' (reinicia a cada mudança)
    app.run(debug=True)