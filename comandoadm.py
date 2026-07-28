from app import create_app
from app.models import db, Setor, Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    setor = Setor(setor="TI")
    db.session.add(setor)
    db.session.commit()

    admin = Usuario(
        nome="admin",
        email="admin@teste.com",
        senha=generate_password_hash("123456"),
        role="admin",
        setor_id=setor.id
    )
    db.session.add(admin)
    db.session.commit()

    print("Setor e admin criados com sucesso!")