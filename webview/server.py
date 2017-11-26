# -*- coding: utf8 -*-
from flask import Flask, render_template, url_for, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
from tinydb import TinyDB, Query
import webview
from models import User

app = Flask(__name__)
app.secret_key = 'agingthai'

db = TinyDB('data/users.json')
formdb = TinyDB('data/forms.json')
UserQuery = Query()

from auth import auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from forms import form_blueprint
app.register_blueprint(form_blueprint, url_prefix='/form')

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


@app.template_filter()
def toblank(value):
    if not value:
        return ''
    else:
        return value


@app.route('/')
def main():
    accounts = db.all()
    return render_template('index.html', accounts=accounts)


@app.route('/register')
def register():
    db.insert({'id': '1', 'name': 'tester', 'passcode': '333444'})
    return jsonify(db.all())


@app.route('/about')
def about():
    return render_template('about.html')


def run_server():
    app.run(host='127.0.0.1', port=5757)


if __name__ == '__main__':
    app.run(debug=True, port=5000)