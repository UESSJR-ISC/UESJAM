from flask import Flask
from flask import flash
from flask import session
from flask import request
from flask import url_for
from flask import redirect
from flask import render_template
from flask_session import Session

from database import Database
from database import engine
from database import get_db_session

from sqlalchemy import or_

import models

app = Flask(__name__)
app.config["SECRET_KEY"] = 'dmo5S4DxuD^9IWK1k33o7Xg88J&D8fq!'

Database.metadata.create_all(engine)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.get('/')
def home():
    user = session.get('user', None)
    
    db_session = get_db_session()

    user = db_session.query(models.Usuarios).filter(models.Usuarios.id==user.id).first()
    jams = db_session.query(models.Jams).all()

    return render_template('home.html', user=user, jams=jams, latest_jam=jams[0])

@app.get('/jams')
def jams():
    user = session.get('user', None)

    db_session = get_db_session()

    user = db_session.query(models.Usuarios).filter(models.Usuarios.id==user.id).first()
    jams = db_session.query(models.Jams).all()

    return render_template('jams.html', user=user, jams=jams, latest_jam=jams[0])

@app.get('/signup')
def signup():
    return render_template('signup.html')

@app.post('/signup')
def signup_form():
    admin = 0
    descripcion = ''
    picture = 'default.png'
    ues_id = request.form['ues-id']
    correo = request.form['user-email']
    password = request.form['user-password']
    usuario_nombre = request.form['user-name']
    confirmar_password = request.form['user-password-confirm']

    # ToDo: validar formulario
   
    nuevo_usuario = models.Usuarios(nombre=usuario_nombre, correo=correo, password=password, ues_id=ues_id, descripcion=descripcion, picture=picture, admin=admin)
    
    db_session = get_db_session()
    db_session.add(nuevo_usuario)
    db_session.commit()
    db_session.refresh(nuevo_usuario)
    
    flash('Ahora puedes iniciar sesion.')

    return redirect(url_for('login'))

@app.get('/logout')
def logout():
    session['user'] = None

    return redirect(url_for('login'))

@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def login_form():
    user_name = request.form['user-name']
    user_password = request.form['user-password']

    db_session = get_db_session()
    user = db_session.query(models.Usuarios).filter(
            or_(models.Usuarios.nombre==user_name, models.Usuarios.correo==user_name), 
            models.Usuarios.password==user_password).first()
    
    if user == None:
        flash('¡Usuario y/o contraseña incorrectos!')
        return redirect(url_for('login'))

    session['user'] = user

    return redirect(url_for('home'))

@app.get('/profile')
def profile():
    user = session.get('user', None)

    if user == None:
        flash('Inicia sesion para continuar.')
        return redirect(url_for('login'))
    
    db_session = get_db_session()

    user = db_session.query(models.Usuarios).filter(models.Usuarios.id==user.id).first()
    jams = db_session.query(models.Jams).all()

    return render_template('profile.html', user=user, jams=jams, latest_jam=jams[0])

@app.get('/admin')
def admin():
    user = session.get('user', None)

    if user == None:
        flash('Inicia sesion para continuar.')
        return redirect(url_for('login'))
    
    db_session = get_db_session()

    user = db_session.query(models.Usuarios).filter(models.Usuarios.id==user.id).first()

    if user.admin != 1:
        return redirect(url_for('home'))
    
    jams = db_session.query(models.Jams).all()
    
    return render_template('admin.html', user=user, jams=jams)

@app.post('/admin/newjam')
def admin_new_jam():
    # ToDo: validar session de admin
    cover = 'default.gif'
    titulo = request.form['jam-title']
    descripcion = request.form['jam-description']
   
    nuevo_jam = models.Jams(titulo=titulo, descripcion=descripcion, cover=cover)
    
    db_session = get_db_session()
    db_session.add(nuevo_jam)
    db_session.commit()
    db_session.refresh(nuevo_jam)
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)