## import libraries

import fire
from tombo import tombo_helper, tombo_stats, resquiggle
import pandas as pd

## define function to generalize the CSV generation for ROC curve generation for 16s rRNA


def extract(statsfile):
    
    # read in the output file from xpore analysis for 16s rRNA

    sample_level_stats = tombo_stats.LevelStats(statsfile)
    
    reg_level_stats = sample_level_stats.get_reg_stats('16s_88_rrsE', '+', 1, 1813)
    
    pd.DataFrame(reg_level_stats).to_csv(statsfile + ".csv")

    return


if __name__ == '__main__':
  fire.Fire(extract)
