# -*- coding: utf8 -*-
from flask import Flask, render_template, url_for, jsonify
from tinydb import TinyDB

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/login')
def login():
    return "<h1>Login Page</h1>"


@app.route('/register')
def register():
    db = TinyDB('data/users.json')
    db.insert({'name': 'สมใจหมาย'})
    return jsonify(db.all())



def run_server():
    app.run(host='127.0.0.1', port=5757)


if __name__ == '__main__':
    run_server()