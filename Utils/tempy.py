import json
import numpy as np
import sys
#from geompy import Polygon2d

def get_polygon_from_geojson(file_path,fnr_to_find):
    
    with open(file_path) as f:
        data = json.load(f)
    print("\nsearching for building with id", fnr_to_find,end="")
    for feature in data['features']:
        fnr = feature['properties']['FNR_BR']
        if(fnr == fnr_to_find):
            print("FOUND IT!")
            points = np.squeeze(np.array(feature['geometry']['coordinates']))      
            polygon = Polygon2d(points)

    return polygon

def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '?' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()
def get_peking_fanz():
    points = [[  568236.1875,  6494307.5],
    [  568234.9375 , 6494308.],
    [  568237.5    , 6494326.],
    [  568243.4375 , 6494325.],
    [  568244.1875 , 6494330.5],
    [  568238.25   , 6494331.],
    [  568244.1875 , 6494373.5],
    [  568250.125  , 6494372.5],
    [  568250.875  , 6494378.],
    [  568244.9375 , 6494378.5],
    [  568247.4375 , 6494397.],
    [  568261.0625 , 6494395.],
    [  568261.     , 6494394.5],
    [  568260.25   , 6494389.],
    [  568260.1875 , 6494389.],
    [  568259.4375 , 6494383.5],
    [  568259.375  , 6494383.],
    [  568258.5625 , 6494377.5],
    [  568258.5    , 6494377.],
    [  568257.75   , 6494371.5],
    [  568257.6875 , 6494371.],
    [  568256.9375 , 6494365.5],
    [  568256.875  , 6494365.],
    [  568256.0625 , 6494359.5],
    [  568256.     , 6494359.],
    [  568255.25   , 6494353.5],
    [  568255.1875 , 6494353.],
    [  568254.375  , 6494347.5],
    [  568254.375  , 6494347.],
    [  568253.5625 , 6494341.5],
    [  568253.5    , 6494341.5],
    [  568252.75   , 6494335.5],
    [  568252.6875 , 6494335.5],
    [  568251.875  , 6494330.],
    [  568251.875  , 6494329.5],
    [  568251.0625 , 6494324.],
    [  568251.     , 6494323.5],
    [  568250.25   , 6494318.],
    [  568250.1875 , 6494317.5],
    [  568249.375  , 6494312.],
    [  568249.375  , 6494311.5],
    [  568248.5625 , 6494306.5],
    [  568248.5625 , 6494306.],
    [  568248.5    , 6494305.5],
    [  568236.125  , 6494307.5],
    [  568236.1875 , 6494307.5]]
    return points

