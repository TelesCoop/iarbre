# IArbre Backend

## Overview

The backend of IArbre calculates the plantability index for Métropole de Lyon. Built with [Django](https://www.djangoproject.com/) and powered by a [PostGIS](https://postgis.net/) database, it forms the core of the project.

This backend was developed by [Telescoop](https://telescoop.fr), following the [V1 implementation](https://forge.grandlyon.com/erasme/script-recalcul-calque) by [Exo-dev](https://exo-dev.fr/).

For more details about the IA.bre project, visit [iarbre.fr](https://iarbre.fr).

## Contents

- [Required Data](#required-data)
- [Installation](#installation)
- [Populating the Database](#populating-the-database)
- [Running the Server](#running-the-server)
- [Help](#help)

## Required Data

A folder named `file_data` containing necessary data must be present at the root of the project.
To obtain this data, please email [contact@telescoop.fr](mailto:contact@telescoop.fr).

## Installation

> **Note**: These steps are designed for Linux. They have not been tested on Windows or macOS.

The backend requires [GDAL](https://gdal.org/en/stable/) and [PostGIS](https://postgis.net/).

Follow the [Django GIS installation guide](https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/postgis/) for Linux and install the necessary packages from source.

Alternatively, you can try installing the required packages using `apt`, though it may not always suffice:

```bash
sudo apt install postgresql-x postgresql-x-postgis-3 postgresql-server-dev-x python3-psycopg
sudo apt install binutils libproj-dev gdal-bin  # For geographic queries
```

_(Replace `x` with your desired PostgreSQL version.)_

### Initializing the Database

After installation, create a user and a new PostGIS-enabled database:

1. Log in as the `postgres` superuser:

   ```bash
   sudo -u postgres psql postgres
   ```

2. Create a new user and database:

   ```sql
   CREATE USER <user_name> WITH PASSWORD 'your_secure_password';
   ALTER USER <user_name> WITH SUPERUSER CREATEDB;
   CREATE DATABASE <db_name> OWNER <user_name>;
   \q
   ```

3. Connect with the new user and enable PostGIS:
   ```bash
   psql -U <user_name> <db_name>
   CREATE EXTENSION postgis;
   \q
   ```

### Installing Required Python Packages

We recommend using a Python virtual environment managed with [`pew`](https://github.com/pew-org/pew):

```bash
pip install pew
cd <path>
pew mkproject <project_name>
```

This creates a new virtual environment and an associated project directory in `<path>`.

Next, clone the repository and install the required packages:

```bash
git clone https://github.com/TelesCoop/iarbre-back.git
pip install -r requirements.txt
```

Create a `local_settings.ini` file with the following content:

```
[database]
engine=postgresql
user=<user_name>
name=<db_name>
password=your_secure_password
```

To work on the project in the future, activate the environment:

```bash
pew workon <project_name>
```

This activates the environment and navigates to the project directory.

## Populating the Database

### Importing Data to the PostGIS Database

Use the land occupancy data in `file_data` to calculate plantability scores by running these management commands:

```bash
python manage.py migrate
python manage.py c01_insert_cities
python manage.py c02_init_grid
python manage.py c03_import_data
python manage.py c04_compute_factors
python manage.py c05_compute_indice
python manage.py generate_mvt_files
```

For details on the land occupancy data and processing, see [data_config.py](https://github.com/TelesCoop/iarbre/blob/main/back/iarbre_data/data_config.py).

The final command, [`generate_mvt_files`](https://github.com/TelesCoop/iarbre/blob/main/back/api/management/commands/generate_mvt_files.py), generates Mapbox Vector Tiles ([MVT](https://gdal.org/en/stable/drivers/vector/mvt.html)) for various zoom levels. These tiles can be accessed via the [API](https://github.com/TelesCoop/iarbre/blob/main/back/api/views.py) and displayed with [MapLibre](https://maplibre.org/).

## Running the Server

Start the backend server:

```bash
python manage.py runserver --nostatic
```

The backend is now running, and the API is ready for the frontend.

## Help

🆘 If you encounter issues or have suggestions for improvement, please open a new issue on our [GitHub issues page](https://github.com/TelesCoop/iarbre/issues).

We are eager to assist and continuously enhance the project! 🚀
