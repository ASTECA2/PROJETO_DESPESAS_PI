from flask import render_template, redirect, url_for, flash, abort, request, send_file
from io import BytesIO
from fpdf import FPDF
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.main.forms import ReportForm, ExpenseForm
from app.models import ExpenseReport, Expense

# --- ROTA RAIZ (Redireciona) ---
@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

# --- DASHBOARD (A rota que estava faltando!) ---
@bp.route('/dashboard')
@login_required
def dashboard():
    # Mostra apenas relatórios ativos (não arquivados)
    reports = ExpenseReport.query.filter_by(author=current_user, is_archived=False)\
        .order_by(ExpenseReport.created_date.desc()).all()
    
    return render_template('index.html', title='Dashboard', reports=reports)

# --- RELATÓRIOS ARQUIVADOS ---
@bp.route('/archived')
@login_required
def archived_reports():
    reports = ExpenseReport.query.filter_by(author=current_user, is_archived=True)\
        .order_by(ExpenseReport.created_date.desc()).all()
    
    return render_template('archived.html', title='Relatórios Arquivados', reports=reports)

# --- CRIAR RELATÓRIO ---
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

# --- VISUALIZAR RELATÓRIO E ADICIONAR DESPESAS ---
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

# --- GERAR PDF (USANDO FPDF2 - Compatível com Vercel) ---
@bp.route('/report/<int:report_id>/pdf')
@login_required
def download_pdf(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)

    expenses = report.expenses.order_by(Expense.date.asc()).all()
    total = sum(e.amount for e in expenses)

    # Configuração do PDF manual
    class PDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 16)
            self.cell(0, 10, f'Relatório: {report.title}', border=False, new_x="LMARGIN", new_y="NEXT", align='C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(100, 10, "Descrição", border=1, fill=True)
    pdf.cell(40, 10, "Data", border=1, fill=True)
    pdf.cell(50, 10, "Valor (R$)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    # Linhas
    for expense in expenses:
        pdf.cell(100, 10, expense.description, border=1)
        data_str = expense.date.strftime('%d/%m/%Y') if expense.date else "-"
        pdf.cell(40, 10, data_str, border=1)
        pdf.cell(50, 10, f"R$ {expense.amount:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

    # Total
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(140, 10, "TOTAL GERAL:", border=0, align='R')
    pdf.cell(50, 10, f"R$ {total:.2f}", border=1, align='C')

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    filename = f"relatorio_{report.id}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

# --- ARQUIVAR ---
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

# --- DESARQUIVAR ---
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

# --- EXCLUIR ---
@bp.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)
    
    Expense.query.filter_by(report_id=report.id).delete()
    db.session.delete(report)
    db.session.commit()
    flash('Relatório excluído permanentemente.', 'success')
    
    return redirect(request.referrer or url_for('main.dashboard'))