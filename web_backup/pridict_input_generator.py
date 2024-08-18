import pandas as pd
from main import run, run_cloning, run_cloning_, run_homo, _find_rtt,_find_rtts, _r, _c, trim_string, run_synony

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
            original_base = wt_rtt[mutation_index]
            differing_base = rtt[mutation_index]
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


def get_pridict_df(library, seq, sseq, frame):
    seq_ = trim_string(seq, sseq)
    scored_rows = library.groupby('PAM No.', group_keys=False).apply(lambda x: x.iloc[len(x) // 2]).reset_index(drop=True)

    wt_rtts_f = list(_find_rtts(seq=seq_, 
                              rtts=_find_rtt(seq_, '+'), 
                              sseq=sseq, 
                              frame=frame,
                              syn=True,
                              strand='+').keys())
    
    wt_rtts_r = list(_find_rtts(seq=trim_string(seq_, sseq), 
                              rtts=_find_rtt(trim_string(seq_, sseq), '-'), 
                              sseq=sseq, 
                              frame=frame,
                              syn=True,
                              strand='-').keys())
    
    wt_rtts = wt_rtts_f + wt_rtts_r

    pridict_inputs = generate_formatted_strings(scored_rows, seq, wt_rtts)

    scored_rows['PRIDICT input'] = pridict_inputs

    for i, row in scored_rows.iterrows():
        if len(row['PRIDICT input']) != 204:
            continue

        # scored_rows.at[i, 'PRIDICT2.0 score'] = manual_dp(row['PRIDICT input'], row['RTTs'], row['PBS'])
        scored_rows.at[i, 'PRIDICT2.0 score'] = 'yo'

    return scored_rows



# seq = 'gagaccctagtctgccactgaggatttggtttttgcccttccagTGTATACTCTGAAAGAGCGATGCCTCCAGGTTGTCCGGAGCCTAGTCAAGCCTGAGAATTACAGGAGACTGGACATCGTCAGGTCGCTCTACGAAGATcTGGAAGACCACCCAAATGTGCAGAAAGACCTGGAGcGGCTGACACAGGAGCGCATTGCACATCAACGGATGGGAGATTGAAGATTTCTGTTGAAACTTACACTGTTT'.upper()
seq = 'ttttttctttaacctaaagtgagatccatcagtagtacaggtagttgttggcaaagcctcttgttcgttccttgtactgagaccctagtctgccactgaggatttggtttttgcccttccagTGTATACTCTGAAAGAGCGATGCCTCCAGGTTGTCCGGAGCCTAGTCAAGCCTGAGAATTACAGGAGACTGGACATCGTCAGGTCGCTCTACGAAGATcTGGAAGACCACCCAAATGTGCAGAAAGACCTGGAGcGGCTGACACAGGAGCGCATTGCACATCAACGGATGGGAGATTGAAGATTTCTGTTGAAACTTACACTGTTTCATCTCAGCTTTTGATGGTACTGATGAGTCTTGATCTAGATACAGGACTGGTTCCTTCCTTAGTTTCAAAGTGTCTCATTCTCA'.upper()
sseq = 'gatttggtttttgcccttccagTGTATACTCTGAAAGAGCGATGCCTCCAGGTTGTCCGGAGCCTAGTCAAGCCTGAGAATTACAGGAGACTGGACATCGTCAGGTCGCTCTACGAAGATcTGGAAGACCACCCAAATGTGCAGAAAGACCTGGAGcGGCTGACACAGGAGCGCATTGCACATCAACGGATGGGAGATTGAAGATTTCTGTT'.upper()
lib = run_synony(seq, sseq, 2)
get_pridict_df(lib, seq, sseq, 2).to_csv('get_pridict_df.csv')
# seq = trim_string(seq, sseq)
# wt_rtts_f = list(_find_rtts(seq=seq, 
#                               rtts=_find_rtt(seq, '+'), 
#                               sseq=sseq, 
#                               frame=2,
#                               syn=True,
#                               strand='+').keys())
    
# wt_rtts_r = list(_find_rtts(seq=trim_string(seq, sseq), 
#                             rtts=_find_rtt(trim_string(seq, sseq), '-'), 
#                             sseq=sseq, 
#                             frame=2,
#                             syn=True,
#                             strand='-').keys())

# wt_rtts = wt_rtts_f + wt_rtts_r

# print(generate_formatted_strings(lib, seq, wt_rtts))

