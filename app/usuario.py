from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
# quando precisar criar uma coluna e a db ja ta criada
from sqlalchemy import or_ #para fazer busca em varias colunas
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .models import *
from .decorators import login_obrigatorio, admin_obrigatorio

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/usuarios', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def usuarios():
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
        return redirect(url_for('usuario.usuarios'))

    usuario = Usuario.query.get(session['usuario_id'])
    buscar = request.args.get('req', '')
    if buscar:
        resultado = Usuario.query.filter(or_(Usuario.nome.ilike(f'%{buscar}%'),
            Usuario.role.ilike(f'%{buscar}%'),
            Usuario.id.ilike(f'%{buscar}%')
            )
        ).all()
        return render_template('buscausuario.html', buscar=buscar, resultado = resultado, usuario=usuario)
    lista_setor = Setor.query.all()

    pagina = request.args.get('pagina', 1, type=int)
    usuariospag = Usuario.query.paginate(page=pagina, per_page=5)
    return render_template('dashboardusuarios.html', setores=lista_setor, usuarios=usuariospag)

@usuario_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def editarusuario(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    if request.method == 'POST':
        novo_nome = request.form['novonome']
        novo_email = request.form['novoemail']
        if novo_nome:
            usuario.nome = novo_nome
        if novo_email:
            usuario.email = novo_email
        db.session.commit()
        return redirect(url_for('usuario.usuarios'))
    return render_template('editarusuario.html', id=id, usuario=usuario)

@usuario_bp.route('/usuarios/excluir/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def excluirusuario(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['confirmacao'] == 'sim':
            db.session.delete(usuario)
            db.session.commit()
            return redirect(url_for('usuario.usuarios'))
        else:
            return redirect(url_for('usuario.usuarios'))
    return render_template('excluirusuario.html', id=id, usuario=usuario)