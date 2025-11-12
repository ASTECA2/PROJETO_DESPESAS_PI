# /app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp # Importa o Blueprint
from app.models import User # Importa o modelo de usuário

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já está logado, manda para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        # Valida o usuário e a senha
        if user is None or not user.check_password(password):
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        # Loga o usuário
        login_user(user, remember=request.form.get('remember_me'))
        flash('Login efetuado com sucesso!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not nome or not email or not password:
            flash('Todos os campos são obrigatórios!', 'warning')
            return redirect(url_for('auth.register'))
            
        # Verifica se o email já existe
        if User.query.filter_by(email=email).first():
            flash('Este email já está em uso.', 'warning')
            return redirect(url_for('auth.register'))
            
        # Cria o novo usuário
        new_user = User(nome=nome, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))

    # Se for GET, apenas mostra a página de registro
    return render_template('register.html')