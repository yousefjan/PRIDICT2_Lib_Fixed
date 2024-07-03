from peglit import pegLIT
# from genet.predict import DeepPrime
# from joblib import load
import subprocess
import os
import time
import pandas as pd


U6_homology_arm = "ttatatatcttgtggaaaggacgaaacacc"
pe_scaffold = "gtttcagagctatgctggaaacagcatagcaagttgaaataaggctagtccgttatcaacttgaaaaagtggcaccgagtcggtgc"
tevopreQ1 = "CGCGGTTCTATCTAGTTACGCGTTAAACCAACTAGAA"
tevopreQ1_ori = 'cgcggttctatctagttacgcgttaaaccaactagaatttttttaagcttgggccgctcgaggtacctctctacatatgacatgtgagcaaaaggccagcaaaaggccaggaaccgtaaaaaggccgcgttgctggcgtttttccataggctccgcccccctgacgagcatcacaaaaatcgacgctcaagtcagaggt'


def pl(spacer, rtt, pbs):

    linkers = pegLIT(seq_spacer=spacer, seq_scaffold=pe_scaffold, seq_template=rtt,
                            seq_pbs=pbs, seq_motif=tevopreQ1)

    return linkers[0]


def dp(wts, link, block):
    if len(wts) < 203:
        return 'not available - wts+edit too short'

    command = [
        'python', '/home/yjsk/mysite/PRIDICT2/pridict2_pegRNA_design.py', 'manual',
        '--sequence-name', 'seq',
        '--sequence', wts
    ]

    csv_file_path = '/home/yjsk/mysite/PRIDICT2/predictions/seq_pegRNA_Pridict_full.csv'

    subprocess.run(command, check=True)

    while not os.path.exists(csv_file_path):
        time.sleep(1)

    pridict2_output = pd.read_csv(csv_file_path)

    os.remove(csv_file_path)

    spacer = pridict2_output['Spacer-Sequence'].values[0]
    RTT = pridict2_output['RTrevcomp'].values[0]
    PBS = pridict2_output['PBSrevcomp'].values[0]

    pegrna = pridict2_output['pegRNA'].values[0]

    score=pridict2_output['PRIDICT2_0_editing_Score_deep_HEK'].values[0]

    if link:
        linker = pl(spacer, RTT, PBS)
    else:
        linker = ''

    if block:
        return f'{U6_homology_arm}{pegrna}{linker}{tevopreQ1_ori}\n\nPRIDICT2_0_editing_Score_deep_HEK is {score}'.upper()
    else:
        return f'{U6_homology_arm}{pegrna}{linker}{tevopreQ1}\n\nPRIDICT2_0_editing_Score_deep_HEK is {score}'.upper()


def manual_dp(wts, rtt, pbs):

    wts, rtt, pbs = wts.upper(), rtt.upper(), pbs.upper()

    if len(wts) < 203:
        return 'not available - wts+edit too short'

    command = [
        'python', '/home/yjsk/mysite/PRIDICT2/pridict2_pegRNA_design.py', 'manual',
        '--sequence-name', 'seq',
        '--sequence', wts
    ]

    csv_file_path = '/home/yjsk/mysite/PRIDICT2/predictions/seq_pegRNA_Pridict_full.csv'

    try:
        subprocess.run(command, check=True)
    except Exception as e:
        print(f"Error processing: {e}")
        return 'not available'

    while not os.path.exists(csv_file_path):
        time.sleep(1)

    pridict2_output = pd.read_csv(csv_file_path)

    os.remove(csv_file_path)

    pridict2_output['RTrevcomp'] = pridict2_output['RTrevcomp'].str.upper()
    pridict2_output['PBSrevcomp'] = pridict2_output['PBSrevcomp'].str.upper()

    score_row = pridict2_output.loc[
        (pridict2_output['RTrevcomp'] == rtt) &
        (pridict2_output['PBSrevcomp'] == pbs),
        'PRIDICT2_0_editing_Score_deep_HEK'
    ]

    if score_row.empty:
        return 'RTT not in model output'
    else:
        return score_row.iloc[0]

    return score_row.iloc[0]


