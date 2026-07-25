from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="cliente")
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)

    pedidos = db.relationship("Pedido", backref="usuario", lazy=True)

    # usuario = Usuario.query.get(1)
    # usuario.pedidos  # lista de todos os Pedido onde pedido.usuario_id == 1

class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(100), nullable=False)

    usuarios = db.relationship("Usuario", backref="empresa", lazy=True)

    # pedido = Pedido.query.get(1)
    # pedido.usuario  # o objeto Usuario dono desse pedido (não uma lista, é um objeto só)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text(100), nullable=False)
    status = db.Column(db.String(20), default="Pendente")
    data = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
