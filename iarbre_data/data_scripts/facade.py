import sys

from shapely.ops import unary_union
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Init
    ENV_targetProj = os.getenv("TARGET_PROJ")

    # Reproj
    df = checkAndReproj(df, ENV_targetProj)

    # Init timer
    bufferTimer = startTimerLog("Buffer Timer")

    # Buffer 2m
    dfBuffered = makeBufferFromGDF(df, 2)

    # End timer
    endTimerLog(bufferTimer)

    # Union timer
    unionTimer = startTimerLog("Union Timer")

    # Regroup
    unionGeom = unary_union(dfBuffered.geometry)
    dataUnion = {"geometry": unionGeom}
    unionFacadeGDF = gp.GeoDataFrame(dataUnion, crs=ENV_targetProj)
    # TODO: + Clean and repair geom ??

    # End union timer
    endTimerLog(unionTimer)

    # Init timer
    simplifyTimer = startTimerLog("Simplify Timer")

    # Simplify
    dfSimplify = unionFacadeGDF.simplify(1)

    # Reproj
    unionBatiDF = checkAndReproj(dfSimplify, ENV_targetProj)

    # End timer
    endTimerLog(simplifyTimer)

    return unionBatiDF


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("Proximité façade subscript process")

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
