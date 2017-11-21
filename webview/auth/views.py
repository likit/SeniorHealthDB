from flask_login import login_user, current_user, logout_user, login_required
from flask import request, render_template, redirect, url_for, session
from . import auth_blueprint as auth
from server import db, UserQuery
from models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

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
        return redirect(url_for('form.main'))


@auth.route('/logout')
@login_required
def logout():
    if 'form_data' in session:
        del session['form_data']
    logout_user()
    return redirect('/')

