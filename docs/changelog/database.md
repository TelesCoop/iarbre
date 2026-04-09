# Historique des Sauvegardes de Base de Données

Ce document suit toutes les sauvegardes de base de données et les changements inclus dans chaque version.

---

## Sauvegardes

## 2026-04-09T13:15_postgres_backup.dump

**Changements :** :

- Simplification des des MVTs de l'intégrité fonctionnel de la biosphère pour les niveaux de zooms éloignés. Nettoyage des `BiosphereFunctionalIntegrityLandCover` en base pour permettre de les suivre ensuite.
- Les QPVs avaient disparus de la DB suite à un changement sur data.grandlyon et sont rajoutés dans cette version.

### 2026-04-07T12:12_postgres_backup.dump

**Changements :**

- **Indice de biosphère fonctionnel** : Ajout des MVTs de l'intégrité fonctionnel de la biosphère ainsi que des données correspondantes dans la DB : `BiosphereFunctionalIntegrity`. Dans la DB se trouvent aussi les données d'occupation des sols : `BiosphereFunctionalIntegrityLandCover`.

### 2026-03-31T11:55_postgres_backup.dump

**Changements :**

- **Raster vegestrate** : Ajout dans `media/rasters/vegestrate` d'une collection de rasters de l'inventaire du végétal correspondant à différentes post-process.

```python
VEGESTRATE_FILES = {
    (2018, "02", False, None): "raw_fullmetropole_ir_02_2018.tif", # Résolution 0.2m
    (2018, "02", True, 3): "postprocessv3_fullmetropole_ir_02_2018.tif",
    (2023, "02", False, None): "raw_lyon_metropole_ir_02_2023.tif",
    (2023, "02", True, 1): "postprocessv1_fullmetropole_RGB_02_2023.tif",
    (2023, "02", True, 2): "postprocessv2_fullmetropole_ir_02_2023.tif",
    (2023, "02", True, 3): "postprocessv3_fullmetropole_ir_02_2023.tif",
}
```

### 2026-03-03T15:35_postgres_backup.dump

**Changements :**

- **Tuiles vegestrate** : Update des tuiles vegestrate pour utiliser la version 2 des données qui utilise le canal IR et un meilleur post-processing : https://github.com/TelesCoop/vegestrate/releases/tag/v2.0-metropole-lyon-ir-2023

### 2026-03-03T12:06_postgres_backup.dump

**Changements :**

- **Tuiles vegestrate** : Ajouts des tuiles vegestrates à la place du raster pour permettre l'interaction.

### 2026-02-11T19:03_postgres_backup.dump

**Changements :**

- **Tuiles de plantabilité** : L'indice croisé plantabilité et vulnérabilité à la chaleur est maintenant en dur dans les tuiles MVTs pour alléger l'affichage du front et permettre les fonctions de filtrage.

### 2026-02-11T07:47_postgres_backup.dump

**Changements :**

- **Inventaire stratifié du végétal** : Ajout dans les `media` du raster de l'inventaire du végétal stratifié pour la toute la métropole de Lyon mise à jour. Version du code utilisée : https://github.com/TelesCoop/vegestrate/releases/tag/v1.0-metropole-lyon-2023

### 2026-01-12T20:03_postgres_backup.dump (3.4 GiB)

**Changements :**

- **Inventaire stratifié du végétal** : Ajout dans les `media` du raster de l'inventaire du végétal stratifié pour la toute la métropole de Lyon.

### 2025-12-09T14:16_postgres_backup.dump

**Changements :**

- **Inventaire stratifié du végétal** : Ajout dans les `media` du raster de l'inventaire du végétal stratifié pour la ville de Villeurbanne.

### 2025-11-24T08:29_postgres_backup.dump

**Changements :**

- **Données Land Use** : Recalcule des facteurs qui étaient mal insérés dans les champs `details` et `meta_factors` du modèle `Tile`.

### 2025-10-29T08:19_postgres_backup.dump

**Changements :**

- **Données IPAVE** : Ajoute les données de IPAVE pour une expérimenation sur une branch.

### 2025-10-22T15:02_postgres_backup.dump

**Changements :**

- **Compte de plantabilité par échellon** : Corrige pour mettre le bon type.

### 2025-10-22T13:06_postgres_backup.dump

**Changements :**

- **Compte de plantabilité par échellon** : Ajout des plantabilités par `City` et `Iris`.
- **Plantabilité** : Les tuiles MVT et le modèle Tile incluent l'information de vulnérabilité à la chaleur sur la zone (croisement par projection au maillage de la plantabilité).

### 2025-10-17T13:06_postgres_backup.dump

**Changements :**

- **Fichier de Référence** - Base de données complète avec toutes les 30 migrations (0001-0030)
- **Modèles Principaux :** City, Data, Tile, TileFactor
- **Géométrie :** Support de double projection (SRID 2154 et 3857 pour la cartographie web)
- **Plantabilité :** Indices de plantabilité avec valeurs brutes et normalisées
- **Tuiles MVT :** Mapbox Vector Tiles pour un rendu cartographique efficace
- **Subdivisions Géographiques :** Modèle IRIS (zones statistiques françaises)
- **Relations :** Hiérarchie complète City-Tile-IRIS
- **Suivi des Villes :** Drapeaux booléens tiles_generated et tiles_computed
- **Zones Climatiques :** LCZ (Local Climate Zones) avec données de classification climatique
- **Évaluation de Vulnérabilité :** Indices de vulnérabilité jour/nuit (vulnérabilité, exposition, capaf, sensibilité)
- **Données Flexibles :** Champs JSON details sur les modèles Lcz, Tile et Vulnerability
- **Métadonnées :** JSONField meta_factors sur Tile pour métadonnées extensibles
- **Cadastre :** Registre parcellaire avec parcel_id et relations avec les villes
- **Points d'Intérêt :** Emplacements ponctuels liés aux villes
- **Types de Données :** MVTTile supporte lcz, plantability, vulnerability, cadastre
- **Niveaux Géographiques :** MVTTile supporte les niveaux tile, city, iris, lcz, cadastre
- **Clés Étrangères :** Tile vulnerability_idx avec comportement de cascade SET_NULL

---

## Modèle pour Nouvelles Sauvegardes

Copiez ce modèle lors de l'ajout d'une nouvelle sauvegarde :

````

### YYYY-MM-DDTHH:MM_postgres_backup.dump

## **Changements :**

-
- ***

```

**Remarque :** Les sauvegardes sont listées par ordre chronologique inversé (la plus récente en premier)
```
````
