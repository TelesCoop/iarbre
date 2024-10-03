import sys

from shapely.ops import unary_union
from main import ENV_targetProj
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Buffer 2m
    df = makeBufferFromGDF(df, 2)

    # Regroup
    unionGeom = unary_union(df)

    # Make GDF
    dataUnion = {"geometry": unionGeom}
    unionDF = gp.GeoDataFrame(dataUnion, crs=ENV_targetProj)

    return unionDF


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("Fibre subscript process")

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
