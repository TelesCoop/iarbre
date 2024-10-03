import sys

from shapely.ops import unary_union
from shapely import wkt
from utils import *


def computeData(df):
    """
    Specific treatments
    """

    # Init var
    DB_params = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PWD"),
        "database": os.getenv("DB_NAME"),
    }
    DB_schema = os.getenv("DB_SCHEMA")
    ENV_targetProj = os.getenv("TARGET_PROJ")

    # TODO: Reproj
    df = checkAndReproj(df, ENV_targetProj)

    print("df input")
    print(df)
    print(type(df))
    print(df.geom_type)
    print(df.loc[[0], "geometry"])
    print(type(df.loc[[0], "geometry"]))
    # print(df.loc[[0],'geometry'][1]._geom)

    # Init timer
    unionTimer = startTimerLog("Union Timer")

    # Convert geom str to WKT
    df["geometry"] = df.geometry.apply(lambda x: wkt.dumps(x))
    print(df)
    df["geometry"] = df.geometry.apply(lambda x: wkt.loads(x))
    print(df)

    # Regroup
    unionGeom = unary_union(df)
    # Make GDF
    dataUnion = {"geometry": unionGeom}
    unionParcelleDF = gp.GeoDataFrame(dataUnion, crs=ENV_targetProj)

    # TODO: Reproj
    unionParcelleDF = checkAndReproj(unionParcelleDF, ENV_targetProj)

    # End timer
    endTimerLog(unionTimer)

    # Get communes datas
    query = "SELECT geom_poly as geom FROM " + DB_schema + ".commmunes"
    communesGDF = getGDFfromDB(DB_params, query, ENV_targetProj)

    # Init timer
    substractTimer = startTimerLog("Substract Timer")

    # Substract with existing batiment geom
    diffDF = gp.overlay(communesGDF, unionParcelleDF, how="difference")
    print(diffDF)
    print(type(diffDF))

    # DEBUG
    # diffDF.to_file("./file_data/bati_result_overlay.shp")

    # End timer
    endTimerLog(substractTimer)

    ### IS_EMPTY ? ###
    # facadeGDF = checkAndDeleteEmptyGeomFromGDF(facadeGDF)

    return diffDF


if __name__ == "__main__":
    # Init timer
    subTimer = startTimerLog("Parcelle Grand Lyon subscript process")

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
