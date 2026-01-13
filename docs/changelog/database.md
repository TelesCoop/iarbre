# Historique des Sauvegardes de Base de Données

Ce document suit toutes les sauvegardes de base de données et les changements inclus dans chaque version.

---

## Sauvegardes

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

```
### YYYY-MM-DDTHH:MM_postgres_backup.dump

**Changements :**
-
-
-

---
```

**Remarque :** Les sauvegardes sont listées par ordre chronologique inversé (la plus récente en premier)
