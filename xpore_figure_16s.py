## import libraries

import fire
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

## define function for ROC curve generation for 16s rRNA and 23s rRNA

def figure(file1, file2, file3):
    
    # read in the ROC files
    
    xpore_16s_1 = pd.read_csv(file1)
    xpore_16s_2 = pd.read_csv(file2)
    xpore_16s_3 = pd.read_csv(file3)
    
    auc_16s_1 = round(abs(np.trapz(xpore_16s_1['tpr'], xpore_16s_1['fpr'])), 4)
    auc_16s_2 = round(abs(np.trapz(xpore_16s_2['tpr'], xpore_16s_2['fpr'])), 4)
    auc_16s_3 = round(abs(np.trapz(xpore_16s_3['tpr'], xpore_16s_3['fpr'])), 4)
    

    ## Generate ROC curves for both 16s rRNA and 23s rRNA
    
    plt.plot(xpore_16s_1["fpr"], xpore_16s_1["tpr"], label = str(auc_16s_1), c='red')
    plt.plot(xpore_16s_2["fpr"], xpore_16s_2["tpr"], label = str(auc_16s_2), c ='blue')
    plt.plot(xpore_16s_3["fpr"], xpore_16s_3["tpr"], label = str(auc_16s_3), c ='green')
    plt.plot([0, 1])

    plt.xlabel('false positive rate')
    plt.ylabel('true positive rate')
    plt.title("ROC curve for xPore - 16s rRNA")
    plt.legend()

    plt.savefig(file1 + "_plot" + ".pdf")
    
    return

if __name__ == '__main__':
  fire.Fire(figure)
