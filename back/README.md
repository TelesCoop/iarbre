# Backend IArbre

![Coverage](https://img.shields.io/badge/coverage-78%25-yellowgreen)

## Aperçu

Le backend d'IArbre calcule l'occupation des sols et les différents indices (plantabilité, etc.).
Le backend utilise [Django](https://www.djangoproject.com/) et une base de données [PostGIS](https://postgis.net/).

Il existe trois applications Django :

- `iarbre_data` pour les calculs d’occupation des sols ;
- `plantability` pour le calcul de l'indice de plantabilité. Le développement correspond à une réplication de [l'implémentation V1](https://forge.grandlyon.com/erasme/script-recalcul-calque) réalisée par [Exo-dev](https://exo-dev.fr/);
- `api` pour la génération de tuiles MVT qui vont pouvoir être servis par l'API REST.

## Contenu

- [Données requises](#donnees-requises)
- [Déploiement avec Ansible](#deploiement-avec-ansible)
- [Installation manuelle](#installation-manuelle)
- [Génération de la base de données](#generation-de-la-base-de-donnees)
- [Démarrage du backend](#demarrage-du-service-backend)
- [Aide](#aide)

## Données requises

Un dossier nommé `file_data` contenant les données nécessaires qui ne sont pas sous license open-data (réseaux ENEDIS, GRDF, d'assainissement et d'eau potable, signalisation lumineuse et tricolore, etc) doit être présent à la racine du projet.
Pour obtenir ces données pour la Métropole de Lyon, veuillez envoyer un e-mail à [contact@telescoop.fr](mailto:contact@telescoop.fr).

## Déploiement avec Ansible

Consultez la documentation de [déploiement](https://docs.iarbre.fr/deploy/) pour plus de détails.

## Installation manuelle

### Ubuntu

Le backend nécessite [GDAL](https://gdal.org/en/stable/) et [PostGIS](https://postgis.net/).

Suivez le [guide d'installation Django GIS](https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/postgis/) pour Linux et installez les packages nécessaires depuis la source.

Vous pouvez également essayer d'installer les packages requis via `apt`, bien que cela puisse ne pas toujours suffire :

```bash
sudo apt install postgresql-x postgresql-x-postgis-3 postgresql-server-dev-x python3-psycopg2
sudo apt install binutils libproj-dev gdal-bin  # Pour les requêtes géographiques
```

### macOS

Pour macOS, vous pouvez utiliser [Homebrew](https://brew.sh/) pour installer les packages requis :

```bash
brew install postgresql postgis gdal
```

_(Remplacez `x` par la version de PostgreSQL souhaitée.)_

### Initialisation de la base de données

Après l'installation, créez un utilisateur et une nouvelle base de données PostGIS :

1. Connectez-vous en tant que super-utilisateur `postgres` :

   ```bash
   sudo -u postgres psql postgres
   ```

2. Créez un nouvel utilisateur et une base de données :

   ```sql
   CREATE USER <nom_utilisateur> WITH PASSWORD 'votre_mot_de_passe_sécurisé';
   ALTER USER <nom_utilisateur> WITH SUPERUSER CREATEDB;
   CREATE DATABASE <nom_base_de_données> OWNER <nom_utilisateur>;
   \q
   ```

3. Connectez-vous avec le nouvel utilisateur et activez PostGIS :
   ```bash
   psql -U <nom_utilisateur> <nom_base_de_données>
   CREATE EXTENSION postgis;
   \q
   ```

### Installation des packages Python requis

Nous recommandons d'utiliser un environnement virtuel Python géré par [`pew`](https://github.com/pew-org/pew) :

```bash
pip install pew
cd <chemin>
pew mkproject <nom_projet>
```

Cela crée un nouvel environnement virtuel et un répertoire de projet associé dans `<chemin>`.

Ensuite, clonez le dépôt et installez les packages requis :

```bash
git clone https://github.com/TelesCoop/iarbre-back.git
pip install -r requirements.txt
```

Créez un fichier `local_settings.ini`, à la racine du dossier `back`, avec le contenu suivant :

```
[database]
engine=postgresql
user=<nom_utilisateur>
name=<nom_base_de_données>
password=votre_mot_de_passe_sécurisé
```

Pour travailler sur le projet à l'avenir, activez l'environnement :

```bash
pew workon <nom_projet>
```

## Génération de la base de données

> **Rappel**
> Avant de lancer les commandes suivantes, assurez-vous que les données nécessaires sont bien présentes dans le dossier `file_data`. Si vous n'avez pas ces données, veuillez envoyer un e-mail à
> [contact@telescoop.fr](mailto:contact@telescoop.fr).

Pour calculer l'indice de plantabilité, il faut au préalables lancer ces deux commandes :

```bash
python manage.py migrate
python manage.py c01_insert_cities_and_iris
python manage.py c03_import_data
python manage.py update_data
```

Elles vont permettre de récupérer les données d'occupation des sols et le découpage des villes.
Pour plus de détails sur les données d'occupation des sols et leur traitement, consultez [data_config.py](https://github.com/TelesCoop/iarbre/blob/main/back/iarbre_data/data_config.py).

### Ajout des données de cadastre

La commande :

```bash
python manage.py import_cadastre
```

va permettre d'ajouter en base le cadastre, ce qui permettra plus tard de générer des MVT qui pourront être rajoutés en fond de carte.

### Génération des calques de LCZ et vulnérabilité à la chaleur

Les données de zones climatiques locales et de vulnérabilité à la chaleur ont été généré par ailleurs.
Les zones climatiques locales sont calculées par le CEREMA qui met les données à disposition sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/).

```bash
python manage.py import_lcz
```

Permet de télécharger les données relatives au zones climatiques locales de la métropole de Lyon et les ajouter dans la DB.

```bash
python manage.py import_vulnerability
```

Permet d'ajouter en DB les résultats de l'étude menée par la Métropole de Lyon à partir du GeoPackage fourni. Les données, sans le détail des sous-facteurs, sont disponibles en open-data sur [data.grandlyon](https://data.grandlyon.com/portail/fr/jeux-de-donnees/exposition-et-vulnerabilite-aux-fortes-chaleurs-dans-la-metropole-de-lyon/info).

### Genération du calque de plantabilité raster

A partir des données géographiques d'occupation des sols de `Data` :

1. Conversion des données de `Data` pour tous les facteurs en raster haute résolution (1x1m)
2. Convolution des rasters, individuellement, avec un noyau carré 5x5. Le raster en résultat contiennent le pourcentage de chaque facteur sur des tuiles carrés 5x5m.
3. Somme pondérée des rasters, avec les poids relatifs aux facteurs, pour produire un raster de plantabilité.
4. Vectorisation : ronversion des pixels du raster de plantabilié en géométries pour insérer dans notre base PostGIS. Des carrés 5x5m vont être créés. On utilise les valeurs des pixels dans le raster de plantabilité pour remplir le champ correspondant à la plantabilité et à la plantabilité seuillée.

> Le calcul est rapide, de l'ordre de 3h pour du 5x5m pour les 3 premières étapes. La dernière étape de vectorisation est la plus longue (~24h).

```bash
python manage.py data_to_raster
python manage.py compute_plantability_raster
python manage.py raster_plantability_to_geom
```

### Génération des tuiles MVT

[`generate_mvt_files`](https://github.com/TelesCoop/iarbre/blob/main/back/api/management/commands/generate_mvt_files.py),
génère des tuiles vectorielles Mapbox/MapLibre ([MVT](https://gdal.org/en/stable/drivers/vector/mvt.html)) pour différents niveaux de zoom.
Ces tuiles sont accessibles via l'[API](https://github.com/TelesCoop/iarbre/blob/main/back/api/views.py) et peuvent être
affichées avec [MapLibre](https://maplibre.org/).

```bash
python manage.py generate_mvt_files --geolevel tile --datatype plantability --number_of_threads 4
```

## Démarrage du service backend

```bash
python manage.py runserver --nostatic
```

Le backend est maintenant en cours d'exécution, et l'API est prête pour le frontend.

## Aide

🆘 Si vous rencontrez des problèmes ou avez des suggestions d'amélioration, veuillez ouvrir un nouvel issue sur notre [page GitHub Issues](https://github.com/TelesCoop/iarbre/issues).
