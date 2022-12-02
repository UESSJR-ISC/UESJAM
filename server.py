from PIL import Image
from io import BytesIO

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

from datetime import datetime

import models

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
JAM_COVERS_FOLDER = 'static/img/jam_covers/'
PROFILE_PICTURES_FOLDER = 'static/img/profile/'
SECRET_KEY = 'dmo5S4DxuD^9IWK1k33o7Xg88J&D8fq!'
ALLOWED_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
ALLOWED_FILE_TYPES = ['zip', 'rar']

app.config.from_object(__name__)

Database.metadata.create_all(engine)
Session(app)

def get_user_from_session():
    user = session.get('user', None)

    if user != None:
        db_session = get_db_session()
        user = db_session.query(models.Usuarios).filter(models.Usuarios.id==user.id).first()
    
    return user

def validate_file_type(filename: str, types):
    return filename != '' and \
        '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in types

def save_jam_cover(file):
    image_data = file.read()
    image = Image.open(BytesIO(image_data))

@app.get('/')
def home():
    db_session = get_db_session()
    jams = db_session.query(models.Jams).filter(models.Jams.visible==1).all()
    latest_jam = db_session.query(models.Jams).filter(models.Jams.visible==1).first()

    user = get_user_from_session()

    return render_template('home.html', user=user, jams=jams, latest_jam=latest_jam)

@app.get('/jams')
def jams():
    db_session = get_db_session()
    jams = db_session.query(models.Jams).filter(models.Jams.visible==1).all()
    latest_jam = db_session.query(models.Jams).filter(models.Jams.visible==1).first()

    user = get_user_from_session()

    return render_template('jams.html', user=user, jams=jams, latest_jam=latest_jam)

@app.get('/jam/<id>')
def jam(id):
    db_session = get_db_session()
    jam = db_session.query(models.Jams).filter(models.Jams.id==id).first()

    user = get_user_from_session()

    return render_template('jam.html', user=user, jam=jam)

@app.get('/signup')
def signup():
    user = get_user_from_session()

    if user != None:
        return redirect(url_for('home'))

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
   
    nuevo_usuario = models.Usuarios(
        nombre=usuario_nombre, 
        correo=correo, 
        password=password, 
        ues_id=ues_id, 
        descripcion=descripcion, 
        picture=picture, 
        admin=admin)
    
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
    user = get_user_from_session()

    if user == None:
        flash('Inicia sesion para continuar.')
        return redirect(url_for('login'))
    
    db_session = get_db_session()
    jams = db_session.query(models.Jams).all()
    latest_jam = db_session.query(models.Jams).first()

    return render_template('profile.html', user=user, jams=jams, latest_jam=latest_jam)

@app.get('/admin')
def admin():
    user = get_user_from_session()

    if user == None:
        flash('Inicia sesion para continuar.')
        return redirect(url_for('login'))

    elif user.admin != 1:
        return redirect(url_for('home'))
    
    db_session = get_db_session()
    jams = db_session.query(models.Jams).all()
    
    return render_template('admin.html', user=user, jams=jams)

@app.post('/admin/newjam')
def admin_new_jam():
    user = get_user_from_session()

    if not user or user.admin != 1:
        return redirect(url_for('home'))

    if 'jam-cover-image' not in request.files:
        flash('No image cover was sent')
        return redirect(url_for('admin')), 400

    image_cover_file = request.files['jam-cover-image']

    if not validate_file_type(image_cover_file.filename, ALLOWED_IMAGE_TYPES):
        flash('Invalida file type for image cover')
        return redirect(url_for('admin')), 400
    
    # ToDo guardar imagen

    opened = 0
    visible = 1
    cover = image_cover_file.filename
    titulo = request.form['jam-title']
    descripcion = request.form['jam-description']
    fecha_inicio = datetime.strptime(request.form['jam-start-date'], '%Y-%m-%d').date()
    fecha_final = datetime.strptime(request.form['jam-end-date'], '%Y-%m-%d').date()
    tags = request.form['jam-tags']
   
    nuevo_jam = models.Jams(
        titulo=titulo, 
        descripcion=descripcion, 
        cover=cover,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final,
        tags=tags,
        opened=opened,
        visible=visible)
    
    db_session = get_db_session()
    db_session.add(nuevo_jam)
    db_session.commit()
    db_session.refresh(nuevo_jam)
    
    return redirect(url_for('admin'))

@app.get('/jam/<id>/close')
def jam_close(id):
    user = get_user_from_session()

    if not user or user.admin != 1:
        return redirect(url_for('home'))
    
    db_session = get_db_session()
    jam = db_session.query(models.Jams).filter(models.Jams.id==id).first()

    jam.opened = 0

    db_session.add(jam)
    db_session.commit()

    return redirect(url_for('jam', id=jam.id))

@app.get('/jam/<id>/open')
def jam_open(id):
    user = get_user_from_session()

    if not user or user.admin != 1:
        return redirect(url_for('home'))
    
    db_session = get_db_session()
    jam = db_session.query(models.Jams).filter(models.Jams.id==id).first()

    jam.opened = 1

    db_session.add(jam)
    db_session.commit()

    return redirect(url_for('jam', id=jam.id))

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)