import sys

from shapely.ops import unary_union
from main import ENV_targetProj
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Select only some data
    strateBasseDF = df.copy()
    strateBasseDF = strateBasseDF[
        (strateBasseDF.gl_2015 == 12)
        | (strateBasseDF.gl_2015 == 13)
        | (strateBasseDF.gl_2015 == 14)
        | (strateBasseDF.gl_2015 == 16)
        | (strateBasseDF.gl_2015 == 17)
        | (strateBasseDF.gl_2015 == 361)
        | (strateBasseDF.gl_2015 == 362)
    ]

    # Clean data & explode
    currentGeoSerie = strateBasseDF.loc[:, "geometry"]
    allGeoSerie = currentGeoSerie.explode(index_parts=False)

    # Simplify
    allGeoSerie = allGeoSerie.simplify(3)

    # Make GDF
    currGDF = gp.GeoDataFrame(allGeoSerie)
    currGDF.columns = ["geometry"]

    return currGDF


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("EVA Strate basse subscript process")

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
