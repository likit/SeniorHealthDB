# -*- coding: utf8 -*-
import hashlib
from datetime import datetime

from . import form_blueprint as form
from flask_login import login_required, current_user
from flask import (render_template, session,
                    request, redirect, url_for, flash)
from tinydb import Query
from server import db, formdb

DATETIMEFORMAT = '%Y-%m-%d %H:%M:%S'
RecQ = Query()


@form.route('/', methods=["GET"])
@login_required
def main():
    # clear existing form data if user starts over
    if request.args.get('startover', False) and 'form_data' in session:
        del session['form_data']

    if 'form_data' not in session:
        session['form_data'] = {'_id': None,
                                    'created_by': current_user.id,
                                    'data': {
                                        'bp': {},
                                        'cvd': [],
                                        'dental': {},
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
            return redirect(url_for('form.dental'))
        else:
            flash('บันทึกลงหน่วยความจำชั่วคราวแล้ว')
            return redirect(url_for('form.cvd'))

    return render_template('forms/cvd.html')


@form.route('/dental', methods=['GET', 'POST'])
@login_required
def dental():
    form_data = session['form_data']
    dental = form_data['data']['dental']
    if request.method == 'POST':
        dental_p1_1_1 = request.form.get('p1.1.1', None)
        dental_p1_1_1_note = request.form.get('p1.1.1.note', None)
        dental_p1_1_2 = request.form.get('p1.1.2', None)
        dental_p1_1_3 = request.form.get('p1.1.3', None)
        dental_p1_1_3_note = request.form.get('p1.1.3.note', None)
        dental_p1_2 = request.form.getlist('p1.2')
        dental_p2_1 = request.form.get('p2.1', None)
        dental_p2_2 = request.form.get('p2.2', None)
        dental_p2_3 = request.form.get('p2.3', None)
        dental_p2_4 = request.form.get('p2.4', None)
        dental_p2_5 = request.form.get('p2.5', None)
        dental_p2_6 = request.form.get('p2.6', None)
        dental_p2_7 = request.form.get('p2.7', None)
        dental_p3 = request.form.getlist('p3')

        dental['p1.1.1'] = dental_p1_1_1
        dental['p1.1.1.note'] = dental_p1_1_1_note
        dental['p1.1.2'] = dental_p1_1_2
        dental['p1.1.3'] = dental_p1_1_3
        dental['p1.1.3.note'] = dental_p1_1_3_note
        dental['p1.2'] = dental_p1_2
        dental['p2.1'] = dental_p2_1
        dental['p2.2'] = dental_p2_2
        dental['p2.3'] = dental_p2_3
        dental['p2.4'] = dental_p2_4
        dental['p2.5'] = dental_p2_5
        dental['p2.6'] = dental_p2_6
        dental['p2.7'] = dental_p2_7
        dental['p3'] = dental_p3
        form_data['data']['dental'] = dental
        session['form_data'] = form_data
        if request.form['submit'] == 'save':
            flash('บันทึกลงหน่วยความจำชั่วคราวแล้ว')
            return redirect(url_for('form.dental'))
        if request.form['submit'] == 'next':
            return redirect(url_for('form.end'))
    return render_template('forms/dental.html')


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
                updated_datetime.now().strftime(DATETIMEFORMAT)
            form_data['data']['created_date'] = \
                form_data['data']['created_date'].strftime(DATETIMEFORMAT)
            try:
                record = formdb.search(RecQ._id==form_data['_id'])[0]
            except IndexError:  # if the record does not exist, insert new record
                formdb.insert(form_data)
            else:  # else update the record
                formdb.update({'data': form_data['data']}, RecQ._id==form_data['_id'])
        except:
            return render_template('forms/saved.html', success=False,
                    form_id=form_data['_id'],
                    updated_datetime=updated_datetime)
        del session['form_data']
        return render_template('forms/saved.html',
                    success=True,
                    form_id=form_data['_id'],
                    updated_datetime=updated_datetime)


@form.route('/end', methods=["GET"])
@login_required
def end():
    return render_template('forms/end.html')


@form.route('/list', methods=['GET'])
@login_required
def record_list():
    records = formdb.search(RecQ.created_by==current_user.id)
    return render_template('forms/list.html', records=records)


@form.route('/edit')
@login_required
def edit():
    recid = request.args.get('recid', None)
    if recid:
        record = formdb.search(RecQ._id==recid)[0]
        if record:
            if 'form_data' in session:
                form_data = session['form_data']
            form_data['_id'] = record['_id']
            record['data']['created_date'] = \
                    datetime.strptime(record['data']['created_date'],
                    DATETIMEFORMAT)
            record['data']['updated_date'] = \
                    datetime.strptime(record['data']['updated_date'],
                    DATETIMEFORMAT)
            form_data['data'] = record['data']
            session['form_data'] = form_data
            return redirect(url_for('form.main'))
    else:
        flash('ไม่พบรายการที่ท่านต้องการแก้ไข')
        return redirect(url_for('form.record_list'))


@form.route('/delete_record')
@login_required
def delete_record():
    recid = request.args.get('recid', None)
    confirmed = request.args.get('confirmed', None)
    if not confirmed and recid:
        return render_template('forms/delete_rec.html', recid=recid)
    if (confirmed == "true") and recid:
        print('confirmed is yes')
        try:
            formdb.remove(RecQ._id==recid)
        except:
            flash('ไม่สามารถลบรายการได้')
            return redirect(url_for('form.record_list'))
        else:
            return redirect(url_for('form.record_list'))
    else:
        return redirect(url_for('form.record_list'))