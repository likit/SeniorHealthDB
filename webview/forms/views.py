from . import form_blueprint as form
from flask_login import login_required
from flask import render_template


@login_required
@form.route('/')
def main():
    return render_template('forms/main.html')


@login_required
@form.route('/diabetes', methods=["GET", "POST"])
def diabetes():
    return render_template('forms/form0.html')