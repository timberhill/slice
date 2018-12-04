

def get_colours_gradient(vals, rgblow, rgbhigh, alpha=(0,1)):
    norm = lambda x, db, ab: db[0] + (x - ab[0]) * (db[1] - db[0]) / (ab[1] - ab[0])

    actual_bounds = min(vals), max(vals)
    
    r = [ norm(val, (rgblow[0], rgbhigh[0]), actual_bounds) for val in vals ]
    g = [ norm(val, (rgblow[1], rgbhigh[1]), actual_bounds) for val in vals ]
    b = [ norm(val, (rgblow[2], rgbhigh[2]), actual_bounds) for val in vals ]

    a = [ norm(val, alpha, actual_bounds) for val in vals ]

    return [(x, y, z) for x,y,z in zip(r, g, b)], a