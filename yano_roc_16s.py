## import libraries

import fire
import pandas as pd
import numpy as np

## define function to generalize the CSV generation for ROC curve generation for 16s rRNA

def roc(filename, w):
    # read in the output file from yano analysis for 16s rRNA
    
    yano_16s = pd.read_csv(filename, sep='\t', header=None)
    
    yano_16s.columns = ["chrom", "start", "end", "gene_id", "score", "strand", "mod_log_R", "pvalue-gtest", "FDR-gtest", "ctrl-frac-mod", "treat-frac-mod", "G-stat-treatvsctrl", "homogeneity", "unmod-mean", "unmod-sd", "mod-mean", "mod-sd", "KS-stat"] 

    ## add a log column with log values of the p value using numpy

    yano_16s["log"] = np.log10(yano_16s["pvalue-gtest"])

    ## calculate values for ROC for 16s rRNA - add mods column with either yes for known modifications or no for all other positions

    known_mods_16s = [716, 727, 1166, 1167, 1407, 1602, 1607, 1698, 1716, 1718, 1719]
    known_mods_16s_pos = [x+w for x in known_mods_16s]
    known_mods_16s_neg = [x-w for x in known_mods_16s]

    def conditions_16s(a):
        if a in (known_mods_16s + known_mods_16s_pos + known_mods_16s_neg):
            return 1
        else:
            return 0
        
    yano_16s['mods'] = yano_16s['start'].apply(conditions_16s)
    yano_16s['mods_end'] = yano_16s['end'].apply(conditions_16s)

    ## sort the rows based on the log values

    sorted_16s = yano_16s.sort_values('log')

    ## calculate variables required for ROC visualization

    thresholds = list(abs(sorted_16s['log']))

    roc_point = []

    for threshold in thresholds:
            
        tp = 0; fp = 0; fn = 0; tn = 0

        for index, instance in sorted_16s.iterrows():
            actual = instance["mods"]
            prediction = abs(instance["log"])

            #print(actual, prediction)
            
            if prediction >= threshold:
                prediction_class = 1
            else:
                prediction_class = 0

            if prediction_class == 1 and actual == 1:
                tp = tp + 1
            elif actual == 1 and prediction_class == 0:
                fn = fn + 1
            elif actual == 0 and prediction_class == 1: 
                fp = fp + 1
            elif actual == 0 and prediction_class == 0:
                tn = tn + 1

        #print(tp, fp, fn, tn)

        tpr = tp / (tp + fn)
        fpr = fp / (tn + fp)

        #print(tpr, fpr)

        roc_point.append([tpr, fpr])        


    ## write out ROC values into a dataframe

    pivot = pd.DataFrame(roc_point, columns=["tpr", "fpr"])
    pivot["threshold"] = thresholds
    pivot.to_csv("roc_" + str(w) + "nt_window_" + filename + ".tsv")
    
    return

if __name__ == '__main__':
  fire.Fire(roc)