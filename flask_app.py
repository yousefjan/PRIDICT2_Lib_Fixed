from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from flask_session import Session
from me_peg import dp, manual_dp
import json
import uuid
from os.path import exists
from os import remove

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pQbXfneo3JBxdh'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

PASSWORD = "ivakinez10572"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def submit():
    password = request.form.get('password')

    if password == PASSWORD:
        session['logged_in'] = True
        return redirect('/menu')
    else:
        return render_template('index.html')


@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect('/')

    return render_template('menu.html')


@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('home.html')


@app.route('/submit_form', methods=['POST'])
def submit_form():
    if not session.get('logged_in'):
        return redirect('/')

    wts = request.form.get('wts')
    link = request.form.get('link')
    block = request.form.get('block')

    link = bool(link)
    block = block == "eblock"

    epeg = dp(wts, link, block)

    return render_template('result.html', epeg=epeg)


@app.route('/manual_pred')
def manual():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('manual.html')


@app.route('/manual_pred_post', methods=['POST'])
def submit_data():
    rtt = request.form['rtt']
    wts = request.form['wts']
    pbs = request.form['pbs']

    efficiency = manual_dp(wts, rtt, pbs)

    return render_template('manual_result.html', efficiency=efficiency)


@app.route('/button1')
def button1():
    if not session.get('logged_in'):
        return redirect('/')

    return redirect('/home')


# @app.route('/library')
# def library():
#     if not session.get('logged_in'):
#         return redirect('/')

#     return render_template('library.html')


# #LIBRARY W/ SCAFFOLD
# @app.route('/process_sequence', methods=['POST'])
# def process_sequence():
#     if not session.get('logged_in'):
#         return jsonify({'error': 'Please log in first.'}), 401

#     data = request.get_json()
#     data_id = str(uuid.uuid4())
#     data_file_path = f'/home/yjsk/mysite/tasks/{data_id}.json'

#     with open(data_file_path, 'w') as file:
#         json.dump(data, file)

#     redirect_url = f'{data_id}' # = pythonanywhere.com/{data_id}
#     return jsonify({'redirect': redirect_url})


@app.route('/cloning')
def cloning():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('cloning.html')


#LIBRARY W/ RANDOM FILLER
@app.route('/process_sequence_cloning', methods=['POST'])
def process_sequence_cloning():
    if not session.get('logged_in'):
        return jsonify({'error': 'Please log in first.'}), 401

    data = request.get_json()
    data_id = str(uuid.uuid4())
    data_file_path = f'/home/yjsk/mysite/tasks/{data_id}.json'

    with open(data_file_path, 'w') as file:
        json.dump(data, file)

    redirect_url = f'{data_id}' # = pythonanywhere.com/{data_id}
    return jsonify({'redirect': redirect_url})


@app.route('/<data_id>', methods=['GET'])
def get_results(data_id):
    result_path = f'/home/yjsk/library/{data_id}.zip'
    if exists(result_path):
        remove(f'/home/yjsk/mysite/tasks/{data_id}.json')
        return send_file(result_path)
    else:
        return jsonify({'status': 'Library is being generated. Please check back later.'}), 202








