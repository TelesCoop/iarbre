# IArbre backend

## Overview
Backend to compute plantability indice for Metropole de Lyon.
This backend is using [Django](https://www.djangoproject.com/)
and a [PostGIS](https://postgis.net/) database.


Developed by [Telescoop](https://telescoop.fr), after the [V1](https://forge.grandlyon.com/erasme/script-recalcul-calque)
from [Exo-dev](https://exo-dev.fr/).

To find more details about the project IA.bre, please go to https://iarbre.fr.

## Contents
- [Data required](#data-required)
- [Installation](#installation)
- [Populate the DB](#populate-the-db)
- [Help](#help)

## Data required

You need a folder named `file_data` that contains some of the data at the root of the project.
Please send email to [contact@telescoop.fr](mailto:contact@telescoop.fr) to get it.


## Installation
> These steps are for Linux. It has not been tested on Windows or macOS.

Requires [GDAL](https://gdal.org/en/stable/) and [PostGIS](https://postgis.net/).

On Linux, follow instructions from Django:
https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/postgis/
and install required packages from source.

Alternatively, you can try installing packages using `apt`, but it might not be
enough:

- Gdal for geographic queries: `sudo apt install binutils libproj-dev gdal-bin psycopg2`
- `sudo apt install postgresql-x postgresql-x-postgis-3 postgresql-server-dev-x python3-psycopg3`
(x matching the PostgreSQL version you want to install).

### Initiate the database
After the installation you need to create the DB using PostGIS:
```bash
$ createdb  <db name>
$ psql <db name>
> CREATE EXTENSION postgis;
```
Then create a user:
```bash
postgres# CREATE USER geodjango PASSWORD 'my_passwd';
```
You need then to create a file named `local_settings.ini` with:
```commandline
[database]
engine=postgresql
user=geodjango
name=<db name>
password=my_passwd
```

### Install required packages
We recommend you to set up a Python virtual environment with [`pew`](https://github.com/pew-org/pew).
```bash
$ pip install pew
$ cd  <path>
$ pew mkproject <project_name>
```
This would create a new virtual environment and an associated project directory in `<path>`.
Then clone the repo in the created directory and install required packages in the virtual
environment.
```bash
$ git clone https://github.com/TelesCoop/iarbre-back.git
$ pip install -r requirements.txt
```
Next time you want to work on this project, use:
```bash
$ pew workon <project_name>
```
It will activate you environment and the shell is automatically moved to the directory.
## Populate the database

### Import DATA to the PostGIS database
Now we will use the land occupancy data in `file_data` to compute the plantability scores.
Run the following management commands:

```bash
$ python manage.py migrate
$ python manage.py c01_insert_cities
$ python manage.py c02_init_grid
$ python manage.py c03_import_data
$ python manage.py c04_compute_factors
$ python manage.py c05_compute_indice
$ python manage.py generate_mvt_files
```
You can find details on the land occupancy data used and their processing in [data_config.py](./iarbre_data/data_config.py).

Last [command](./api/management/commands/generate_mvt_files.py) `python manage.py generate_mvt_files` generates Mapbox Vector Tiles
([MVT](https://gdal.org/en/stable/drivers/vector/mvt.html)) for different zoom levels.
These tiles could then be retrieved using the [api](./api/views.py) by the frontend and displayed using [MapLibre](https://maplibre.org/).
## Run server
```bash
$ python manage.py runserver --nostatic
```
Now the backend is running and the API is ready to be used by the frontend.
## Help
🆘
If you encounter any issues while using this code or need some improvements, feel free to post a new issue
on the [issues webpage](https://github.com/TelesCoop/iarbre-back/issues).
We will get back to you promptly, as we are keen on continuously improving it. 🚀
