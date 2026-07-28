from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .models import *
from .decorators import login_obrigatorio, admin_obrigatorio
from datetime import datetime

main_bp = Blueprint('main', __name__)

'''@main_bp.route('/')
@login_obrigatorio
def home():
    usuario = Usuario.query.get(session['usuario_id']) #get pega o id direto
    return render_template('home.html', usuario=usuario)'''

@main_bp.route('/')
@login_obrigatorio
def home():
    usuario = Usuario.query.get(session['usuario_id'])
    meus_chamados = Chamado.query.filter_by(usuario_id=usuario.id)
    abertos = meus_chamados.filter(Chamado.status != 'Concluído').count()
    em_andamento = meus_chamados.filter_by(status='Em andamento').count()
    concluidos = meus_chamados.filter_by(status='Concluído').count()
    return render_template('home.html', usuario=usuario, abertos=abertos, em_andamento=em_andamento, concluidos=concluidos)


@main_bp.route('/paineladmin')
@login_obrigatorio
@admin_obrigatorio
def paineladmin():
    hoje = datetime.utcnow()

    total_chamados = Chamado.query.count()
    abertos = Chamado.query.filter(Chamado.status != 'Concluído').count()
    em_andamento = Chamado.query.filter_by(status='Em andamento').count()
    concluidos = Chamado.query.filter_by(status='Concluído').count()
    urgentes = Chamado.query.filter_by(prioridade='Urgente').filter(Chamado.status != 'Concluído').count()
    chamados_no_mes = Chamado.query.filter(Chamado.data >= datetime(hoje.year, hoje.month, 1)).count()
    total_usuarios = Usuario.query.filter_by(role='cliente').count()
    total_setores = Setor.query.count()
    recentes = Chamado.query.order_by(Chamado.data.desc()).limit(5).all()
    return render_template('homeadmin.html',abertos=abertos, em_andamento=em_andamento, concluidos=concluidos, urgentes=urgentes, chamados_no_mes=chamados_no_mes, total_usuarios=total_usuarios, total_setores=total_setores, total_chamados=total_chamados, recentes=recentes)

'''@main_bp.route('/paineladmin')
@login_obrigatorio
@admin_obrigatorio
def paineladmin():
    return render_template('homeadmin.html')'''


@main_bp.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    lista_setor = Setor.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        setor = request.form['setor']
        senha = request.form['senha']
        
        novo_usuario = Usuario(nome=nome, email=email, setor_id=int(setor))
        novo_usuario.senha = generate_password_hash(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash(f'Usuário {novo_usuario.nome} cadastrado com sucesso!')
        return redirect(url_for('main.login'))
    
    return render_template('cadastro.html', setores=lista_setor)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.senha and check_password_hash(usuario.senha, senha):
            flash('Login realizado com sucesso!')
            session['usuario_id'] = usuario.id
            if usuario.role == 'admin':
                return redirect(url_for('main.paineladmin'))
            return redirect(url_for('main.home'))
        else:
            flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@main_bp.route('/logout')
@login_obrigatorio
def logout():
    session.pop('usuario_id', None)
    flash('Você saiu da sua conta.')
    return redirect(url_for('main.login'))