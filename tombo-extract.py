import os
from tombo import tombo_helper, tombo_stats, resquiggle
import pandas as pd

def depth_directory(directory: str):
    '''Loop files in the directory to produce coverage plots'''

    for filename in os.listdir(directory):
            if "a8_16s" in filename:
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                sample_level_stats = tombo_stats.LevelStats(file_directory)
                reg_level_stats = sample_level_stats.get_reg_stats('16s1_extended', '+', 1, 1991)
                pd.DataFrame(reg_level_stats).to_csv(str(filename) + ".csv")
            elif "a8_23s" in filename:
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                sample_level_stats = tombo_stats.LevelStats(file_directory)
                reg_level_stats = sample_level_stats.get_reg_stats('23s1_extended', '+', 1, 3341)
                pd.DataFrame(reg_level_stats).to_csv(str(filename) + ".csv")
            elif "g9_16s" in filename:
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                sample_level_stats = tombo_stats.LevelStats(file_directory)
                reg_level_stats = sample_level_stats.get_reg_stats('16s1_extended', '+', 1, 1869)
                pd.DataFrame(reg_level_stats).to_csv(str(filename) + ".csv")
            elif "g9_23s" in filename:
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                sample_level_stats = tombo_stats.LevelStats(file_directory)
                reg_level_stats = sample_level_stats.get_reg_stats('23s1_extended', '+', 1, 3118)
                pd.DataFrame(reg_level_stats).to_csv(str(filename) + ".csv")
            elif "k12_16s" in filename:
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                sample_level_stats = tombo_stats.LevelStats(file_directory)
                reg_level_stats = sample_level_stats.get_reg_stats('16s1_extended', '+', 1, 1813)
                pd.DataFrame(reg_level_stats).to_csv(str(filename) + ".csv")
            elif "k12_23s" in filename:
                file_directory = os.path.join(directory, filename)
                print(file_directory)
                sample_level_stats = tombo_stats.LevelStats(file_directory)
                reg_level_stats = sample_level_stats.get_reg_stats('23s1_extended', '+', 1, 3163)
                pd.DataFrame(reg_level_stats).to_csv(str(filename) + ".csv")

if __name__=='__main__':
        depth_directory('/data/bhargava/filteredrnamods/tombostats/')
