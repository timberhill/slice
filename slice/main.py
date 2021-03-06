import pandas as pd
import numpy as np
import os
from joblib import Parallel, delayed

import settings as settings
import spectrum_handlers as sh
from plotter import plot_all_lines


def main():
    # SETUP

    # read the list of lines
    lines = pd.read_csv(settings.lines_list_path, header=0, delim_whitespace=True)
    outfiles = ["{}{}.dat".format(int(line["center"]*100), line["name"]) for i, line in lines.iterrows()]

    # write headers in the output files
    for i in range(len(outfiles)):
        with open(settings.output_path + outfiles[i], "w") as out:
            out.write("filename" + "\t")
            out.write("bjd"      + "\t")
            out.write("ew"       + "\t")
            out.write("asym"     + "\t")
            out.write("\n")

    # read the data file
    file_list = pd.read_csv(settings.list_path, header=0, delim_whitespace=True)
    file_list["filename"] = file_list["filename"].apply(lambda x: x.replace(":", "."))

    # get the list of files in the s1d folder
    s1dfiles = pd.DataFrame(
        [
            fname[0:29].replace(":", ".")
            for fname in os.listdir(settings.s1d_folder)
            if fname.endswith("s1d_A.fits")
        ],
        columns=["filename"]
    )

    # combine the two lists
    data = pd.merge(file_list, s1dfiles, how="inner", on="filename", \
        left_index=False, right_index=False, sort=True, suffixes=("_cut", ""))

    # compute low activity template
    template = sh.compute_template(
            data.nsmallest(settings.template_n, "logS"), 
            s1d_folder=settings.s1d_folder,
            wlbase=settings.wlbase
        )
    # save the template for further use
    np.save(settings.output_path + 'template.npy', np.array(template))


    # RUN THE CODE
    def process_file(row, wlbase, template, lines, outfiles):
        print("Processing spectrum {}".format(row["filename"]))

        spectrum = sh.read_spectrum(
            filename=row["filename"] + "_s1d_A.fits", 
            folder=settings.s1d_folder,
            rv=row["rv"],
            wlbase=settings.wlbase
        )

        measurements = sh.measure_all_lines(spectrum, template, lines, np.copy(settings.wlbase))

        for i in range(len(outfiles)):
            with open(settings.output_path + outfiles[i], "a") as out:
                out.write("{}\t".format(row["filename"]))
                out.write("{}\t".format(row["bjd"]))
                out.write("{}\t".format(measurements[i]["ew"]))
                out.write("{}".format(measurements[i]["asym"]))
                out.write("\n")


    # measure lines in all spectra
    if settings.ncores > 1:
        Parallel(n_jobs=settings.ncores)(delayed(process_file)(row, settings.wlbase, template, lines, outfiles) \
            for i, row in data.iterrows())
    else:
        for i, row in data.iterrows():
            process_file(row, settings.wlbase, template, lines, outfiles)

    # plot lines' correlations
    if settings.plots_path is not None:
        plot_all_lines()


if __name__ == "__main__":
    main()
