# SETTINGS

lines_list_path = "../data/active_lines.dat"

list_path    = "../data/rvdata.dat" # list of files containing columns "filename", "rv"[in km/s] and "logS"
# s1d_folder = "../data/s1d/" # folder which contains *s1d*.fits files from HARPS DRS
s1d_folder   = "/media/timberhill/TIMBERSTICK/s1d/"
output_path  = "../data/results/" # save per-line measurements here (1 file per line)
summary_file = "../data/results.dat" # file to save aggregated line data as amplitudes and correlation coefficients
plots_path = "../data/plots/"

template_n   = 10 # number of spectra to stack for low activity template
ncores       = 2 # number of cores to utilize


# common wavelength base
import numpy as np
wlbase = np.arange(3800, 6850, 0.01)
ccdgap = (wlbase > 5300) & (wlbase < 5340)
wlbase = wlbase[~ccdgap]