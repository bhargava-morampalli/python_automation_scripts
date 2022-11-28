## import libraries

import fire
import pandas as pd
import numpy as np

## define function to generalize the CSV generation for ROC curve generation for 16s rRNA

def roc(filename, w):
    # read in the output file from nanodoc analysis for 23s rRNA

    nanodoc_23s = pd.read_csv(filename, sep='\t')
    nanodoc_23s.columns = ['position', '5mer', 'depth_tgt', 'depth_ref', 'med_current', 'mad_current', 'med_currentR', 'mad_currentR', 'current_ratio', 'scoreSide1', 'scoreSide2', 'score']

    ## calculate values for ROC for 23s rRNA - add mods column with either yes for known modifications or no for all other positions

    known_mods_23s = [945, 946, 947, 1155, 1818, 2035, 2111, 2115, 2117, 2139, 2162, 2230, 2269, 2451, 2645, 2649, 2657, 2698, 2701, 2703, 2704, 2752, 2780, 2805]
    known_mods_23s_pos = [x+w for x in known_mods_23s]
    known_mods_23s_neg = [x-w for x in known_mods_23s]

    def conditions_23s(a):
        if a in (known_mods_23s + known_mods_23s_pos + known_mods_23s_neg):
            return 1
        else:
            return 0

    nanodoc_23s['mods'] = nanodoc_23s['position'].apply(conditions_23s)

    ## sort the rows based on the log values

    sorted_23s = nanodoc_23s.sort_values('score')

    ## calculate variables required for ROC visualization

    thresholds = list(abs(sorted_23s['score']))

    roc_point = []

    for threshold in thresholds:

        tp = 0; fp = 0; fn = 0; tn = 0

        for index, instance in sorted_23s.iterrows():
            actual = instance["mods"]
            prediction = abs(instance["score"])

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
    pivot.to_csv(filename + "_roc_" + str(w) + "nt_window.tsv")

    return


if __name__ == '__main__':
  fire.Fire(roc)