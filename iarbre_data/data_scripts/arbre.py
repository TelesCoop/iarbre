import sys

from shapely.ops import unary_union
from main import ENV_targetProj
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Select only some data
    arbreDF = df.copy()
    arbreDF = arbreDF[
        (arbreDF.genre != "Emplacement libre") & (arbreDF.genre != "Souche")
    ]

    # Buffer on rayoncouronne_m field value
    arbreDF["geometry"] = arbreDF.apply(customBuffer, axis=1)

    # Regroup
    unionGeom = unary_union(arbreDF.geometry)

    # Make GDF
    dataUnion = {"geometry": unionGeom}
    unionDF = gp.GeoDataFrame(dataUnion, crs=ENV_targetProj)

    # Clean data & explode
    currentGeoSerie = unionDF.loc[:, "geometry"]
    # allGeoSerie = currentGeoSerie.explode(index_parts=False)

    # Simplify
    currentGeoSerie = currentGeoSerie.simplify(1)

    # Make GDF
    currGDF = gp.GeoDataFrame(currentGeoSerie)
    currGDF.columns = ["geometry"]

    return currGDF


def customBuffer(row):
    if row.rayoncouro > 0:
        return row.geometry.buffer(row.rayoncouro)
        # return row.geometry.buffer(row.rayoncouronne_m)
    else:
        # Default buffer value 1m
        return row.geometry.buffer(1)


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("Arbre subscript process")

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
