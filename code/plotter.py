import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import settings as settings


def get_colours_gradient(vals, rgblow, rgbhigh, alpha=(0,1)):
    norm = lambda x, db, ab: db[0] + (x - ab[0]) * (db[1] - db[0]) / (ab[1] - ab[0])

    actual_bounds = min(vals), max(vals)
    
    r = [ norm(val, (rgblow[0], rgbhigh[0]), actual_bounds) for val in vals ]
    g = [ norm(val, (rgblow[1], rgbhigh[1]), actual_bounds) for val in vals ]
    b = [ norm(val, (rgblow[2], rgbhigh[2]), actual_bounds) for val in vals ]

    a = [ norm(val, alpha, actual_bounds) for val in vals ]

    return [(x, y, z) for x,y,z in zip(r, g, b)], a


def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh
	


def plot_all_lines():
    lines = pd.read_csv(settings.lines_list_path, header=0, delim_whitespace=True)
    file_list = pd.read_csv(settings.list_path, header=0, delim_whitespace=True)
    file_list["filename"] = file_list["filename"].apply(lambda x: x.replace(":", "."))

    for iline, line in lines.iterrows():
        filename = "{}{}.dat".format(int(line["center"]), line["name"])
        print("Plotting {}".format(filename) )
        linedata = pd.read_csv(settings.output_path + filename, header=0, delim_whitespace=True)

        data = pd.merge(linedata, file_list, how='inner', on='filename', \
            left_index=False, right_index=False, sort=True, suffixes=('', '_'))
        
        f, ax = plt.subplots(2, 2, figsize=(10,9))

        labels = [
            [ ["logS", "ew"] , ["rvc", "ew"] ],
            [ ["logS", "asym"] , ["rvc", "asym"] ]
        ]

        for i in [0,1]:
            for j in [0,1]:
                xlabel = labels[i][j][0]
                ylabel = labels[i][j][1]

                # compute PCCs
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

plot_all_lines()
