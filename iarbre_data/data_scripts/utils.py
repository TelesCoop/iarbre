# Import
import os
from os.path import exists
import re
import sys
import unicodedata
from math import *
from datetime import datetime
from io import StringIO
from fiona import BytesCollection  
import logging
import platform

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import geopandas as gp
import pandas as pd
import numpy as np
import requests
import shapely
from shapely.geometry import Polygon, MultiPolygon

if not platform.system() != "Linux":
    import resource


# -----------------------------------------------------
# ----        Explicit Return code function        ----
# ---- Usefull for exiting code from openShift Job ----
# -----------------------------------------------------
def return_error_and_exit_job(Code=-1):
    sys.exit(Code)

# -------------
# ---- LOG ----
# -------------

def initLogging(logsPath):
    start_date = datetime.now()
    logFilePath = logsPath + 'log_' + start_date.strftime("%d-%m-%Y") + '.log'

    if os.path.isfile(logFilePath):
        os.remove(logFilePath)

    # Init instance of logger
    currLogger = logging.getLogger('main')
    currLogger.setLevel(logging.DEBUG)

    # Define logger and destination path
    fileHandler = logging.FileHandler(logFilePath, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
    formatter.datefmt = '%d/%m/%Y %H:%M:%S'
    fileHandler.setFormatter(formatter)

    #TODO: Add history and backup handler

    # Add handler
    currLogger.addHandler(fileHandler)

    # First log
    debugLog(style.YELLOW, "Logger is initialized", logging.INFO, onlyFile=True)

def debugLog(color, message, level=logging.INFO, onlyFile=False):
    currLogger = logging.getLogger('main')
    # Log in file
    if level == logging.INFO:
        currLogger.info(message)
    elif level == logging.WARN:
        currLogger.warning(message)
    elif level == logging.ERROR:
        currLogger.error(message)
    elif level == logging.CRITICAL:
        currLogger.critical(message)
    else:
        currLogger.info(message)
    
    if not onlyFile:
        # Print in console
        print(color + message + '\n', style.RESET)

def startTimerLog(taskname):
    # Log time
    start_date = datetime.now()
    debugLog(style.MAGENTA, "Start task \'{}\' at {}".format(taskname, start_date.strftime("%d/%m/%Y, %H:%M:%S")), logging.INFO)

    # Create timer dict obj
    timer = {'taskname': taskname, 'start_date': start_date}

    return timer

def endTimerLog(timer):
    # Log time end
    end_date = datetime.now()
    time_elapsed = datetime.now() - timer["start_date"]

    # Split timedelta
    time_el_d = time_elapsed.days
    time_el_h = floor(time_elapsed.seconds / 3600)
    time_el_m = floor(time_elapsed.seconds / 60)
    time_el_s = time_elapsed.seconds - (time_el_m * 60)
    time_el_ms = time_elapsed.microseconds

    # Log
    debugLog(style.MAGENTA, "End task \'{}\' at {} in {} days {} hours {} min {} sec {} micros".format(timer["taskname"], end_date.strftime("%d/%m/%Y, %H:%M:%S"), time_el_d, time_el_h, time_el_m, time_el_s, time_el_ms), logging.INFO)

# ------------------------
# ---- ENV OPERATIONS ----
# ------------------------

def checkEnvFile():
    # Init all var in .env file
    file_exists = exists('.env')
    dbHost = os.getenv('DB_HOST')
    dbUser = os.getenv('DB_USER')
    dbPwd = os.getenv('DB_PWD')
    dbName = os.getenv('DB_NAME')
    dbSchema = os.getenv('DB_SCHEMA')
    targetProj = os.getenv('TARGET_PROJ')
    boolTempFile = os.getenv('REMOVE_TEMP_FILE')
    skipExistingData = os.getenv('SKIP_EXISTING_DATA')
    enableTruncate = os.getenv('ENABLE_TRUNCATE')
    sourceDataPath = os.getenv('SOURCE_DATA_PATH')

    # Check if file exists
    if file_exists == False:
        debugLog(style.RED, "The .env file is not found. Please create it based on .env.example", logging.ERROR)
        return_error_and_exit_job(-1)
    else:
        # Check all var in .env file
        if (dbHost == None or dbUser == None or dbPwd == None or dbName == None or dbSchema == None or targetProj == None or boolTempFile == None or skipExistingData == None or enableTruncate == None or sourceDataPath == None):
            debugLog(style.RED, "Please make sure you have correctly initialized the .env file", logging.ERROR)
            return_error_and_exit_job(-1)

# -------------------------
# ---- DATE OPERATIONS ----
# -------------------------

def getMinNowDate():
    # Get now date and format
    dt = datetime.now()
    dt = dt.strftime("%d-%m-%Y_%H-%M-%S")

    return dt

def dateConverter(o):
    # Date converter (for JSON serialization)
    if isinstance(o, datetime):
        return o.__str__()

# -------------------------
# ---- TEXT OPERATIONS ----
# -------------------------

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def text_to_id(text):
    """
    Convert input text to id.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-]', '', text)
    return text

# -------------------------
# ---- DATA OPERATIONS ----
# -------------------------

def connectDB(params_DB, jsonEnable = False, setSearchpath = True):
    try:
        conn = psycopg2.connect(**params_DB)
        cur = None
        if jsonEnable:
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()
        
        # # Set Schema 'base'
        # if setSearchpath:
        #     cur.execute(f'SET search_path TO '+ params_DB['schema'])

        return conn, cur

    except (Exception, psycopg2.Error) as error :
        debugLog(style.RED, "Error while trying to connect in PostgreSQL database : {}".format(error), logging.ERROR)

def closeDB(conn, cur):
    try:
        # Commit (save change)
        conn.commit()

        # Close DB connection
        cur.close()

    except (Exception, psycopg2.Error) as error :
        debugLog(style.RED, "Error while trying to connect in PostgreSQL database : {}".format(error), logging.ERROR)

def getCountfromDB(DB_params, DB_schema, tableName, queryFilter=None, connInput = None, curInput = None):
    conn = None
    cur = None
    if connInput is None and curInput is None:
        # Connect DB
        conn, cur = connectDB(DB_params)
    else:
        conn = connInput
        cur = curInput
    
    # Build request
    countQuery = "SELECT COUNT(1) FROM " + DB_schema + "." + tableName

    if queryFilter:
        countQuery = countQuery + " WHERE " + queryFilter
    
    # Execute query
    cur.execute(countQuery)
    countValue = cur.fetchone()[0]

    if connInput is None and curInput is None:
        # Final close cursor & DB
        closeDB(conn, cur)

    return countValue

def getDatafromDB(DB_params, sqlQuery, connInput = None, curInput = None):
    conn = None
    cur = None
    if connInput is None and curInput is None:
        # Connect DB
        conn, cur = connectDB(DB_params, jsonEnable=True)
    else:
        conn = connInput
        cur = curInput
    
    # Get all Data
    cur.execute(sqlQuery)
    dataValues = json.dumps(cur.fetchall(), indent=2, default=dateConverter)

    if connInput is None and curInput is None:
        # Final close cursor & DB
        closeDB(conn, cur)

    return dataValues

def insertDataInDB(DBcursor, sqlQuery):
    # Insert Data
    try:
        DBcursor.execute(sqlQuery)
    except psycopg2.Error as e:
        print(e)
        raise
    return DBcursor

def updateDataInDB(DBcursor, sqlQuery):
    # Update Data
    DBcursor.execute(sqlQuery)
    return DBcursor

def deleteDataInDB(DB_params, DB_schema, tableName, queryFilter=None):
    # Connect DB
    conn, cur = connectDB(DB_params)
    
    # Build request
    deleteQuery = "DELETE FROM " + DB_schema + "." + tableName

    if queryFilter:
        deleteQuery = deleteQuery + " WHERE " + queryFilter
    
    # Execute query
    cur.execute(deleteQuery)

    # Execute COMMIT
    commmitQuery = "COMMIT;"
    cur.execute(commmitQuery)

    # Final close cursor & DB
    closeDB(conn, cur)

    return

def truncateDataInDB(DB_params, DB_schema, tableName):
    # Connect DB
    conn, cur = connectDB(DB_params)
    
    # Build request
    truncateQuery = "TRUNCATE TABLE " + DB_schema + "." + tableName + " CASCADE"

    # Execute query
    cur.execute(truncateQuery)

    # Final close cursor & DB
    closeDB(conn, cur)

    return

def deleteCustomDataInDB(DB_params, sqlQuery):
    conn = None
    cur = None

    # Connect DB
    conn, cur = connectDB(DB_params, jsonEnable=True)
    
    # Get all Data
    cur.execute(sqlQuery)

    # Final close cursor & DB
    closeDB(conn, cur)

    return

def getGDFfromDB(DB_params, sqlQuery, projection):
    # Connect DB
    conn, cur = connectDB(DB_params)

    # Get data (schema in sqlQuery)
    df = gp.read_postgis(sqlQuery, conn, crs=projection) 

    # Get length
    lenDF = len(df)

    # Log
    debugLog(style.GREEN, "Datas was loaded successfully (with {} entites) \n".format(lenDF), logging.INFO)

    # Final close cursor & DB
    closeDB(conn, cur)

    return df

def insertGDFintoDB(DB_params, DB_schema, gdf, tablename, columnsListToDB):
    # Start Insert Timer
    insertTimer = startTimerLog('Inserting GDF data')

    # Connect DB
    conn, cur = connectDB(DB_params,jsonEnable=False, setSearchpath=False)

    # Save dataframe to an in memory buffer
    buffer = StringIO()
    gdf.to_csv(buffer, sep=';', index_label='id', header=False, index=False)
    buffer.seek(0)

    # Insert with copy_from
    try:
        cur.copy_from(buffer, tablename, sep=";", columns=columnsListToDB)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        debugLog(style.RED, "Error while inserting : {}".format(error), logging.ERROR)
        # Rollback and close
        conn.rollback()
        cur.close()
        return 1
    
    # Final close cursor & DB
    closeDB(conn, cur)

    # End Insert Timer
    endTimerLog(insertTimer)

def splitList(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
            for i in range(wanted_parts) ]

# -------------------------
# ---- GEOM OPERATIONS ----
# -------------------------

def wfs2gp_df(layer_name, url, bbox=None, wfs_version="2.0.0", outputFormat='GML3', reprojMetro=False, targetProj=None, req_timeout=600, proxies=None):
    # Concat params
    params = dict(service='WFS', version=wfs_version,request='GetFeature', typeName=layer_name, outputFormat=outputFormat, crs=targetProj)
    # Load data in Bytes
    with BytesCollection(requests.get(url,params=params, timeout=req_timeout, proxies=proxies).content) as f:
        # Make GDF
        df = gp.GeoDataFrame.from_features(f)
    
    # Log
    lenDF = len(df)
    debugLog(style.GREEN, "API datas loaded successfully (with {} entites) \n".format(lenDF), logging.INFO)

    # Reproj
    if reprojMetro:
        df = df.set_crs("EPSG:4326")
    if targetProj:
        df = checkAndReproj(df, targetProj)

    return df

def checkAndReproj(df, targetProj):
    # Get actual DF proj
    currentProj = df.crs
    debugLog(style.YELLOW, "Current projection of dataframe : {}".format(currentProj), logging.INFO)
    
    if currentProj != targetProj:
        # Reproj to targeted proj
        df = df.to_crs(targetProj)

        # Log
        newProj = df.crs
        debugLog(style.GREEN, "Successful reproj to : {}".format(newProj), logging.INFO)
    else:
        debugLog(style.GREEN, "No need to reproj this dataframe", logging.INFO)

    return df

def convertGeomToWKT(df):
    #TODO!: Check actual format ?
    # print(type(df.geometry))

    # Convert geom to WKT
    df = df.to_wkt()
    debugLog(style.GREEN, "Successful convert dataframe geom into WKT format", logging.INFO)
    
    return df

def createGridFromDF(df, gridTileSize: int):
    """
    Generate grid based on initial dataframe bbox
    Arguments:
        df: <dataframe> initial DF
        gridTileSize: <integer> wished size for tiles
    Returns:
        The GeoDataFrame of the grid merged with initial DF
    """

    # Start Grid Timer
    gridTimer = startTimerLog('Generate Grid with size ' + str(gridTileSize) + "x" + str(gridTileSize))
    
    # Instanciate Geodataframe
    gdf = gp.GeoDataFrame(df, crs=df.crs)

    # Calculate bounds from initial geom DF
    gdf.total_bounds

    # Get total area for the grid
    xmin, ymin, xmax, ymax= gdf.total_bounds

    # Define cell size
    cell_size = gridTileSize

    # Define Projection of the grid
    crs = "epsg:2154"

    # Create the cells in a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax + cell_size, cell_size):
        for y0 in np.arange(ymin, ymax+cell_size, cell_size):
            # Bounds
            x1 = x0-cell_size
            y1 = y0+cell_size
            grid_cells.append( shapely.geometry.box(x0, y0, x1, y1)  )
    
    # Compile result in Geodataframe
    gridGDF = gp.GeoDataFrame(grid_cells, columns=['geometry'], crs=crs)

    # Log grid length
    debugLog(style.BLUE, "Grid generated with : {} tiles".format(len(gridGDF)), logging.INFO)

    # End Grid Timer
    endTimerLog(gridTimer)

    # Log Merge time
    mergeTimer = startTimerLog('Merge grid with geom')

    # Keep only revellant cell - Merge with communes gdf
    #TODO!: overlap (intersect) to optimize ?
    mergedGDF = gridGDF.sjoin(gdf, how='inner', predicate='intersects')

    # Clean other column
    mergedGDF = mergedGDF.drop(columns=['index_right'])
    
    # Log merged length
    debugLog(style.BLUE, "Merged Grid generated with : {} tiles as result".format(len(mergedGDF)), logging.INFO)

    # End Merge time
    endTimerLog(mergeTimer)

    return mergedGDF

def checkAndDeleteEmptyGeomFromGDF(df):
    # Log
    debugLog(style.YELLOW, "Analyze and delete lines with empty geom in current GeoDataFrame", logging.INFO)

    # Origin length
    orgGDFLength = len(df)

    # Get geometry from GDF
    geomSerie = df.loc[:,'geometry']

    # Check empty geom and remove concerned line
    geomSerieEmpty = geomSerie.is_empty

    # Invert value to make filter (True = keep)
    arrEmptyInv = []
    for index, row in geomSerieEmpty.items():
        arrEmptyInv.append(not row)

    # Make geoSerie
    geomSerieEmptyInv = pd.Series(arrEmptyInv)

    # Filter GDF lines based in empty value
    df = df.loc[geomSerieEmptyInv]

    # Final length
    finGDFLength = len(df)

    # Result length
    resLength = orgGDFLength - finGDFLength

    # Finally log + return
    debugLog(style.GREEN, "{} empty geom(s) was deleted".format(str(resLength)), logging.INFO)
    
    return df

def checkAndRepairGeomFromGDF(df):
    # Log
    debugLog(style.YELLOW, "Analyze and repair geom(s) in current GeoDataFrame", logging.INFO)

    # Get geometry from GDF
    geomSerie = df.loc[:,'geometry']
    
    # Check valid geom from geoSerie
    geomSerieWrong = geomSerie.is_valid
    
    # Invert value to make filter (True = need to repair)
    arrEmptyInv = []
    for index, row in geomSerieWrong.items():
        arrEmptyInv.append(not row)

    # Make GeoSerie
    geomSerieWrongInv = pd.Series(arrEmptyInv)

    # Filter GDF lines based in wrong value
    currentGDFWrong = df.loc[geomSerieWrongInv]

    # Get Length
    lengthWrongGeom = len(currentGDFWrong)

    if lengthWrongGeom:
        # Init var
        multiExist = False
        
        # Check if one of geom is MULTI
        allGeomType = currentGDFWrong.geom_type
        for geomT in allGeomType:
            if geomT == 'MultiPolygon' or geomT == 'MultiLineString':
                multiExist = True

        # Explode if multi geom
        if multiExist:
            currentGDFWrong = currentGDFWrong.explode(index_parts=False)

        # Repair each geom and insert in initial GDF
        for index, row in currentGDFWrong.iterrows():
            # Get only geom
            currWrongGeom = row['geometry']
            # Repair with buffer 0
            repairGeom = currWrongGeom.buffer(0.01)
            # Set repaired geom into GDF
            df.loc[[index], 'geometry'] = repairGeom

    # Finally log + return
    debugLog(style.GREEN, "{} geom(s) was repaired".format(str(lengthWrongGeom)), logging.INFO)
    
    return df

def makeBufferFromGDF(df, bufferSize):
    # Make buffer on all geometry in GDF
    df = df.buffer(bufferSize)

    return df

def flattenGeom(GDFgeometry):
    '''
    Takes a GeoSeries of 3D Multi/Polygons (has_z) and returns a list of 2D Multi/Polygons
    '''
    new_geo = []
    for p in GDFgeometry:
        if p.has_z:
            if p.geom_type == 'Polygon':
                lines = [xy[:2] for xy in list(p.exterior.coords)]
                new_p = Polygon(lines)
                new_geo.append(new_p)
            elif p.geom_type == 'MultiPolygon':
                new_multi_p = []
                for ap in p:
                    lines = [xy[:2] for xy in list(ap.exterior.coords)]
                    new_p = Polygon(lines)
                    new_multi_p.append(new_p)
                new_geo.append(MultiPolygon(new_multi_p))
    return new_geo

# --------------------------
# ---- FILES OPERATIONS ----
# --------------------------

def createGDFfromGeoJSON(filePath):
    try:
        # Read
        currentGDF = gp.read_file(filePath)
        # Count
        lenDF = len(currentGDF)
        # Log
        debugLog(style.GREEN, "GeoJSON file \'{}\' loaded successfully (with {} entites)".format(filePath, lenDF), logging.INFO)
        # Return
        return currentGDF
    except(Exception) as error:
        debugLog(style.RED, "Error while trying to open file : {}".format(error), logging.INFO)
        return None

def checkAndCreateDirectory(dirPath):
    # Check if directory exist then create if not
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)
        debugLog(style.YELLOW, "The directory {} was created".format(dirPath))

# ----------------
# ---- MEMORY ----
# ----------------

def memory_limit(percentage: float):
    if platform.system() != "Linux":
        debugLog(style.RED, 'Memory limitation only works on linux !', logging.ERROR)
        return
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (get_memory() * 1024 * percentage, hard))

def get_memory():
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
    return free_memory

def memory(percentage=0.8):
    def decorator(function):
        def wrapper(*args, **kwargs):
            memory_limit(percentage)
            try:
                return function(*args, **kwargs)
            except MemoryError:
                mem = get_memory() / 1024 /1024
                debugLog(style.YELLOW, 'Remain: %.2f GB'.format(mem), logging.INFO)
                sys.stderr.write('\n\nERROR: Memory Exception\n')
                sys.exit(1)
        return wrapper
    return decorator

# ---------------------
# ---- COLOR STYLE ----
# ---------------------

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


# -----------------------------
# ---- PROGRESS OPERATIONS ----
# -----------------------------
def setProgress(DBcursor, DBSchema, codeInsee, id_factor=None):
    stage = 'tiles'
    qryFilter = ''
    insertComplement = ''
    if id_factor:
        stage = 'factors'
        qryFilter = ' and id_factor = {}'.format(id_factor)
        insertComplement = ', {}'.format(id_factor)
    # Ensure there is only one occurence for the township
    DBcursor.execute('DELETE FROM ' + DBSchema + '.' + stage + '_progress WHERE insee = ' + str(codeInsee) + qryFilter)
    insertDataInDB(DBcursor,'INSERT INTO ' + DBSchema + '.' + stage + '_progress VALUES (' + str(codeInsee) + insertComplement + ')')

def getProgress(DBcursor, DBSchema, codeInsee, id_factor=None):
    stage = 'tiles'
    qryFilter = ''
    if id_factor:
        stage = 'factors'
        qryFilter = ' and id_factor = {}'.format(id_factor)

    qry = 'SELECT count(*) FROM '+ DBSchema + '.'  + stage + '_progress WHERE insee = ' + str(codeInsee) + qryFilter
    debugLog(style.YELLOW, qry, logging.INFO)
    DBcursor.execute(qry)   
    dataValues = DBcursor.fetchone()

    if dataValues is None:
        return 0  
    try:
        ret = dataValues['count']
    except:
        return 0
    
    return dataValues['count'] 

def resetProgress(DB_params, DB_schema):
    debugLog(style.WHITE, "Deleting process tables...", logging.INFO)
    truncateDataInDB(DB_params, DB_schema, 'tiles_progress')
    truncateDataInDB(DB_params, DB_schema, 'factors_progress')
    debugLog(style.GREEN, "Done.", logging.INFO)

def resetDataInDb(DB_params, DB_schema):
    debugLog(style.WHITE, "Deleting datas table...", logging.INFO)
    truncateDataInDB(DB_params, DB_schema, 'datas')
    debugLog(style.GREEN, "Done.", logging.INFO)

    debugLog(style.WHITE, "Deleting tiles_factors table...", logging.INFO)
    truncateDataInDB(DB_params, DB_schema, 'tiles_factors')
    debugLog(style.GREEN, "Done.", logging.INFO)

    debugLog(style.WHITE, "Deleting tiles table...", logging.INFO)
    truncateDataInDB(DB_params, DB_schema, 'tiles')
    debugLog(style.GREEN, "Done.", logging.INFO)

    