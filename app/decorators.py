from functools import wraps
from flask import session, flash, redirect, url_for
from .models import Usuario

def login_obrigatorio(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa fazer login para acessar essa página.')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorada

def admin_obrigatorio(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa fazer login para acessar essa página.')
            return redirect(url_for('main.login'))
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario.role != 'admin':
            flash('Você não tem permissão para acessar essa página.')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorada