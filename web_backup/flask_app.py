from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from flask_session import Session
from me_peg import dp, manual_dp
import os
import matplotlib.pyplot as plt
from zipfile import ZipFile
import json
import uuid

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


@app.route('/library')
def library():
    if not session.get('logged_in'):
        return redirect('/')

    return render_template('library.html')


@app.route('/process_sequence', methods=['POST'])
def process_sequence():
    if not session.get('logged_in'):
        return jsonify({'error': 'Please log in first.'}), 401

    data = request.get_json()
    data_id = str(uuid.uuid4())
    data_file_path = f'/home/yjsk/mysite/tasks/{data_id}.json'

    with open(data_file_path, 'w') as file:
        json.dump(data, file)

    redirect_url = f'{data_id}'
    return jsonify({'redirect': redirect_url})

@app.route('/<data_id>', methods=['GET'])
def get_results(data_id):
    result_path = f'/home/yjsk/mysite/results/Lib_oSF_HA_{data_id}.zip'
    try:
        return send_file(result_path)
    except FileNotFoundError:
        return jsonify({'status': 'Library is being generated. Please check back later.'}), 202




#LIBRARY W/ SCAFFOLD W/ HOMO
@app.route('/process_sequence_homo', methods=['POST'])
def process_sequence_homo():
    if not session.get('logged_in'):
        return jsonify({'error': 'Please log in first.'}), 401

    data = request.get_json()
    dna_sequence = data.get('dna_sequence')
    sat_area = data.get('sat_area')
    frame = int(data.get('frame'))

    try:
        df, df_no_ctl, df_only_ctl = run_homo(dna_sequence, sat_area, frame)
        freq_table = run_freq_table(dna_sequence, sat_area)
        df_pams = run_synony_homo(dna_sequence, sat_area, frame)
        df_pridict = get_pridict_df(df, dna_sequence, sat_area, frame)

        # Create the frequency plot
        plt.figure()
        run_freq_plot(dna_sequence, sat_area)

        # Create PAM figure
        run_figure(dna_sequence, sat_area)

        pdf_filename = '/home/yjsk/library/freq_plot.pdf'
        pdf_filename_fig = '/home/yjsk/library/pam_figure.pdf'

        csv_filename = '/home/yjsk/library/Lib_oSF_HA_full_sequences.csv'
        csv_filename_no = '/home/yjsk/library/Lib_oSF_HA_no_ctl.csv'
        csv_filename_only = '/home/yjsk/library/Lib_oSF_HA_only_ctl.csv'
        csv_filename_pams  = '/home/yjsk/library/Lib_oSF_HA_full_sequences_synmut.csv'
        csv_filename_freq = '/home/yjsk/library/Lib_oSF_HA_epeg_frequency_table.csv'
        csv_filename_pridict = '/home/yjsk/library/Lib_oSF_HA_scored.csv'
        zip_filename = '/home/yjsk/library/Lib_oSF_HA.zip'

        df.to_csv(csv_filename, index=False)
        df_no_ctl.to_csv(csv_filename_no, index=False)
        df_only_ctl.to_csv(csv_filename_only, index=False)
        freq_table.to_csv(csv_filename_freq, index=False)
        df_pams.to_csv(csv_filename_pams)
        df_pridict.to_csv(csv_filename_pridict, index=False)

        # Create a ZIP file containing both CSV files and the PDF
        with ZipFile(zip_filename, 'w') as z:
            z.write(csv_filename, arcname=csv_filename.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(csv_filename_no, arcname=csv_filename_no.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(csv_filename_only, arcname=csv_filename_only.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(csv_filename_freq, arcname=csv_filename_freq.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(csv_filename_pams, arcname=csv_filename_pams.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(csv_filename_pridict, arcname=csv_filename_pridict.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(pdf_filename.replace('/library', ''), arcname=pdf_filename.replace('/home/yjsk/library', '/Lib_oSF_HA'))
            z.write(pdf_filename_fig.replace('/library', ''), arcname=pdf_filename_fig.replace('/home/yjsk/library', '/Lib_oSF_HA'))


        # Clean up temporary files
        os.remove(pdf_filename.replace('/library', ''))
        os.remove(pdf_filename_fig.replace('/library', ''))
        os.remove(csv_filename)
        os.remove(csv_filename_no)
        os.remove(csv_filename_only)
        os.remove(csv_filename_freq)
        os.remove(csv_filename_pams)
        os.remove(csv_filename_pridict)

        # Return the ZIP file to the client for download
        return send_file(zip_filename, as_attachment=True,
        download_name=zip_filename.replace('/home/yjsk/library', '/Lib_oSF_HA'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/cloning')
def cloning():
    if not session.get('logged_in'):
        return redirect('/')

    return render_template('cloning.html')


#LIBRARY FOR CLONING (W/ HOMO)
@app.route('/process_sequence_cloning', methods=['POST'])
def process_sequence_cloning():
    if not session.get('logged_in'):
        return jsonify({'error': 'Please log in first.'}), 401

    data = request.get_json()
    dna_sequence = data.get('dna_sequence')
    sat_area = data.get('sat_area')
    frame = int(data.get('frame'))

    try:
        df, df_no_ctl, df_only_ctl = run_cloning(dna_sequence, sat_area, frame)
        freq_table = run_freq_table(dna_sequence, sat_area)
        df_pams = run_synony_cloning_homo(dna_sequence, sat_area, frame)
        # df_pridict = get_pridict_df(df, dna_sequence, sat_area, frame)

        # Create the frequency plot
        plt.figure()
        run_freq_plot(dna_sequence, sat_area)

        # Create PAM figure
        run_figure(dna_sequence, sat_area)

        pdf_filename = '/home/yjsk/library/freq_plot.pdf'
        pdf_filename_fig = '/home/yjsk/library/pam_figure.pdf'

        csv_filename = '/home/yjsk/library/Lib_Rd_HA_full_sequences.csv'
        csv_filename_no = '/home/yjsk/library/Lib_Rd_HA_no_ctl.csv'
        csv_filename_only = '/home/yjsk/library/Lib_Rd_HA_only_ctl.csv'
        csv_filename_pams  = '/home/yjsk/library/Lib_Rd_HA_full_sequences_synmut.csv '
        csv_filename_freq = '/home/yjsk/library/Lib_Rd_HA_epeg_frequency_table.csv'
        # csv_filename_pridict = '/home/yjsk/library/Lib_Rd_HA_scored.csv'
        zip_filename = '/home/yjsk/library/Lib_Random_HA.zip'

        df.to_csv(csv_filename, index=False)
        df_no_ctl.to_csv(csv_filename_no, index=False)
        df_only_ctl.to_csv(csv_filename_only, index=False)
        freq_table.to_csv(csv_filename_freq, index=False)
        df_pams.to_csv(csv_filename_pams)
        # df_pridict.to_csv(csv_filename_pridict, index=False)

        # Create a ZIP file containing both CSV files and the PDF
        with ZipFile(zip_filename, 'w') as z:
            z.write(csv_filename, arcname=csv_filename.replace('/home/yjsk/library', '/Lib_Random_HA'))
            z.write(csv_filename_no, arcname=csv_filename_no.replace('/home/yjsk/library', '/Lib_Random_HA'))
            z.write(csv_filename_only, arcname=csv_filename_only.replace('/home/yjsk/library', '/Lib_Random_HA'))
            z.write(csv_filename_freq, arcname=csv_filename_freq.replace('/home/yjsk/library', '/Lib_Random_HA'))
            z.write(csv_filename_pams, arcname=csv_filename_pams.replace('/home/yjsk/library', '/Lib_Random_HA'))
            # z.write(csv_filename_pridict, arcname=csv_filename_pridict.replace('/home/yjsk/library', '/Lib_Random_HA'))
            z.write(pdf_filename.replace('/library', ''), arcname=pdf_filename.replace('/home/yjsk/library', '/Lib_Random_HA'))
            z.write(pdf_filename_fig.replace('/library', ''), arcname=pdf_filename_fig.replace('/home/yjsk/library', '/Lib_Random_HA'))


        # Clean up temporary files
        os.remove(pdf_filename.replace('/library', ''))
        os.remove(pdf_filename_fig.replace('/library', ''))
        os.remove(csv_filename)
        os.remove(csv_filename_no)
        os.remove(csv_filename_only)
        os.remove(csv_filename_freq)
        os.remove(csv_filename_pams)
        # os.remove(csv_filename_pridict)

        # Return the ZIP file to the client for download
        return send_file(zip_filename, as_attachment=True,
        download_name=zip_filename.replace('/home/yjsk/library', '/Lib_Random_HA'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


#LIBRARY FOR CLONING (W/O HOMO)
@app.route('/process_sequence_cloning_nohomo', methods=['POST'])
def process_sequence_cloning_nohomo():
    if not session.get('logged_in'):
        return jsonify({'error': 'Please log in first.'}), 401

    data = request.get_json()
    dna_sequence = data.get('dna_sequence')
    sat_area = data.get('sat_area')
    frame = int(data.get('frame'))

    try:
        df, df_no_ctl, df_only_ctl = run_cloning_(dna_sequence, sat_area, frame)
        freq_table = run_freq_table(dna_sequence, sat_area)
        df_pams = run_synony_cloning(dna_sequence, sat_area, frame)
        # df_pridict = get_pridict_df(df, dna_sequence, sat_area, frame)

        # Create the frequency plot
        plt.figure()
        run_freq_plot(dna_sequence, sat_area)

        # Create PAM figure
        run_figure(dna_sequence, sat_area)

        pdf_filename = '/home/yjsk/library/freq_plot.pdf'
        pdf_filename_fig = '/home/yjsk/library/pam_figure.pdf'

        csv_filename = '/home/yjsk/library/Lib_Rd_noHA_full_sequences.csv'
        csv_filename_no = '/home/yjsk/library/Lib_Rd_noHA_no_ctl.csv'
        csv_filename_only = '/home/yjsk/library/Lib_Rd_noHA_only_ctl.csv'
        csv_filename_pams  = '/home/yjsk/library/Lib_Rd_noHA_full_sequences_synmut.csv '
        csv_filename_freq = '/home/yjsk/library/Lib_Rd_noHA_epeg_frequency_table.csv'
        # csv_filename_pridict = '/home/yjsk/library/Lib_Rd_noHA_scored.csv'
        zip_filename = '/home/yjsk/library/Lib_Random_noHA.zip'

        df.to_csv(csv_filename, index=False)
        df_no_ctl.to_csv(csv_filename_no, index=False)
        df_only_ctl.to_csv(csv_filename_only, index=False)
        freq_table.to_csv(csv_filename_freq, index=False)
        df_pams.to_csv(csv_filename_pams)
        # df_pridict.to_csv(csv_filename_pridict, index=False)

        # Create a ZIP file containing both CSV files and the PDF
        with ZipFile(zip_filename, 'w') as z:
            z.write(csv_filename, arcname=csv_filename.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            z.write(csv_filename_no, arcname=csv_filename_no.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            z.write(csv_filename_only, arcname=csv_filename_only.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            z.write(csv_filename_freq, arcname=csv_filename_freq.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            z.write(csv_filename_pams, arcname=csv_filename_pams.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            # z.write(csv_filename_pridict, arcname=csv_filename_pridict.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            z.write(pdf_filename.replace('/library', ''), arcname=pdf_filename.replace('/home/yjsk/library', '/Lib_Random_noHA'))
            z.write(pdf_filename_fig.replace('/library', ''), arcname=pdf_filename_fig.replace('/home/yjsk/library', '/Lib_Random_noHA'))


        # Clean up temporary files
        os.remove(pdf_filename.replace('/library', ''))
        os.remove(pdf_filename_fig.replace('/library', ''))
        os.remove(csv_filename)
        os.remove(csv_filename_no)
        os.remove(csv_filename_only)
        os.remove(csv_filename_freq)
        os.remove(csv_filename_pams)
        # os.remove(csv_filename_pridict)

        # Return the ZIP file to the client for download
        return send_file(zip_filename, as_attachment=True,
        download_name=zip_filename.replace('/home/yjsk/library', '/Lib_Random_noHA'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500







