## import libraries

import fire
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

## define function for ROC curve generation for 16s rRNA and 23s rRNA

def figure(file1, file2, file3, file4, file5, file6):
    
    # read in the ROC files
    
    ndoc_16s_1 = pd.read_csv(file1)
    ndoc_16s_2 = pd.read_csv(file2)
    ndoc_16s_3 = pd.read_csv(file3)
    ndoc_16s_4 = pd.read_csv(file4)
    ndoc_16s_5 = pd.read_csv(file5)
    ndoc_16s_6 = pd.read_csv(file6)
    
    auc_16s_1 = round(abs(np.trapz(ndoc_16s_1['tpr'], ndoc_16s_1['fpr'])), 4)
    auc_16s_2 = round(abs(np.trapz(ndoc_16s_2['tpr'], ndoc_16s_2['fpr'])), 4)
    auc_16s_3 = round(abs(np.trapz(ndoc_16s_3['tpr'], ndoc_16s_3['fpr'])), 4)
    
    auc_23s_1 = round(abs(np.trapz(ndoc_16s_4['tpr'], ndoc_16s_4['fpr'])), 4)
    auc_23s_2 = round(abs(np.trapz(ndoc_16s_5['tpr'], ndoc_16s_5['fpr'])), 4)
    auc_23s_3 = round(abs(np.trapz(ndoc_16s_6['tpr'], ndoc_16s_6['fpr'])), 4)
    

    ## Generate ROC curves for both 16s rRNA and 23s rRNA
    
    
    plt.plot(ndoc_16s_1["fpr"], ndoc_16s_1["tpr"], label = str(auc_16s_1), c='red')
    plt.plot(ndoc_16s_2["fpr"], ndoc_16s_2["tpr"], label = str(auc_16s_2), c = 'blue')
    plt.plot(ndoc_16s_3["fpr"], ndoc_16s_3["tpr"], label = str(auc_16s_3), c = 'green')
    plt.plot([0, 1])

    plt.xlabel('false positive rate')
    plt.ylabel('true positive rate')
    plt.title("ROC curve for nanodoc - 16s rRNA")
    plt.legend()

    plt.savefig( "ndoc_16s_roc.pdf" )


    plt.plot(ndoc_16s_4["fpr"], ndoc_16s_4["tpr"], label = str(auc_23s_1), c='orange')
    plt.plot(ndoc_16s_5["fpr"], ndoc_16s_5["tpr"], label = str(auc_23s_2), c='purple')
    plt.plot(ndoc_16s_6["fpr"], ndoc_16s_6["tpr"], label = str(auc_23s_3), c='brown')
    plt.plot([0, 1])

    plt.xlabel('false positive rate')
    plt.ylabel('true positive rate')
    plt.title("ROC curve for nanodoc - 23s rRNA")
    plt.legend()

    plt.savefig( "ndoc_23s_roc.pdf" )

    
    return

if __name__ == '__main__':
  fire.Fire(figure)