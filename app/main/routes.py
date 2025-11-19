from flask import render_template, redirect, url_for, flash, abort, Response, request, send_file
from io import BytesIO
from fpdf import FPDF  # <--- Importação nova
from app.main import bp
from flask_login import login_required, current_user
# ... (mantenha seus outros imports de forms e models)

# ... (mantenha as outras rotas iguais) ...

@bp.route('/report/<int:report_id>/pdf')
@login_required
def download_pdf(report_id):
    report = ExpenseReport.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)

    expenses = report.expenses.order_by(Expense.date.asc()).all()
    total = sum(e.amount for e in expenses)

    # --- CRIAÇÃO DO PDF COM FPDF2 (PURO PYTHON) ---
    class PDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 16)
            self.cell(0, 10, f'Relatório: {report.title}', border=False, new_x="LMARGIN", new_y="NEXT", align='C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

    # Inicializa o PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(100, 10, "Descrição", border=1, fill=True)
    pdf.cell(40, 10, "Data", border=1, fill=True)
    pdf.cell(50, 10, "Valor (R$)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    # Linhas da Tabela
    for expense in expenses:
        pdf.cell(100, 10, expense.description, border=1)
        # Formata a data se existir
        data_str = expense.date.strftime('%d/%m/%Y') if expense.date else "-"
        pdf.cell(40, 10, data_str, border=1)
        pdf.cell(50, 10, f"R$ {expense.amount:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

    # Total
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(140, 10, "TOTAL GERAL:", border=0, align='R')
    pdf.cell(50, 10, f"R$ {total:.2f}", border=1, align='C')

    # Salva na memória
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