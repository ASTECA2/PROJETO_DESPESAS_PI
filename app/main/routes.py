from flask import render_template, redirect, url_for, flash, abort, Response, request
import weasyprint
from app.main import bp
from flask_login import login_required, current_user

from app import db
from app.main.forms import ReportForm, ExpenseForm
from app.models import ExpenseReport, Expense

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    # Agora filtra para mostrar APENAS relatórios não arquivados
    reports = ExpenseReport.query.filter_by(author=current_user, is_archived=False)\
        .order_by(ExpenseReport.created_date.desc()).all()
    
    return render_template('index.html', title='Dashboard', reports=reports)


# --- ROTA NOVA PARA A PÁGINA DE ARQUIVADOS ---
@bp.route('/archived')
@login_required
def archived_reports():
    # Busca APENAS relatórios arquivados
    reports = ExpenseReport.query.filter_by(author=current_user, is_archived=True)\
        .order_by(ExpenseReport.created_date.desc()).all()
    
    return render_template('archived.html', title='Relatórios Arquivados', reports=reports)


@bp.route('/create_report', methods=['GET', 'POST'])
@login_required
def create_report():
    form = ReportForm()
    if form.validate_on_submit():
        report = ExpenseReport(title=form.title.data, author=current_user)
        db.session.add(report)
        db.session.commit()
        flash('Relatório criado com sucesso!', 'success')
        return redirect(url_for('main.view_report', report_id=report.id))
    
    return render_template('create_report.html', title='Novo Relatório', form=form)


@bp.route('/report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def view_report(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403) 

    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(description=form.description.data, 
                          amount=form.amount.data, 
                          report=report)
        db.session.add(expense)
        db.session.commit()
        flash('Despesa adicionada!', 'success')
        return redirect(url_for('main.view_report', report_id=report.id))

    expenses = report.expenses.order_by(Expense.date.asc()).all()
    total = sum(e.amount for e in expenses)
    
    return render_template('view_report.html', 
                           title=report.title, 
                           report=report, 
                           expenses=expenses,
                           total=total,
                           form=form)


@bp.route('/report/<int:report_id>/pdf')
@login_required
def download_pdf(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)

    expenses = report.expenses.order_by(Expense.date.asc()).all()
    total = sum(e.amount for e in expenses)

    html = render_template('report_pdf.html', 
                           report=report, 
                           expenses=expenses, 
                           total=total)
    
    pdf = weasyprint.HTML(string=html).write_pdf()

    filename = f"relatorio_{report.title.lower().replace(' ', '_')}_{report.id}.pdf"
    response = Response(pdf, mimetype='application/pdf')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


# --- ROTA NOVA PARA ARQUIVAR ---
@bp.route('/report/<int:report_id>/archive', methods=['POST'])
@login_required
def archive_report(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)
    
    report.is_archived = True
    db.session.commit()
    flash('Relatório arquivado.', 'success')
    return redirect(url_for('main.dashboard'))


# --- ROTA NOVA PARA DESARQUIVAR ---
@bp.route('/report/<int:report_id>/unarchive', methods=['POST'])
@login_required
def unarchive_report(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)
    
    report.is_archived = False
    db.session.commit()
    flash('Relatório restaurado para o dashboard.', 'success')
    return redirect(url_for('main.archived_reports'))


# --- ROTA NOVA PARA EXCLUIR ---
@bp.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)
    
    # Exclui todas as despesas primeiro
    Expense.query.filter_by(report_id=report.id).delete()
    
    # Exclui o relatório
    db.session.delete(report)
    db.session.commit()
    flash('Relatório excluído permanentemente.', 'success')
    
    # Redireciona para a página de onde veio (arquivados ou dashboard)
    return redirect(request.referrer or url_for('main.dashboard'))
