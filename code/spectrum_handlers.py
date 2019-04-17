import os
import numpy as np
from astropy.io import fits
from scipy.interpolate import interp1d
import settings as settings


def doppler_shift(wls, fls, rv, wlbase=[]):
    c = 299792.458 # km/s
    doppler_factor = np.sqrt( ( 1 + rv/c) / (1 - rv/c) )
    new_wls = wls * doppler_factor
    f = interp1d(new_wls, fls, kind=1, fill_value="extrapolate")

    if len(wlbase) > 0:
        return { "wls" : wlbase,        "fls" : f(np.copy(wlbase)) }
    else:
        return { "wls" : np.array(wls), "fls" : f(wls) }


def read_spectrum(filename, folder="", rv=0, wlbase=[], norm=False):
    f = fits.open(folder + filename)

    wl0 = f[0].header["CRVAL1"]
    wl_step = f[0].header["CDELT1"]
    wls = np.array( [ wl0 + i*wl_step for i in range(0, len(f[0].data))] )
    fls = f[0].data.astype("f8") / f[0].header["EXPTIME"]

    f.close()

    spectrum = doppler_shift(
        wls=np.array(wls),
        fls=np.array(fls),
        rv=-rv,
        wlbase=wlbase
    )

    # normalise
    m = np.median(spectrum["fls"][(spectrum["wls"] > 5600)&(spectrum["wls"] < 5700)])
    spectrum["fls"] /= m
    spectrum["filename"] = filename

    return spectrum


def compute_template(data, s1d_folder, wlbase, method=np.median):
    print("Computing template...")
    stack = []
    for i, row in data.iterrows():
        print("\tAdding {}, logS = {}".format(row["filename"], "{0:.3f}".format(row["logS"])))
        
        spectrum = read_spectrum(
            filename=row["filename"] + "_s1d_A.fits", 
            folder=s1d_folder,
            rv=row["rv"],
            wlbase=wlbase,
            norm=True
        )

        stack.append(spectrum["fls"])
        
    template = { "wls" : wlbase, "fls" : method(np.array(stack), axis=0)}
    
    print("Done.")
    return template


def get_eqw(w, f, r1, r2=[0,0], r3=[0,0], cont=-1e10):
    """
    Measure equivalent width
    r1 = core of the line
    continuum is estimated from r2 and r3 unless the value is explicitly specified
    """
    ys1 = np.asarray(f[ (w >= float(r1[0])) & (w <= float(r1[1])) ])
    ys2 = np.asarray(f[ (w >= float(r2[0])) & (w <= float(r2[1])) ])
    ys3 = np.asarray(f[ (w >= float(r3[0])) & (w <= float(r3[1])) ])

    if cont < -1e9:
        cont = np.median( list(ys2) + list(ys3) )

    lineArea = cont * abs(r1[1] - r1[0]) - ys1.sum()*0.01    
    eqw = lineArea / cont

    return eqw


def get_relative_flux(wavelengths, fluxes, rng):
    """
    Just sum up the pixel values in the range
    """
    return np.sum(fluxes[ (wavelengths >= float(rng[0])) & (wavelengths <= float(rng[1])) ])


def compute_relative_spectrum(spectrum, template, wlbase):
    relative = spectrum["fls"] / template["fls"]
    relative[np.isnan(relative)] = 0
    relative[relative == np.inf] = 0

    # bin spectrum (median)
    # this corrects for variations in the continuum abd incorrect blaze corrections
    temp = wlbase[0]
    binsize = 10
    bins, binvalues = [], []
    while temp <= wlbase[-1]:
        spectrum_bit = relative[ (wlbase > temp) & (wlbase <= temp+binsize) ]
        if len(spectrum_bit) > 0:
            bins.append(temp + binsize / 2)
            binvalues.append( np.median(spectrum_bit) )
        temp += binsize
    
    fit = interp1d(bins, binvalues, kind="cubic", fill_value="extrapolate")

    return relative - fit(wlbase) + 1


def measure_all_lines(spectrum, template, lines, wlbase):
    relative = compute_relative_spectrum(spectrum, template, wlbase)
    measurements = []

    for i, line in lines.iterrows():
        #  get the bit of the spectrum where the line is
        linemask = (wlbase >= line["ll"]) & (wlbase <= line["rr"])
        wlbase_masked = wlbase[linemask]
        relative_masked = relative[linemask]
        # flux_masked = spectrum["fls"][linemask]

        # compute equivalent width of the line
        ew = get_eqw(
                wlbase_masked, relative_masked, \
                r1=[line["cl"], line["cr"]], \
                r2=[line["ll"], line["lr"]], \
                r3=[line["rl"], line["rr"]],
            )

        # compute flux difference on the right and left (from relative spectra)
        left_limit  = line["center"] - (line["cr"] - line["cl"]) / 2.0
        right_limit = line["center"] + (line["cr"] - line["cl"]) / 2.0
        left_mask = \
            (wlbase >= left_limit) & \
            (wlbase <= line["center"])
        right_mask = \
            (wlbase >= line["center"]) & \
            (wlbase <= right_limit )
        left_flux  = np.mean(relative[left_mask ])
        right_flux = np.mean(relative[right_mask])
        asym = right_flux - left_flux

        measurements.append({
            "species"   : line["name"],
            "center"    : line["center"],
            "ew"        : ew,
            "asym"      : asym
        })

    return measurements