# -*- coding: utf8 -*-
import hashlib
from datetime import datetime

from . import form_blueprint as form
from flask_login import login_required, current_user
from flask import render_template, session, request, redirect, url_for, flash
from tinydb import Query
from server import db, formdb


@form.route('/', methods=["GET"])
@login_required
def main():
    # clear existing form data if user starts over
    if request.args.get('startover', False) and 'form_data' in session:
        del session['form_data']

    if 'form_data' not in session:
        session['form_data'] = {'_id': None, 'data': {
            'bp': {},
            'cvd': {},
        }}

    form_data = session['form_data']
    if not form_data['_id']:
        survey_datetime = datetime.now()
        hashtext = current_user.name.encode('utf8') + str(survey_datetime)
        form_data['_id'] = hashlib.sha224(hashtext).hexdigest()
        form_data['data']['created_date'] = survey_datetime
        session['form_data'] = form_data  # update form data in session
        is_in_progress = False
    else:
        is_in_progress = True
    return render_template('forms/main.html',
            form_id=form_data['_id'],
            survey_datetime=form_data['data']['created_date'],
            is_in_progress=is_in_progress
        )


@form.route('/personalinfo', methods=["GET", "POST"])
@login_required
def personalinfo():
    if request.method == 'POST':
        return redirect(url_for('form.bloodpressure'))
    return render_template('forms/personal.html')


@form.route('/bloodpressure', methods=["GET", "POST"])
@login_required
def bloodpressure():
    form_data = session['form_data']
    bp = form_data['data']['bp']

    if request.method == 'POST':
        try:
            bp['systolic'] = int(request.form['sbp'])
        except ValueError:
            bp['systolic'] = None
        try:
            bp['diastolic'] = int(request.form['dbp'])
        except ValueError:
            bp['diastolic'] = None
        form_data['data']['bp'] = bp
        session['form_data'] = form_data
        if request.form['submit'] == 'next':
            return redirect(url_for('form.cvd'))
        if request.form['submit'] == 'save':
            flash('บันทึกลงหน่วยความจำชั่วคราวแล้ว')
            return redirect(url_for('form.bloodpressure'))

    bp_systolic = bp.get('systolic', None)
    bp_diastolic = bp.get('diastolic', None)

    return render_template('forms/bloodpressure.html',
                bp_systolic=bp_systolic, bp_diastolic=bp_diastolic)


@form.route('/cvd', methods=['GET', 'POST'])
@login_required
def cvd():
    form_data = session['form_data']
    cvd = form_data['data']['cvd']

    if request.method == 'POST':
        form_data['data']['cvd'] = request.form.getlist('cvd')
        session['form_data'] = form_data
        if request.form['submit'] == 'next':
            return redirect(url_for('form.end'))
        else:
            flash('บันทึกลงหน่วยความจำชั่วคราวแล้ว')
            return redirect(url_for('form.cvd'))

    return render_template('forms/cvd.html')


@form.route('/exit')
@login_required
def exit():
    if 'form_data' not in session:
        return redirect(url_for('form.main'))

    form_data = session['form_data']
    return render_template('forms/exit.html',
            form_id=form_data['_id'],
            survey_datetime=form_data['data']['created_date'])


@form.route('/save')
@login_required
def save():
    if 'form_data' not in session:
        return redirect(url_for('form.main'))
    else:
        form_data = session['form_data']
        try:
            updated_datetime = datetime.now()
            form_data['data']['updated_date'] = \
                updated_datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            form_data['data']['created_date'] = \
                form_data['data']['created_date'].strftime("%Y-%m-%d %H:%M:%S")
            formdb.insert(form_data)
        except:
            return render_template('forms/saved.html',
                success=False)
        return render_template('forms/saved.html',
                    success=True,
                    form_id=form_data['_id'],
                    updated_datetime=updated_datetime)


@form.route('/end', methods=["GET"])
@login_required
def end():
    return render_template('forms/end.html')