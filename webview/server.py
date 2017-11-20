# -*- coding: utf8 -*-
from flask import Flask, render_template, url_for, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
from tinydb import TinyDB, Query
import webview
from models import User

app = Flask(__name__)
app.secret_key = 'agingthai'

db = TinyDB('data/users.json')
UserQuery = Query()

from auth.views import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    try:
        user = db.search(UserQuery.id == user_id)[0]
    except IndexError:
        return None
    else:
        u = User(user['id'], user['name'])
        return u


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/register')
def register():
    db.insert({'id': '1', 'name': 'tester', 'passcode': '333444'})
    return jsonify(db.all())


@login_required
@app.route('/form/<int:form_id>')
def form(form_id):
    form = 'form%d.html' % form_id
    return render_template(form)


@app.route('/about')
def about():
    return render_template('about.html')


def run_server():
    app.run(host='127.0.0.1', port=5757)


if __name__ == '__main__':
    run_server()