from flask import Flask
from flask import url_for
from flask import redirect
from flask import render_template

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('home.html')

@app.get('/signup')
def signup():
    return render_template('signup.html')

@app.post('/signup')
def signup_form():
    # validar y guardar el registro aqui
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

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)