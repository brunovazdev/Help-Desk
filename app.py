from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
# quando precisar criar uma coluna e a db ja ta criada
from flask_migrate import Migrate
import requests
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados.db'
app.config['SECRET_KEY'] = 'flashmessage'
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = request.form['idade']
        novo_usuario = Usuario(nome=nome, idade=idade)
        db.session.add(novo_usuario)
        db.session.commit()
        flash(f'Usuário {novo_usuario.nome} cadastrado com sucesso!')
        return redirect(url_for('cadastro'))
    
    return render_template('cadastro.html')


@app.route('/deletar', methods=['GET', 'POST'])
def deletar():
    if request.method == 'POST':
        id = request.form['id']
        usuario = Usuario.query.get(id)
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuário ID: {usuario.id} - Nome: "{usuario.nome}", deletado com sucesso')
        return redirect(url_for('deletar'))
    return render_template('deletar.html')

@app.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.all() #mostra todos os usuarios
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    if request.method == 'POST':
        id = request.form['id']
        nome_novo = request.form['nome']
        idade_nova = request.form['idade']
        usuario = db.session.query(Usuario).filter_by(id=id).first()
        if nome_novo:
            usuario.nome = nome_novo
        if idade_nova:
            usuario.idade = idade_nova
        db.session.commit()
        flash('Usuário editado!')
        return redirect(url_for('editar'))
    return render_template('editar.html')

if __name__ == '__main__':
    app.run()
