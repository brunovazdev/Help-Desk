from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class Setor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setor = db.Column(db.String(100), nullable=False)

    usuarios = db.relationship("Usuario", backref="setor", lazy=True)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="cliente")
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)

    chamados = db.relationship("Chamado", backref="usuario", lazy=True)

    # usuario = Usuario.query.get(1)
    # usuario.pedidos  # lista de todos os Pedido onde pedido.usuario_id == 1

class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text(100), nullable=False)
    status = db.Column(db.String(20), default="Pendente")
    categoria = db.Column(db.String(30), nullable=False, default="Outros")
    prioridade = db.Column(db.String(10), nullable=False, default="Indefinida")
    data = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False) 
    # chamado = Chamado.query.get(1)
    # chamado.usuario  # o objeto Usuario dono desse chamado (não uma lista, é um objeto só)

class Comentario(db.Model): #um para muitos
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    chamado_id = db.Column(db.Integer, db.ForeignKey('chamado.id'), nullable=False) #chave estrangeira pega o id do chamado
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False) #chave estrangeira pega o id do usuario

    chamado = db.relationship("Chamado", backref="comentarios", lazy=True)
    autor = db.relationship("Usuario", backref="comentarios", lazy=True)