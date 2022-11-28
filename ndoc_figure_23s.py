## import libraries

import fire
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

## define function for ROC curve generation for 16s rRNA and 23s rRNA

def figure(file4, file5, file6):
    
    # read in the ROC files
    
    ndoc_16s_4 = pd.read_csv(file4)
    ndoc_16s_5 = pd.read_csv(file5)
    ndoc_16s_6 = pd.read_csv(file6)
    
    auc_23s_1 = round(abs(np.trapz(ndoc_16s_4['tpr'], ndoc_16s_4['fpr'])), 4)
    auc_23s_2 = round(abs(np.trapz(ndoc_16s_5['tpr'], ndoc_16s_5['fpr'])), 4)
    auc_23s_3 = round(abs(np.trapz(ndoc_16s_6['tpr'], ndoc_16s_6['fpr'])), 4)
    

    ## Generate ROC curves for both 16s rRNA and 23s rRNA
    
    plt.plot(ndoc_16s_4["fpr"], ndoc_16s_4["tpr"], label = str(auc_23s_1), c='orange')
    plt.plot(ndoc_16s_5["fpr"], ndoc_16s_5["tpr"], label = str(auc_23s_2), c='purple')
    plt.plot(ndoc_16s_6["fpr"], ndoc_16s_6["tpr"], label = str(auc_23s_3), c='brown')
    plt.plot([0, 1])

    plt.xlabel('false positive rate')
    plt.ylabel('true positive rate')
    plt.title("ROC curve for nanoDoc - 23s rRNA")
    plt.legend()

    plt.savefig(file4 + "_plot" + ".pdf")

    return

if __name__ == '__main__':
  fire.Fire(figure)
