## import libraries

import fire
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

## define function for ROC curve generation for 16s rRNA and 23s rRNA

def figure(file1, file2, file3):
    
    # read in the ROC files
    
    tombo_16s_1 = pd.read_csv(file1)
    tombo_16s_2 = pd.read_csv(file2)
    tombo_16s_3 = pd.read_csv(file3)
    
    auc_16s_1 = round(abs(np.trapz(tombo_16s_1['tpr'], tombo_16s_1['fpr'])), 4)
    auc_16s_2 = round(abs(np.trapz(tombo_16s_2['tpr'], tombo_16s_2['fpr'])), 4)
    auc_16s_3 = round(abs(np.trapz(tombo_16s_3['tpr'], tombo_16s_3['fpr'])), 4)
    

    ## Generate ROC curves for both 16s rRNA and 23s rRNA
    
    plt.plot(tombo_16s_1["fpr"], tombo_16s_1["tpr"], label = str(auc_16s_1), c='red')
    plt.plot(tombo_16s_2["fpr"], tombo_16s_2["tpr"], label = str(auc_16s_2), c ='blue')
    plt.plot(tombo_16s_3["fpr"], tombo_16s_3["tpr"], label = str(auc_16s_3), c ='green')
    plt.plot([0, 1])

    plt.xlabel('false positive rate')
    plt.ylabel('true positive rate')
    plt.title("ROC curve for Tombo - 16s rRNA")
    plt.legend()

    plt.savefig(file1 + "_plot" + ".pdf" )
    
    return

if __name__ == '__main__':
  fire.Fire(figure)