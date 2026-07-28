from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
# quando precisar criar uma coluna e a db ja ta criada
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv
from .models import *
from .decorators import login_obrigatorio, admin_obrigatorio

setor_bp = Blueprint('setor', __name__)

@setor_bp.route('/setores', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def setores():
    lista_setores = Setor.query.all() #quando quiser passar valor pro html 
    if request.method == 'POST':
        setor = request.form['setor']
        nova_setor = Setor(setor=setor)
        db.session.add(nova_setor)
        db.session.commit()
        flash(f'Setor {setor} cadastrado com sucesso!')
        return redirect(url_for('setor.setores'))
    return render_template('dashboardsetores.html', setores=lista_setores)

@setor_bp.route('/setores/excluir/<int:id>', methods=['POST'])
@login_obrigatorio
@admin_obrigatorio
def excluir_setor(id):
    setor = Setor.query.get_or_404(id)
    if request.form.get('confirmacao') != 'sim':
        flash('Exclusão cancelada.')
        return redirect(url_for('setor.setores'))
    if setor.usuarios:
        flash('Não é possível excluir: essa setor ainda tem usuários vinculados.')
        return redirect(url_for('setor.setores'))
    db.session.delete(setor)
    db.session.commit()
    flash(f'Setor {setor.setor} excluída com sucesso!')
    return redirect(url_for('setor.setores'))

@setor_bp.route('/setores/confirmar-exclusao/<int:id>', methods=['GET'])
@login_obrigatorio
@admin_obrigatorio
def confirmar_exclusao_setor(id):
    setor = Setor.query.get_or_404(id)
    return render_template('excluirsetor.html', setor=setor)

@setor_bp.route('/setores/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def editarsetor(id):
    setor = db.session.query(Setor).filter_by(id=id).first()
    if request.method == 'POST':
        novo_nome = request.form['novonome']
        if novo_nome:
            setor.setor = novo_nome
        db.session.commit()
        return redirect(url_for('setor.setores'))
    return render_template('editarsetor.html', id=id, setor=setor)