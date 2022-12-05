import os

from PIL import Image
from io import BytesIO

from werkzeug.utils import secure_filename

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
from sqlalchemy import func
from sqlalchemy import desc

from datetime import datetime

import uuid

import models

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
JAM_COVERS_FOLDER = 'static/img/jam_covers/'
PROFILE_PICTURES_FOLDER = 'static/img/profile/'
GAMES_FILES_PATH = 'game/'
SECRET_KEY = 'dmo5S4DxuD^9IWK1k33o7Xg88J&D8fq!'
ALLOWED_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
ALLOWED_FILE_TYPES = ['zip', 'rar', 'exe']

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

    file_name = "%s.png" % str(uuid.uuid4())
    file_path = JAM_COVERS_FOLDER + file_name

    image.save(file_path, format="png")

    return file_name

def make_game_path():
    game_path = GAMES_FILES_PATH + str(uuid.uuid4()) + "/"

    os.mkdir('static/' + game_path)

    return game_path
    

def save_game_file(file, game_path, game_title):
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    file_name = "%s.%s" % (secure_filename(game_title), file_ext)
    file_path = game_path + file_name

    file.save('static/' + file_path)

    return file_name

def save_game_image(file, game_path):
    image_data = file.read()
    image = Image.open(BytesIO(image_data))

    file_name = "%s.png" % str(uuid.uuid4())
    file_path = game_path + file_name

    image.save('static/' + file_path, format="png")

    return file_name

@app.teardown_request
def remove_session(ex=None):
    db_session = get_db_session()
    db_session.remove()

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

    if jams == None:
        return redirect(url_for('home'))

    user = get_user_from_session()

    return render_template('jams.html', user=user, jams=jams, latest_jam=latest_jam)

@app.get('/jam/<id>')
def jam(id):
    user = get_user_from_session()
    
    db_session = get_db_session()

    jam = db_session.query(models.Jams)\
        .filter(models.Jams.id==id)\
        .first()
    
    if user != None:
        own_game = db_session.query(models.Juegos)\
            .filter(models.Juegos.usuario_id==user.id, models.Juegos.jam_id==id)\
            .first()
    else:
        own_game = None

    return render_template('jam.html', user=user, jam=jam, own_game=own_game)

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
        print("error 1")
        flash('No image cover was sent')
        return redirect(url_for('admin'))

    image_cover_file = request.files['jam-cover-image']

    if not validate_file_type(image_cover_file.filename, ALLOWED_IMAGE_TYPES):
        print("error 2")
        flash('Invalida file type for image cover')
        return redirect(url_for('admin'))

    opened = 0
    visible = 1
    cover = save_jam_cover(image_cover_file)
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

@app.get('/jam/<id>/toggle-open')
def jam_toggle_open(id):
    user = get_user_from_session()

    if not user or user.admin != 1:
        return redirect(url_for('home'))
    
    db_session = get_db_session()
    jam = db_session.query(models.Jams).filter(models.Jams.id==id).first()

    jam.opened = 0 if jam.opened == 1 else 1

    db_session.add(jam)
    db_session.commit()

    return redirect(url_for('jam', id=jam.id))

@app.get('/jam/<id>/toggle-visibility')
def jam_toggle_visibility(id):
    user = get_user_from_session()

    if not user or user.admin != 1:
        return redirect(url_for('home'))
    
    db_session = get_db_session()
    jam = db_session.query(models.Jams).filter(models.Jams.id==id).first()

    jam.visible = 0 if jam.visible == 1 else 1

    db_session.add(jam)
    db_session.commit()

    return redirect(url_for('admin'))

@app.post('/game')
def game_post():
    user = get_user_from_session()

    jam_id = request.form['game-jam-id']

    db_session = get_db_session()
    game = db_session.query(models.Juegos)\
        .filter(models.Juegos.usuario_id==user.id, models.Juegos.jam_id==jam_id)\
        .first()

    if game != None:
        flash('Ya has publicado un juego para esta Jam')
        return redirect(url_for('jam', id=jam_id))

    if not user:
        flash('Inicia sesion para continuar.')
        return redirect(url_for('login'))
    
    if 'game-cover' not in request.files:
        print("error 1")
        flash('No image cover was sent')
        return redirect(url_for('jam', id=jam_id))

    image_cover_file = request.files['game-cover']

    if not validate_file_type(image_cover_file.filename, ALLOWED_IMAGE_TYPES):
        print("error 2")
        flash('Invalid file type for image cover')
        return redirect(url_for('jam', id=jam_id))
    
    if 'game-files' not in request.files:
        print("error 1")
        flash('No game files was sent')
        return redirect(url_for('jam', id=jam_id))

    game_files = request.files['game-files']

    if not validate_file_type(game_files.filename, ALLOWED_FILE_TYPES):
        print("error 2")
        flash('Invalid file type for game files')
        return redirect(url_for('jam', id=jam_id))
    
    game_title = request.form['game-title']
    short_description = request.form['game-short-description']
    large_description = request.form['game-large-description']
    path = make_game_path()
    cover = save_game_image(image_cover_file, path)
    files = save_game_file(game_files, path, game_title)
    usuario_id = user.id

    game = models.Juegos(
        nombre=game_title,
        descripcion_corta=short_description,
        descripcion_larga=large_description,
        cover=cover,
        files=files,
        path=path,
        jam_id=jam_id,
        usuario_id=usuario_id
    )

    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)

    return redirect(url_for('jam', id=jam_id))

@app.get('/vote/<jam_id>/<game_id>')
def vote(jam_id, game_id):
    user = get_user_from_session()

    if not user:
        flash('Inicia sesion para continuar.')
        return redirect(url_for('login'))
    
    db_session = get_db_session()
    vote = db_session.query(models.Votos).filter(models.Votos.usuario_id==user.id, models.Votos.jam_id==jam_id).first()

    if vote != None:
        flash('Ya has votado para esta Jam')
        return redirect(url_for('jam', id=jam_id))
    
    new_vote = models.Votos(usuario_id=user.id, juego_id=game_id, jam_id=jam_id)

    db_session.add(new_vote)
    db_session.commit()
    db_session.refresh(new_vote)

    return redirect(url_for('jam', id=jam_id))

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)