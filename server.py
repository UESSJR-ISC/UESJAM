from flask import Flask
from flask import request
from flask import url_for
from flask import redirect
from flask import render_template

from database import Database
from database import engine
from database import get_session

import models

app = Flask(__name__)
app.config["SECRET_KEY"] = 'dmo5S4DxuD^9IWK1k33o7Xg88J&D8fq!'

Database.metadata.create_all(engine)

@app.get('/')
def home():
    return render_template('home.html')

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
   
    
    nuevo_usuario = models.Usuarios(nombre=usuario_nombre, correo=correo, password=password, ues_id=ues_id, descripcion=descripcion, picture=picture, admin=admin)
    
    session = get_session()
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    
    return redirect(url_for('profile'))

@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def login_form():
    #validar sesion aqui
    return redirect(url_for('profile'))

@app.get('/profile')
def profile():
    return render_template('profile.html')

@app.get('/admin')
def admin():
    return render_template('admin.html')

@app.post('/admin/newjam')
def admin_new_jam():
    cover = 'default.png'
    titulo = request.form['jam-title']
    descripcion = request.form['jam-description']
   
    
    nuevo_jam = models.Jams(titulo=titulo, descripcion=descripcion, cover=cover)
    
    session = get_session()
    session.add(nuevo_jam)
    session.commit()
    session.refresh(nuevo_jam)
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)