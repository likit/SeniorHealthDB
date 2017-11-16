from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/login')
def login():
    return "<h1>Login Page</h1>"


def run_server():
    app.run(host='127.0.0.1', port=5757)


if __name__ == '__main__':
    run_server()