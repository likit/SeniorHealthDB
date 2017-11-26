# -*- coding: utf-8 -*-
from flask_login import login_user, current_user, logout_user, login_required
from flask import (request, render_template,
                    redirect, url_for, session, flash)
from . import auth_blueprint as auth
from server import db, UserQuery
from models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user_id = request.args.get('user_id', None)
        account = db.search(UserQuery.id==user_id)[0]
        return render_template('auth/login.html', account=account)

    if request.method == 'POST':
        user_id = request.form.get('user_id', None)
        passcode = request.form.get('passcode', None)
        if not user_id or not passcode:
            return render_template('auth/loginerror.html')
        try:
            u = db.search(UserQuery.id == user_id)[0]
            if u['passcode'] == passcode:
                u = User(u['id'], u['firstname'] + ' ' + u['lastname'])
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


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname', None)
        lastname = request.form.get('lastname', None)
        user_id = request.form.get('user_id', None)
        password1 = request.form.get('passcode1', None)
        password2 = request.form.get('passcode2', None)
        print(firstname, lastname, user_id, password1, password2)
        if firstname and lastname and password1 and password2 and user_id:
            if password1 == password2 and password1.isdigit() and len(password1) == 6:
                db.insert({
                    'id': user_id,
                    'firstname': firstname,
                    'lastname': lastname,
                    'passcode': password1
                })
                return redirect(url_for('auth.login', user_id=user_id))
        else:
            flash('กรุณาตรวจสอบข้อมูลให้ถูกต้องอีกครั้ง')
    return render_template('auth/register.html')