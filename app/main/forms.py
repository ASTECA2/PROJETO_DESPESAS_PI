# /app/main/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField  # Importe DecimalField
from wtforms.validators import DataRequired, NumberRange

class ReportForm(FlaskForm):
    title = StringField('Título do Relatório', validators=[DataRequired()])
    submit = SubmitField('Criar Relatório')

# --- ADICIONE ESTE NOVO FORMULÁRIO ---
class ExpenseForm(FlaskForm):
    description = StringField('Descrição da Despesa', validators=[DataRequired()])
    amount = DecimalField('Valor (R$)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Adicionar Despesa')