import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from utilities import *
import settings


def plot_all_lines():
    lines = pd.read_csv(settings.lines_list_path, header=0, delim_whitespace=True)
    file_list = pd.read_csv(settings.list_path, header=0, delim_whitespace=True)
    file_list["filename"] = file_list["filename"].apply(lambda x: x.replace(":", "."))

    labels = [
        [ ["logS", "ew"] , ["rvc", "ew"] ],
        [ ["logS", "asym"] , ["rvc", "asym"] ]
    ]

    for iline, line in lines.iterrows():
        filename = "{}{}.dat".format(int(line["center"]*100), line["name"])
        print("Plotting {}".format(filename) )
        linedata = pd.read_csv(settings.output_path + filename, header=0, delim_whitespace=True)

        data = pd.merge(linedata, file_list, how='inner', on='filename', \
            left_index=False, right_index=False, sort=True, suffixes=('', '_'))
        
        f, ax = plt.subplots(2, 2, figsize=(10,9))

        for i in [0,1]:
            for j in [0,1]:
                xlabel = labels[i][j][0]
                ylabel = labels[i][j][1]

                # compute PCCs, but remove FAR FAR outliers first
                x = data[xlabel][~is_outlier(data[xlabel])]
                x = data[xlabel][~is_outlier(data[ylabel])]
                y = data[ylabel][~is_outlier(data[xlabel])]
                y = data[ylabel][~is_outlier(data[ylabel])]
                
                p, pp = pearsonr(x, y)

                # plot
                ax[i,j].scatter(x, y, 
                    color='#000b29', marker='+', rasterized=True)
                ax[i,j].set_xlabel(xlabel)
                ax[i,j].set_ylabel(ylabel)
                ax[i,j].set_title('p=({:.2f}, {:.2f})'.format(p, pp))
        

        f.suptitle("{} {}".format(line["name"], line["center"]), fontweight='bold')
        plt.tight_layout(pad=3)
        plt.savefig(settings.plots_path + filename.replace(".dat", ".png"))
        plt.close()


if __name__ == "__main__":
    plot_all_lines()
