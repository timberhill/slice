import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr
import spectrum_handlers as sh
import settings
from utilities import *


def pearson(x, y):
    # remove nans and infinities
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)

    return pearsonr(x, y)


lines = pd.read_csv(settings.lines_list_path, header=0, delim_whitespace=True)

# load the template to measure EWs
template = np.load(settings.output_path + "template.npy").item()

# open file and write a header
with open(settings.summary_file, "a") as output_file:
    output_file.truncate(0) # empty the file
    # write file header
    output_file.write("name\t")
    output_file.write("center\t")
    output_file.write("ew\t")
    output_file.write("ew_diff\t")
    output_file.write("asym_diff\t")
    output_file.write("logS_ew_p\t")
    output_file.write("logS_ew_pp\t")
    output_file.write("logS_asym_p\t")
    output_file.write("logS_asym_pp\t")
    output_file.write("rv_ew_p\t")
    output_file.write("rv_ew_pp\t")
    output_file.write("rv_asym_p\t")
    output_file.write("rv_asym_pp\n")

    # summarise stuff for every line
    for i, line in lines.iterrows():
        print("Correlating {} {:.2f}".format(line["name"], line["center"]))
        half_width = (line["center"] - line["ll"]) / 2
        linemask = (settings.wlbase >= line["ll"] - half_width) & (settings.wlbase <= line["rr"] + half_width)
        filepath = "{}{}{}.dat".format(settings.output_path, int(line["center"]*100), line["name"])
        
        # match ew & asymmetry of the line with the original list with rv & logS
        file_list = pd.read_csv(settings.list_path, header=0, delim_whitespace=True)
        file_list["filename"] = file_list["filename"].apply(lambda x: x.replace(":", "."))
        line_data  = pd.read_csv(filepath, header=0, delim_whitespace=True)
        data = pd.merge(file_list, line_data, how="inner", on="filename", \
            left_index=False, right_index=False, sort=True, suffixes=("_orig", ""))
            
        wlbase_masked   = settings.wlbase[linemask]
        template_masked = template["fls"][linemask]

        ew_template = sh.get_eqw(wlbase_masked, template_masked, \
                        r1=[line["cl"], line["cr"]], \
                        r2=[line["ll"], line["lr"]], \
                        r3=[line["rl"], line["rr"]]
                    )
        
        # get amplitude of the line changes -- median of top N active spectra
        # N here is the same as the one used for computation of the template
        top_ew   = np.median(data.nlargest(settings.template_n, "logS")["ew"])
        top_asym = np.median(data.nlargest(settings.template_n, "logS")["asym"])

        # measure 2-tailed pearson correlation coefficients
        logS_ew_p,   logS_ew_pp   = pearson(data["logS"], data["ew"])
        logS_asym_p, logS_asym_pp = pearson(data["logS"], data["asym"])
        rv_ew_p,     rv_ew_pp     = pearson(data["rv"],   data["ew"])
        rv_asym_p,   rv_asym_pp   = pearson(data["rv"],   data["asym"])

        output_file.write("{}\t".format(line["name"]))
        output_file.write("{}\t".format(line["center"]))
        output_file.write("{:.5f}\t".format(ew_template))
        output_file.write("{:.5f}\t".format(top_ew))
        output_file.write("{:.5f}\t".format(top_asym))
        output_file.write("{:.5f}\t".format(logS_ew_p))
        output_file.write("{:.5f}\t".format(logS_ew_pp))
        output_file.write("{:.5f}\t".format(logS_asym_p))
        output_file.write("{:.5f}\t".format(logS_asym_pp))
        output_file.write("{:.5f}\t".format(rv_ew_p))
        output_file.write("{:.5f}\t".format(rv_ew_pp))
        output_file.write("{:.5f}\t".format(rv_asym_p))
        output_file.write("{:.5f}\n".format(rv_asym_pp))



