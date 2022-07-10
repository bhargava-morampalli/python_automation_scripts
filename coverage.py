import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def depth_directory(directory: str):
    '''Loop files in the directory to produce coverage plots'''

    for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                file = pd.read_csv(file_directory, sep='\t', header=None)
                file.columns = ["chrom", "position", "depth"]
                print(file.head())
                sns.set_theme(style="darkgrid")
                x = sns.relplot(x=file["position"], y=file["depth"], kind='line', height=6, aspect=4)
                plt.fill_between(file["position"], file["depth"], 0, facecolor="orange", color='blue', alpha=0.2)
                plt.yscale('log')
                plt.title("Coverage Plot")
                plt.savefig(str(filename) + ".pdf")

if __name__=='__main__':
        depth_directory('/data/bhargava/combinedrnamods/allfastqs/alldepths/')
