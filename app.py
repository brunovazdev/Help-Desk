from flask import Flask, render_template, request, redirect, url_for, flash, session
# quando precisar criar uma coluna e a db ja ta criada
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv
from models import *

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)

def admin_obrigatorio(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa fazer login para acessar essa página.')
            return redirect(url_for('login'))
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario.role != 'admin':
            flash('Você não tem permissão para acessar essa página.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorada

def login_obrigatorio(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa fazer login para acessar essa página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada


@app.route('/')
@login_obrigatorio
def home():
    return render_template('home.html')

@app.route('/paineladmin')
@login_obrigatorio
@admin_obrigatorio
def paineladmin():
    return render_template('homeadmin.html')


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    lista_empresa = Empresa.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        empresa = request.form['empresa']
        senha = request.form['senha']
        
        novo_usuario = Usuario(nome=nome, email=email, empresa_id=int(empresa))
        novo_usuario.senha = generate_password_hash(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash(f'Usuário {novo_usuario.nome} cadastrado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html', empresas=lista_empresa)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.senha and check_password_hash(usuario.senha, senha):
            flash('Login realizado com sucesso!')
            session['usuario_id'] = usuario.id
            if usuario.role == 'admin':
                return redirect(url_for('paineladmin'))
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos.')
        if usuario.role == 'cliente':
            return redirect(url_for('home'))
        if usuario.role == 'admin':
            return redirect(url_for('paineladmin'))
    return render_template('login.html')


@app.route('/usuarios', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def usuarios():
    usuarios = Usuario.query.all() #mostra todos os usuarios
    lista_empresa = Empresa.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        empresa = request.form['empresa']
        senha = request.form['senha']
        
        novo_usuario = Usuario(nome=nome, email=email, empresa_id=int(empresa))
        novo_usuario.senha = generate_password_hash(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash(f'Usuário {novo_usuario.nome} cadastrado com sucesso!')
        return redirect(url_for('login'))
    return render_template('dashboardusuarios.html', usuarios=usuarios, empresas=lista_empresa)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('usuarios'))
    return render_template('editarusuario.html', id=id, usuario=usuario)

@app.route('/usuarios/excluir/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def excluirusuario(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['confirmacao'] == 'sim':
            db.session.delete(usuario)
            db.session.commit()
            return redirect(url_for('usuarios'))
        else:
            return redirect(url_for('usuarios'))
    return render_template('excluirusuario.html', id=id, usuario=usuario)

@app.route('/empresas', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def empresas():
    lista_empresas = Empresa.query.all() #quando quiser passar valor pro html 
    if request.method == 'POST':
        empresa = request.form['empresa']
        cnpj = request.form['cnpj']
        nova_empresa = Empresa(empresa=empresa, cnpj=cnpj)
        db.session.add(nova_empresa)
        db.session.commit()
        flash(f'Empresa {empresa} com cnpj {cnpj} cadastrada com sucesso!')
        return redirect(url_for('empresas'))
    return render_template('dashboardempresas.html', empresas=lista_empresas)

@app.route('/empresas/excluir/<int:id>', methods=['POST'])
@login_obrigatorio
@admin_obrigatorio
def excluir_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    if request.form.get('confirmacao') != 'sim':
        flash('Exclusão cancelada.')
        return redirect(url_for('empresas'))
    if empresa.usuarios:
        flash('Não é possível excluir: essa empresa ainda tem usuários vinculados.')
        return redirect(url_for('empresas'))
    db.session.delete(empresa)
    db.session.commit()
    flash(f'Empresa {empresa.empresa} excluída com sucesso!')
    return redirect(url_for('empresas'))

@app.route('/empresas/confirmar-exclusao/<int:id>', methods=['GET'])
@login_obrigatorio
@admin_obrigatorio
def confirmar_exclusao_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    return render_template('excluirempresa.html', empresa=empresa)

@app.route('/empresas/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def editarempresa(id):
    empresa = db.session.query(Empresa).filter_by(id=id).first()
    if request.method == 'POST':
        novo_nome = request.form['novonome']
        novo_cnpj = request.form['novocnpj']
        if novo_nome:
            empresa.empresa = novo_nome
        if novo_cnpj:
            empresa.cnpj = novo_cnpj
        db.session.commit()
        return redirect(url_for('usuarios'))
    return render_template('editarempresa.html', id=id, empresa=empresa)

@app.route('/criarpedido', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def criarpedido():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        novo_pedido = Pedido(titulo=titulo, descricao=descricao, usuario_id=session['usuario_id'])
        db.session.add(novo_pedido)
        db.session.commit()
        flash(f'Pedido {novo_pedido.id} criado com sucesso!')
        return redirect(url_for('criarpedido'))
    return render_template('criarpedido.html')

@app.route('/verpedidos')
@login_obrigatorio
@admin_obrigatorio
def verpedidos():
    pedidos = Pedido.query.all()
    return render_template('verpedidos.html', pedidos=pedidos)

@app.route('/pedidos', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def pedidos():
    pedidos = Pedido.query.all()
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        novo_pedido = Pedido(titulo=titulo, descricao=descricao, usuario_id=session['usuario_id'])
        db.session.add(novo_pedido)
        db.session.commit()
        flash(f'O pedido {novo_pedido.titulo} foi cadastrado com sucesso')
        return redirect(url_for('pedidos'))
    return render_template('dashboardpedidos.html', pedidos=pedidos)

@app.route('/pedidos/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def editarpedido(id):
    pedido = db.session.query(Pedido).filter_by(id=id).first()
    if request.method == 'POST':
        novo_titulo = request.form['novotitulo']
        nova_descricao = request.form['novadescricao']
        novo_status = request.form['novostatus']
        if novo_titulo:
            pedido.titulo = novo_titulo
        if nova_descricao:
            pedido.descricao = nova_descricao
        if novo_status:
            pedido.status = novo_status
        db.session.commit()
        return redirect(url_for('verpedidos'))
    return render_template('editarpedido.html', id=id, pedido=pedido)

@app.route('/pedidos/excluir/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@admin_obrigatorio
def excluirpedido(id):
    pedido = db.session.query(Pedido).filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['confirmacao'] == 'sim':
            db.session.delete(pedido)
            db.session.commit()
            return redirect(url_for('verpedidos'))
        else:
            return redirect(url_for('verpedidos'))
    return render_template('excluirpedido.html', id=id, pedido=pedido)

@app.route('/logout')
@login_obrigatorio
def logout():
    session.pop('usuario_id', None)
    flash('Você saiu da sua conta.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
