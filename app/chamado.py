from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from sqlalchemy import or_ #para fazer busca em varias colunas
import os
from .models import *
from .decorators import login_obrigatorio, admin_obrigatorio

chamado_bp = Blueprint('chamado', __name__)

@chamado_bp.route('/chamado/criar', methods=['GET', 'POST'])
@login_obrigatorio
def criarchamado():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        novo_chamado = Chamado(titulo=titulo, descricao=descricao, categoria=categoria, usuario_id=session['usuario_id'])
        db.session.add(novo_chamado)
        db.session.commit()
        flash(f'Chamado {novo_chamado.id} criado com sucesso!')
        return redirect(url_for('chamado.verchamados'))
    usuario = Usuario.query.get['usuario_id']
    return render_template('criarchamado.html', usuario=usuario)

@chamado_bp.route('/chamado/visualizar')
@login_obrigatorio
def verchamados():
    pagina = request.args.get('pagina', 1, type=int) #1 é o default
    chamadospag = Chamado.query.filter_by(usuario_id=session['usuario_id']).paginate(page=pagina, per_page=5)
    return render_template('verchamados.html', chamados=chamadospag)

@chamado_bp.route('/chamados', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def chamados():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        novo_chamado = Chamado(titulo=titulo, descricao=descricao, usuario_id=session['usuario_id'])
        db.session.add(novo_chamado)
        db.session.commit()
        flash(f'O chamado {novo_chamado.titulo} foi cadastrado com sucesso')
        return redirect(url_for('chamado.chamados'))

    buscar = request.args.get('req', '')# quando o metodo for GET do form usamos isso
    if buscar:
        resultado = Chamado.query.filter(or_(Chamado.titulo.ilike(f'%{buscar}%'), 
        Chamado.descricao.ilike(f'%{buscar}%'), 
        Chamado.categoria.ilike(f'%{buscar}%'), 
        Chamado.prioridade.ilike(f'%{buscar}%'), 
        Chamado.status.ilike(f'%{buscar}%')
        )
    ).all() #identar assim e mil vzs melhor e so peguei agr...
        return render_template('buscachamado.html', buscar=buscar, resultado=resultado)

    pagina = request.args.get('pagina', 1, type=int)
    chamadospag = Chamado.query.paginate(page=pagina, per_page=5)
    return render_template('dashboardchamado.html', chamados=chamadospag)

@chamado_bp.route('/chamados/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def editarchamado(id):
    chamado = db.session.query(Chamado).filter_by(id=id).first()
    if request.method == 'POST':
        novo_titulo = request.form['novotitulo']
        nova_descricao = request.form['novadescricao']
        novo_status = request.form['novostatus']
        nova_categoria = request.form['novacategoria']
        nova_prioridade = request.form['novaprioridade']
        if novo_titulo:
            chamado.titulo = novo_titulo
        if nova_descricao:
            chamado.descricao = nova_descricao
        if novo_status:
            chamado.status = novo_status
        if nova_categoria:
            chamado.categoria = nova_categoria
        if nova_prioridade:
            chamado.prioridade = nova_prioridade
        db.session.commit()
        return redirect(url_for('chamado.chamados'))
    return render_template('editarchamado.html', id=id, chamado=chamado)

@chamado_bp.route('/chamados/excluir/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def excluirchamado(id):
    chamado = db.session.query(Chamado).filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['confirmacao'] == 'sim':
            db.session.delete(chamado)
            db.session.commit()
            return redirect(url_for('chamado.chamados'))
        else:
            return redirect(url_for('chamado.chamados'))
    return render_template('excluirchamado.html', id=id, chamado=chamado)

@chamado_bp.route('/chamados/<int:id>/detalhes', methods=['GET', 'POST'])
@login_obrigatorio
def detalhes(id):
    chamado = Chamado.query.get_or_404(id)
    acesso = Usuario.query.get(session['usuario_id'])
    if session['usuario_id'] == chamado.usuario_id or acesso.role == 'admin':
        if request.method == 'POST':
            comentario = request.form['comentario']
            novo_comentario = Comentario(texto=comentario, chamado_id=chamado.id, usuario_id=acesso.id)
            db.session.add(novo_comentario)
            db.session.commit()
            return redirect(url_for('chamado.detalhes', id=id))
        return render_template('detalheschamado.html', id=id, chamado=chamado, acesso=acesso)
    else:
        flash('Você não tem permissão para ver esse chamado.')
        return redirect(url_for('chamado.verchamados'))