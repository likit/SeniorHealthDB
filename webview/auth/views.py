from flask_login import login_user, current_user, logout_user
from flask import request, render_template, redirect
from . import auth_blueprint as auth
from server import db, UserQuery
from models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    pid = request.form.get('pid', None)
    passcode = request.form.get('passcode', None)
    if not pid or not passcode:
        return render_template('auth/loginerror.html')
    try:
        u = db.search(UserQuery.id == pid)[0]
        if u['passcode'] == passcode:
            u = User(u['id'], u['name'])
        else:
            return render_template('auth/loginerror.html')
    except IndexError:
        return render_template('auth/loginerror.html')
    else:
        login_user(u)
        return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect('/')

