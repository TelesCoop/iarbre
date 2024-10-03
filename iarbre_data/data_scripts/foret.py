import sys

from shapely.ops import unary_union
from main import ENV_targetProj
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Select only some data
    strateForetDF = df.copy()
    strateForetDF = strateForetDF[
        (strateForetDF.gl_2015 == 311)
        | (strateForetDF.gl_2015 == 312)
        | (strateForetDF.gl_2015 == 322)
        | (strateForetDF.gl_2015 == 331)
        | (strateForetDF.gl_2015 == 341)
        | (strateForetDF.gl_2015 == 342)
        | (strateForetDF.gl_2015 == 351)
        | (strateForetDF.gl_2015 == 371)
        | (strateForetDF.gl_2015 == 372)
        | (strateForetDF.gl_2015 == 374)
        | (strateForetDF.gl_2015 == 411)
        | (strateForetDF.gl_2015 == 412)
    ]

    # Clean data & explode
    currentGeoSerie = strateForetDF.loc[:, "geometry"]
    allGeoSerie = currentGeoSerie.explode(index_parts=False)

    # Simplify
    allGeoSerie = allGeoSerie.simplify(3)

    # Make GDF
    currGDF = gp.GeoDataFrame(allGeoSerie)
    currGDF.columns = ["geometry"]

    return currGDF


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("EVA Forêts subscript process")

    # Get data with temp filename in argv
    argv = sys.argv[1:]
    firstArgv = None
    secArgv = None

    # Argv exist ?
    if argv:
        if len(sys.argv[1:]) > 0:
            firstArgv = sys.argv[1:][0]
        else:
            wrongArguments()

        if len(sys.argv[1:]) > 1:
            secArgv = sys.argv[1:][1]
        else:
            wrongArguments()

        # Load file Data (geoJSON)
        currentGDF = createGDFfromGeoJSON(firstArgv)

        # Log & Launch treatment
        currentGDF = computeData(currentGDF)

        # Write Result in temp file
        currentGDF.to_file(secArgv)

        # End timer
        endTimerLog(subTimer)
    else:
        wrongArguments()
