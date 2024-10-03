import sys

from shapely.ops import unary_union
from main import ENV_targetProj
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Select only some data
    soucheDF = df.copy()
    soucheDF = soucheDF[
        (soucheDF.genre == "Emplacement libre") | (soucheDF.genre == "Souche")
    ]

    # Buffer 1m
    soucheDF = makeBufferFromGDF(soucheDF, 1)

    return soucheDF


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("Arbre souche subscript process")

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
