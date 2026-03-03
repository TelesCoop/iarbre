# Backend IArbre ![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ludovicdmt/86d9b33a236f4e03bca8799858fc7f6d/raw/coverage-badge.json)

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
- [Pipeline de plantabilité](#pipeline-de-plantabilite)
- [Génération de la base de données](#generation-de-la-base-de-donnees)
- [Gestion des sauvegardes de base de données](#gestion-des-sauvegardes-de-base-de-donnees)
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

## Pipeline de plantabilité

Le pipeline orchestre l'ensemble des étapes de calcul du calque de plantabilité, de l'ingestion des données brutes jusqu'aux statistiques par ville et IRIS. Il est défini dans [`pipeline/plantability_pipeline.yaml`](pipeline/plantability_pipeline.yaml) et piloté par une commande Django dédiée.

### Lancer le pipeline

> **Rappel** — assurez-vous que les données nécessaires sont bien présentes dans `file_data` avant de lancer le pipeline. Si vous n'avez pas ces données, veuillez envoyer un e-mail à [contact@telescoop.fr](mailto:contact@telescoop.fr).

```bash
python manage.py migrate
python manage.py run_pipeline
```

### Options

```bash
python manage.py run_pipeline --dry-run   # aperçu des étapes sans exécution
python manage.py run_pipeline --reset     # repart de zéro en ignorant l'état existant
python manage.py run_pipeline --config pipeline/plantability_pipeline.yaml  # config explicite
python manage.py run_pipeline --state /chemin/vers/state.json               # fichier d'état explicite
```

### Reprise après échec

À chaque étape, le runner sauvegarde un fichier d'état JSON dans `output/pipeline_calque_de_plantabilite_state.json`. En cas d'échec, il suffit de relancer exactement la même commande : les étapes déjà terminées (`"status": "completed"`) sont automatiquement ignorées et le pipeline reprend à partir de l'étape échouée.

```bash
python manage.py run_pipeline   # reprend depuis la dernière étape échouée
```

### Étapes du pipeline

| Ordre | Étape                                     | Commande Django               |
| ----- | ----------------------------------------- | ----------------------------- |
| 1     | Insertion des villes et IRIS              | `c01_insert_cities_and_iris`  |
| 2     | Import des données d'occupation des sols  | `c03_import_data`             |
| 3     | Mise à jour des données OCS               | `update_data`                 |
| 4     | Conversion en rasters (5 m)               | `data_to_raster`              |
| 5     | Extraction top-5 d'usage du sol par tuile | `raster_to_land_use`          |
| 6     | Calcul du raster de plantabilité          | `compute_plantability_raster` |
| 7     | Vectorisation du raster en tuiles PostGIS | `raster_plantability_to_geom` |
| 8     | Calcul des comptages par ville et IRIS    | `compute_plantability_counts` |

Le graphe de dépendances complet et les descriptions détaillées de chaque étape sont dans [`pipeline/plantability_pipeline.yaml`](pipeline/plantability_pipeline.yaml).

## Génération de la base de données

> Les commandes ci-dessous correspondent aux étapes individuelles du pipeline. Pour une exécution complète, préférez utiliser `python manage.py run_pipeline` décrit dans la section précédente.

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

## Gestion des sauvegardes de base de données

### Sauvegarde de la base de données

Pour créer une sauvegarde de la base de données et des fichiers media sur S3 :

```bash
python manage.py backup_db backup_db_and_media --zipped
```

Cette commande utilise `telescoop_backup` pour créer une sauvegarde compressée avec un timestamp (format : `YYYY-MM-DDTHH:MM_postgres_backup.dump`).

### Restauration de la base de données

#### Restaurer une version spécifique

Pour restaurer une version spécifique de la base de données, créez ou modifiez le fichier `back/.db_recover_target` avec le nom de la sauvegarde :

```bash
echo "2025-10-21T13:12_postgres_backup.dump" > back/.db_recover_target
cd back && python manage.py backup_db recover_db_and_media
```

#### Restaurer la dernière version

Si le fichier `.db_recover_target` n'existe pas, la commande restaurera automatiquement la dernière sauvegarde disponible :

```bash
make back_recover_db_and_media
```

Vous pouvez également ignorer le fichier `.db_recover_target` (s'il existe) et forcer l'utilisation de la dernière sauvegarde :

```bash
make back_recover_db_and_media USE_FILE=no
```

### Liste des sauvegardes disponibles

Pour voir toutes les sauvegardes disponibles sur S3 :

```bash
make back_backup_list
```

### Historique des sauvegardes

Consultez le fichier [database_changelog.md](https://github.com/TelesCoop/iarbre/blob/dev/docs/changelog/database_changelog.md) pour voir l'historique détaillé de toutes les sauvegardes et leurs changements.

### Déploiement

Lors du déploiement avec Ansible, le système :

- Vérifie si `back/.db_recover_target` existe
- Si oui : restaure la version spécifiée dans le fichier
- Si non : restaure la dernière sauvegarde disponible

Cela permet de contrôler précisément quelle version de la base de données est déployée en production.

## Démarrage du service backend

```bash
python manage.py runserver --nostatic
```

Le backend est maintenant en cours d'exécution, et l'API est prête pour le frontend.

## Générer le code coverage

```bash
coverage run manage.py test && coverage report
```

Cette commande va exécuter tous les tests et générer un report pour mesurer si toutes les lignes sont testées. Si il n'existe aucun test pour un script, ce script ne sera pas inclus dans le report.

## Aide

🆘 Si vous rencontrez des problèmes ou avez des suggestions d'amélioration, veuillez ouvrir un nouvel issue sur notre [page GitHub Issues](https://github.com/TelesCoop/iarbre/issues).
