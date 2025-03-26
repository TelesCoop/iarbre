# Backend IArbre

## Aperçu

Le backend d'IArbre calcule l'occupation des sols et les différents indices (plantabilité, etc.).
Le backend utilise [Django](https://www.djangoproject.com/) et une base de données [PostGIS](https://postgis.net/).

Il existe trois applications Django :

- `iarbre_data` pour les calculs d’occupation des sols ;
- `plantability` pour le calcul de l'indice de plantabilité. Le développement correspond à une réplication de [l'implémentation V1](https://forge.grandlyon.com/erasme/script-recalcul-calque) réalisée par [Exo-dev](https://exo-dev.fr/).
- `api` pour rendre accessible ces résultats par à une API rest ;

## Contenu

- [Données requises](#donnees-requises)
- [Déploiement avec Ansible](#deploiement-avec-ansible)
- [Installation manuelle](#installation-manuelle)
- [Génération de la base de données](#generation-de-la-base-de-donnees)
- [Démarrage du backend](#demarrage-du-service-backend)
- [Aide](#aide)

## Données requises

Un dossier nommé `file_data` contenant les données nécessaires doit être présent à la racine du projet.
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

Utilisation des données d'occupation des sols dans `file_data` et calcul de l'indice de plantabilité :

```bash
python manage.py migrate
python manage.py c01_insert_cities_and_iris
python manage.py c02_init_grid
python manage.py c03_import_data
python manage.py c04_compute_factors
python manage.py c01_compute_plantability_indice
python manage.py generate_mvt_files
```

Pour plus de détails sur les données d'occupation des sols et leur traitement, consultez [data_config.py](https://github.com/TelesCoop/iarbre/blob/main/back/iarbre_data/data_config.py).

La dernière commande, [`generate_mvt_files`](https://github.com/TelesCoop/iarbre/blob/main/back/api/management/commands/generate_mvt_files.py),
génère des tuiles vectorielles Mapbox ([MVT](https://gdal.org/en/stable/drivers/vector/mvt.html)) pour différents niveaux de zoom.
Ces tuiles sont accessibles via l'[API](https://github.com/TelesCoop/iarbre/blob/main/back/api/views.py) et peuvent être
affichées avec [MapLibre](https://maplibre.org/).

## Démarrage du service backend

```bash
python manage.py runserver --nostatic
```

Le backend est maintenant en cours d'exécution, et l'API est prête pour le frontend.

## Aide

🆘 Si vous rencontrez des problèmes ou avez des suggestions d'amélioration, veuillez ouvrir un nouvel issue sur notre [page GitHub Issues](https://github.com/TelesCoop/iarbre/issues).
