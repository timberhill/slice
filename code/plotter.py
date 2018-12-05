import pandas as pd
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
                p, pp = pearsonr(data[xlabel], data[ylabel])

                # plot
                ax[i,j].scatter(data[xlabel], data[ylabel], 
                    color='#000b29', marker='+', rasterized=True)
                ax[i,j].set_xlabel(xlabel)
                ax[i,j].set_ylabel(ylabel)
                ax[i,j].set_title('p=({:.2f}, {:.2f})'.format(p, pp))
        

        f.suptitle("{} {}".format(line["name"], line["center"]), fontweight='bold')
        plt.tight_layout(pad=3)
        plt.savefig(settings.plots_path + filename.replace(".dat", ".png"))
        plt.close()

plot_all_lines()