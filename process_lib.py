import os
import json
from main import _find_rtt, _find_rtts, _r, _c, trim_string, run, run_homo, run_cloning, run_cloning_, run_freq_table, run_freq_plot, run_figure, run_synony, run_synony_homo, run_synony_cloning, run_synony_cloning_homo
from me_peg import manual_dp
import matplotlib.pyplot as plt
from zipfile import ZipFile


def find_mutation_index(original, mutated, strand):
    if strand=='+':
        original = _r(_c(original))
        mutated = _r(_c(mutated))

    for i in range(len(original)):
        if original[i] != mutated[i]:
            return i


def generate_formatted_strings(library, seq, wt_rtts):
    formatted_strings = []

    for _, row in library.iterrows():
        wt_rtt = wt_rtts[row['PAM No.']-1]
        rtt = row['RTTs']
        strand = row['Strand']
        mutation_index = find_mutation_index(wt_rtt, rtt, strand)

        if strand == '-':
            index = seq.find(wt_rtt) + mutation_index
        else:
            index = seq.find(_r(_c(wt_rtt))) + mutation_index

        original_base = _r(_c(wt_rtt))[mutation_index]
        differing_base = _r(_c(rtt))[mutation_index]

        start = max(0, index - 100)
        end = min(len(seq), index + 100)
        pre = seq[start:index]
        post = seq[index+1:end]
        formatted_string = pre + f"({original_base}/{differing_base})" + post
        formatted_strings.append(formatted_string)

    return formatted_strings


def get_pridict_df(seq, sseq, frame):
    seq, sseq = seq.upper(), sseq.upper()
    seq_ = trim_string(seq, sseq)
    library = run(seq, sseq, frame)[0]
    scored_rows = library.groupby('PAM No.', group_keys=False).apply(lambda x: x.iloc[len(x) // 2]).reset_index(drop=True)

    wt_rtts_f = _find_rtt(seq, sseq, strand='+')
    wt_rtts_r = _find_rtt(seq, sseq, strand='-')
    
    wt_rtts = wt_rtts_f + wt_rtts_r

    pridict_inputs = generate_formatted_strings(scored_rows, seq, wt_rtts)

    scored_rows['PRIDICT input'] = pridict_inputs
    for i, row in scored_rows.iterrows():
        if len(row['PRIDICT input']) != 204:
            continue

        # scored_rows.at[i, 'PRIDICT2.0 score'] = manual_dp(row['PRIDICT input'], row['RTTs'], row['PBS'])
        scored_rows.at[i, 'PRIDICT2.0 score'] = 'yo'

    return scored_rows


def process_task(data_id):
    input_path = f'/home/yjsk/mysite/tasks/{data_id}.json'
    with open(input_path, 'r') as file:
        data = json.load(file)

    seq = data.get('dna_sequence')
    sseq = data.get('sat_area')
    frame = int(data.get('frame'))

    df, df_no_ctl, df_only_ctl = run_homo(seq, sseq, frame)
    freq_table = run_freq_table(seq, sseq)
    df_pams = run_synony_homo(seq, sseq, frame)
    df_pridict = get_pridict_df(df, seq, sseq, frame)

    # Create the frequency plot
    plt.figure()
    run_freq_plot(seq, sseq)

    # Create PAM figure
    run_figure(seq, sseq)

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


if __name__ == '__main__':
    print('running...')
    task_files = os.listdir('/home/yjsk/mysite/tasks')
    if task_files:  # Check if there are any files to process
        for filename in task_files:
            data_id = filename.split('.')[0]
            process_task(data_id)




