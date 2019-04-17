import settings as settings
import spectrum_handlers as sh
import pandas as pd
import numpy as np
import os
from joblib import Parallel, delayed



# read the data file
file_list = pd.read_csv(settings.list_path, header=0, delim_whitespace=True)
# file_list["filename"] = file_list["filename"].apply(lambda x: x.replace(":", "."))

# get the list of files in the s1d folder
s1dfiles = pd.DataFrame(
    [
        fname[0:29]#.replace(":", ".")
        for fname in os.listdir(settings.s1d_folder)
        if fname.endswith("s1d_A.fits")
    ],
    columns=["filename"]
)

# combine the two lists
data = pd.merge(file_list, s1dfiles, how="inner", on="filename", \
    left_index=False, right_index=False, sort=True, suffixes=("_cut", ""))
telluric_data = pd.read_csv("/home/timberhill/repositories/AlphaCen/data/gatherer_telluric.dat", header=0, delim_whitespace=True)

data = pd.merge(data, telluric_data, how="inner", on="filename", \
    left_index=False, right_index=False, sort=True, suffixes=("_cut", ""))

print(len(data))
data = data[ data["filename"].str.startswith("HARPS.2009") ]
print(len(data))


# compute high telluric template
hightemplate = sh.compute_template(
        data.nlargest(settings.template_n, "water6544"), 
        s1d_folder=settings.s1d_folder,
        wlbase=settings.wlbase,
        method=np.median
    )

# compute low telluric template
lowtemplate = sh.compute_template(
        data.nsmallest(settings.template_n, "water6544"), 
        s1d_folder=settings.s1d_folder,
        wlbase=settings.wlbase,
        method=np.median
    )

telluric_template = sh.compute_relative_spectrum(hightemplate, lowtemplate, settings.wlbase)


# iodine wavelength range ? 
mask = (settings.wlbase >= 5000) #& (settings.wlbase <= 6300)
telluric_template = {
    "wls" : settings.wlbase[mask],
    "fls" : telluric_template[mask]
}

# find the lines
# see https://stackoverflow.com/questions/24656367/find-peaks-location-in-a-spectrum-numpy
from scipy.signal import find_peaks
Y = telluric_template["fls"] - 1
X = telluric_template["wls"]
Y *= -1 # flip it to find maxima
# get the actual peaks
peaks, _ = find_peaks(Y, height=0.02, distance=2)
# multiply back for plotting purposes
Y *= -1

# plot the thing
import matplotlib.pyplot as plt
plt.plot(X, Y)
plt.plot(X[peaks], Y[peaks], "x")
plt.show()


# save the template for further use
np.save(os.path.join(settings.output_path, "telluric_template.npy"), np.array(telluric_template))
# save telluric lines list
table = np.array([X[peaks], -Y[peaks]]).T
np.savetxt(fname=os.path.join(settings.output_path, "telluric_lines.dat"), 
            X=table,
            header="wavelength\tdepth",
            delimiter="\t",
            fmt=['%0.2f', '%0.5f'])