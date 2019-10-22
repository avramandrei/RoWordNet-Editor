from flask_login import LoginManager
from app import app
from app.services.model import users
from flask import flash, redirect, url_for


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.session_protection = 'strong'
login_manager.login_view = 'login'


@login_manager.user_loader
def user_loader(user_id):
    for user in users:
        if user.id == user_id:
            return user


@login_manager.request_loader
def request_loader(request):
    user_id = request.form.get('id')
    password = request.form.get('password')

    user = None

    for user_it in users:
        if user_it.id == user_id:
            user = user_it

    if user is None:
        return

    user.is_authenticated = user.verify_password(password)

    return user


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('login'))

