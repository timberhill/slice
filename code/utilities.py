import numpy as np


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