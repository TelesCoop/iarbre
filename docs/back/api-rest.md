# API REST

Cette page décrit l'API DjangoREST (application `api` pour le backend). Elle sert de référence pour le frontend, pour les intégrations SIG.

### Casse des clés JSON

Le renderer par défaut est `djangorestframework_camel_case` :

- les clés des réponses JSON sont converties en **camelCase** (`plantability_normalized_indice` devient `plantabilityNormalizedIndice`), y compris les propriétés des GeoJSON ;
- les clés des corps JSON envoyés en `POST` peuvent être en camelCase ou en snake_case, elles sont converties en snake_case ;
- les **paramètres de requête (query string) ne sont pas convertis** : ils s'écrivent tels que documentés (`city_code`, `geometry__intersects`, etc.).

### Coordonnées et projections

| Contexte                                                             | Projection             | Ordre                                                          |
| -------------------------------------------------------------------- | ---------------------- | -------------------------------------------------------------- |
| Paramètres `lat` / `lng`, `geometry__intersects`, polygones envoyés  | EPSG:4326 (WGS 84)     | `lng,lat` pour `geometry__intersects`, paramètres nommés sinon |
| GeoJSON renvoyés (`qpv/`, `public-buildings/`, `boundaries/cities/`) | EPSG:4326              | `[lng, lat]`                                                   |
| Stockage en base                                                     | EPSG:2154 (Lambert-93) | -                                                              |
| Tuiles MVT                                                           | EPSG:3857              | schéma XYZ                                                     |

Un polygone envoyé sans SRID est considéré en EPSG:4326.

### Limites

- Polygones (`in-polygon`) : surface maximale **5 km²** et **100 sommets** maximum (`back/api/utils/polygon.py`).
- Throttling : seul `POST /short-links/` est limité, à **10 requêtes/minute** par IP anonyme.

### Cache

Beaucoup de vues GET sont mises en cache côté serveur (`cache_page`, cache fichier). La durée est indiquée pour chaque route.

### Codes d'erreur

| Code  | Cas                                                                               |
| ----- | --------------------------------------------------------------------------------- |
| `400` | Paramètre manquant ou invalide. Corps `{"error": "..."}` (ou texte brut pour WMS) |
| `404` | Objet introuvable. Corps `{"detail": "..."}`                                      |
| `504` | Génération PDF trop longue                                                        |

### Valeurs de référence

**`datatype`** (`back/api/constants.py`) :

| Valeur                           | Donnée                                                            |
| -------------------------------- | ----------------------------------------------------------------- |
| `plantability`                   | Indice de plantabilité (tuiles de 5 m)                            |
| `vulnerability`                  | Vulnérabilité à la chaleur                                        |
| `lcz`                            | Zones climatiques locales                                         |
| `vegestrate`                     | Strates de végétation                                             |
| `cadastre`                       | Parcelles cadastrales                                             |
| `biosphere_functional_integrity` | Intégrité fonctionnelle de la biosphère                           |
| `plantability_vulnerability`     | Croisement plantabilité / vulnérabilité (uniquement `in-polygon`) |

**`geolevel`** : `tile`, `city`, `iris`, `lcz`, `cadastre`, `biosphere_functional_integrity`.

**Indice de plantabilité normalisé** : valeurs paires de `0` (non plantable) à `10` (très plantable). Les distributions sont des objets `{"<indice>": <nombre de tuiles>}`. Voir [Facteurs de plantabilité](../methodology/plantability.md).

**Vulnérabilité** : indices de `1` à `9`, jour et nuit. Voir [Atlas des vulnérabilités](../methodology/vulnerability.md).

---

## Référentiel territorial

### `GET /cities/`

Liste des communes de la Métropole avec leurs statistiques agrégées. Lyon est découpée en arrondissements (codes INSEE `69381` à `69389`), le code `69123` ne renvoie rien.

| Paramètre              | Type   | Description                                                      |
| ---------------------- | ------ | ---------------------------------------------------------------- |
| `code`                 | string | Code INSEE exact                                                 |
| `code__in`             | string | Liste de codes INSEE séparés par des virgules                    |
| `geometry__intersects` | string | Point `lng,lat` en EPSG:4326, renvoie la commune qui le contient |

```bash
curl "https://carte.iarbre.fr/api/cities/?geometry__intersects=4.835,45.76"
```

```json
[
  {
    "id": 62,
    "code": "69382",
    "name": "Lyon 2e Arrondissement",
    "plantabilityCounts": {
      "0": 40557,
      "2": 47800,
      "4": 13340,
      "6": 17418,
      "8": 12166,
      "10": 2961
    },
    "averageNormalizedIndice": 2.83,
    "averageIndice": -3.63,
    "treesSurface": 209563.9,
    "bushesSurface": 66671.7,
    "grassSurface": 155050.1,
    "totalVegetationSurface": 431285.8
  }
]
```

Les surfaces de végétation sont en m².

### `GET /cities/{id}/`

Une commune par son identifiant interne (`id`), même format qu'un élément de la liste.

### `GET /iris/`

Liste des IRIS (découpage statistique INSEE infra-communal). Mêmes filtres que `/cities/` (`code`, `code__in`, `geometry__intersects`).

```json
[
  {
    "id": 465,
    "code": "693820202",
    "name": "Bellecour-a Gourjus",
    "city": 61,
    "plantabilityCounts": {
      "0": 2220,
      "2": 1627,
      "4": 283,
      "6": 104,
      "8": 95,
      "10": 5
    },
    "averageNormalizedIndice": 1.34,
    "averageIndice": -5.24
  }
]
```

`city` est l'`id` interne de la commune.

### `GET /iris/{id}/`

Un IRIS par son identifiant interne.

### `GET /boundaries/cities/`

Contours des communes en GeoJSON (`FeatureCollection`), propriétés `code` et `name`. Cache : 30 jours.

---

## Indicateurs

### `GET /dashboard/`

Tableau de bord agrégé pour la Métropole, une commune ou un IRIS. Cache : 1 heure.

| Paramètre   | Type   | Description                             |
| ----------- | ------ | --------------------------------------- |
| `city_code` | string | Code INSEE de la commune                |
| `iris_code` | string | Code IRIS (prioritaire sur `city_code`) |

Sans paramètre, la réponse couvre toute la Métropole. Un code inconnu renvoie `404`.

```json
{
  "city": { "id": 62, "code": "69382", "name": "Lyon 2e Arrondissement" },
  "areaKm2": 0.109,
  "plantability": {
    "averageNormalizedIndice": 1.3,
    "distribution": {
      "0": 2220,
      "2": 1627,
      "4": 283,
      "6": 104,
      "8": 95,
      "10": 5
    },
    "distributionByDivision": [],
    "metaFactors": {
      "Bâtiments": 96.9,
      "Espaces verts": 1.2,
      "Infrastructure de transport": 27.3
    }
  },
  "vulnerability": {
    "averageDay": 6.6,
    "averageNight": 6.8,
    "expoDay": 2.6,
    "expoNight": 2.5,
    "sensibilityDay": 2.4,
    "sensibilityNight": 2.4,
    "capafDay": 1.6,
    "capafNight": 1.9
  },
  "vegetation": {
    "totalM2": 2416.3,
    "treesSurfaceM2": 1558.8,
    "bushesSurfaceM2": 535.7,
    "grassSurfaceM2": 321.7
  },
  "lcz": {
    "averageBuildingSurfaceRate": 73.9,
    "averageBuildingHeight": 23.6,
    "impermeableSurfaceRate": 36.4,
    "permeableSoilRate": 1.3,
    "buildingRate": 36.8,
    "treeCoverRate": 23.4,
    "totalVegetationRate": 14.7,
    "waterRate": 10.9
  },
  "buildings": { "averageBuildingFootprintM2": 232.5 },
  "biosphere": { "averageIndice": 12.8, "distribution": { "6": 2, "7": 1 } }
}
```

| Bloc                                  | Contenu                                                                                                            |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `city`                                | Commune concernée, `null` pour la Métropole                                                                        |
| `plantability.distributionByDivision` | Détail par IRIS (scope commune) ou par commune (scope Métropole), vide pour un IRIS                                |
| `plantability.metaFactors`            | Part moyenne de chaque grande famille de facteurs d'occupation du sol                                              |
| `vulnerability`                       | Moyennes des indices de vulnérabilité, d'exposition (`expo`), de sensibilité et de capacité à faire face (`capaf`) |
| `vegetation`                          | Surfaces de strates arborée, arbustive et herbacée, en m²                                                          |
| `lcz`                                 | Moyennes des indicateurs morphologiques des zones climatiques locales, en % (hauteur en m)                         |
| `buildings`                           | Emprise au sol moyenne des bâtiments, en m²                                                                        |
| `biosphere`                           | Indice moyen et distribution de l'intégrité fonctionnelle de la biosphère                                          |

### `POST /dashboard/in-polygon/`

Même réponse que `GET /dashboard/`, calculée sur un polygone dessiné. `city` vaut `null` et `distributionByDivision` est vide.

Corps : une géométrie GeoJSON `Polygon` en EPSG:4326 (voir [Limites](#limites)).

```bash
curl -X POST "https://carte.iarbre.fr/api/dashboard/in-polygon/" \
  -H "Content-Type: application/json" \
  -d '{"type":"Polygon","coordinates":[[[4.834,45.759],[4.836,45.759],[4.836,45.761],[4.834,45.761],[4.834,45.759]]]}'
```

### `POST /tiles/{datatype}/in-polygon/`

Scores moyens dans un polygone. `datatype` vaut `plantability`, `vulnerability` ou `plantability_vulnerability`.

Corps : une géométrie GeoJSON `Polygon` en EPSG:4326.

```json
{
  "datatype": "plantability",
  "count": 1453,
  "irisCodes": ["693820102", "693820103", "693820201", "693820202"],
  "cityCodes": ["69382"],
  "plantabilityNormalizedIndice": 1.3,
  "plantabilityIndice": 1.3,
  "distribution": { "0": 827, "2": 370, "4": 213, "6": 33, "8": 8, "10": 2 }
}
```

| `datatype`                   | Champs spécifiques                                                                           |
| ---------------------------- | -------------------------------------------------------------------------------------------- |
| `plantability`               | `plantabilityNormalizedIndice`, `plantabilityIndice`, `distribution`                         |
| `vulnerability`              | `vulnerabilityIndiceDay`, `vulnerabilityIndiceNight` (`irisCodes` et `cityCodes` sont vides) |
| `plantability_vulnerability` | Union des deux                                                                               |

Erreurs : `400` (datatype ou polygone invalide), `404` si aucune tuile n'intersecte le polygone.

### `GET /tiles/{datatype}/{id}/`

Détail d'un élément identifié par l'`id` présent dans les propriétés des tuiles MVT. Cache : 24 heures.

| `datatype`                       | Champs                                                                                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `plantability`                   | `id`, `plantabilityNormalizedIndice`, `plantabilityIndice`, `details` (part de chaque facteur sur la tuile), `geolevel`, `datatype` |
| `vulnerability`                  | `id`, indices `vulnerabilityIndex*`, `expoIndex*`, `capafIndex*`, `sensibiltyIndex*` (jour/nuit), `details`, géométries             |
| `lcz`                            | `id`, `lczIndex`, `lczDescription`, `details`, géométries                                                                           |
| `vegestrate`                     | `id`, `indice` (strate), `surface`, `geolevel`, `datatype`                                                                          |
| `biosphere_functional_integrity` | `id`, `indice`                                                                                                                      |

### `GET /tiles/vegetation-height/value/`

Renvoie la hauteur de végétation (canopy height model) en un point.

| Paramètre | Type  | Description         |
| --------- | ----- | ------------------- |
| `lat`     | float | Latitude EPSG:4326  |
| `lng`     | float | Longitude EPSG:4326 |

Réponse : `{"height": 12}` en mètres, `{"height": null}` hors emprise ou sans végétation.

### `GET /biosphere/land-cover-at-point/`

Répartition de l'occupation du sol dans un rayon de 500 m autour d'un point.

| Paramètre | Type  | Description         |
| --------- | ----- | ------------------- |
| `lat`     | float | Latitude EPSG:4326  |
| `lng`     | float | Longitude EPSG:4326 |

```json
[
  {
    "landCover": "feuillu",
    "landCoverLabel": "Feuillu",
    "binary": true,
    "percentage": 6.7
  },
  {
    "landCover": "batiment",
    "landCoverLabel": "Bâtiment",
    "binary": false,
    "percentage": 36.2
  }
]
```

`binary` indique si la classe est favorable (`true`) ou non (`false`) à l'intégrité de la biosphère.

---

## Couches cartographiques

### `GET /tiles/{geolevel}/{datatype}/{z}/{x}/{y}.mvt`

Tuiles vectorielles Mapbox Vector Tile pré-générées (`application/x-protobuf`). Cache : 24 heures. `404` si la tuile n'existe pas.
Sert pour afficher sur une carte MapLibre ou autre mais sinon sans doute peu utile.

Le nom de la couche dans la tuile est `{geolevel}--{datatype}`.

| `geolevel` / `datatype`                                             | Propriétés des entités                                                          |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `tile` / `plantability`                                             | `id`, `indice` (indice normalisé)                                               |
| `tile` / `vegestrate`                                               | `id`, `indice` (strate), `surface`                                              |
| `lcz` / `lcz`                                                       | `id`, `indice`, `description`                                                   |
| `lcz` / `vulnerability`                                             | `id`, `indice_day`, `indice_night`, indices `expo_*`, `capaf_*`, `sensibilty_*` |
| `cadastre` / `cadastre`                                             | `id`, `parcel_id`, `city_code`, `section`, `numero`, `surface`                  |
| `biosphere_functional_integrity` / `biosphere_functional_integrity` | `id`, `indice`                                                                  |

### `GET /tiles/vegetation-height/{z}/{x}/{y}.png`

Tuiles raster PNG 256×256 de la hauteur de végétation, générées à la volée. Cache : 24 heures.

| Paramètre | Valeurs                                                                                                              |
| --------- | -------------------------------------------------------------------------------------------------------------------- |
| `kind`    | `class` (défaut) : pixels colorés par classe. `raw` : hauteur encodée en Terrarium (`R * 256 + G + B / 256 - 32768`) |

### `GET /orthophoto/{z}/{x}/{y}.png`

Proxy des orthophotos de la Métropole de Lyon en tuiles XYZ. Cache : 6 mois. `404` si le service amont échoue.

### `GET /qpv/`

Quartiers prioritaires de la politique de la ville en GeoJSON (`FeatureCollection`). Propriétés : `metadata`, `factor`. Cache : 24 heures.

### `GET /public-buildings/`

Bâtiments publics (IGN BD TOPO, écoles privées exclues, et crèches publiques de Grand Lyon) en GeoJSON (`FeatureCollection`), coordonnées arrondies à 6 décimales. Cache : 24 heures. Données importées par `python manage.py import_public_buildings`.

| Propriété           | Description                                                                                                                                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`              | Nom (toponyme)                                                                                                                                                                                                                                    |
| `category`          | `enseignement`, `sante` (hôpitaux, établissements hospitaliers, maisons de retraite, résidences autonomie), `administratif` (mairies), `culture` (musées, écomusées, bibliothèques, archives), `petite_enfance` (crèches publiques de Grand Lyon) |
| `nature`            | Nature BD TOPO (ex. `Enseignement primaire`, `Collège`, `Mairie`)                                                                                                                                                                                 |
| `natureDetaillee`   | Nature détaillée (ex. `Ecole maternelle`)                                                                                                                                                                                                         |
| `fictif`            | `true` si l'emprise BD TOPO est fictive : la géométrie est alors un `Point`, sinon un `Polygon`/`MultiPolygon`                                                                                                                                    |
| `studentCount`      | Nombre d'élèves (écoles, collèges, lycées publics)                                                                                                                                                                                                |
| `educationPriority` | `REP`, `REP+` ou `null`                                                                                                                                                                                                                           |
| `capacity`          | Nombre de places d'accueil (crèches)                                                                                                                                                                                                              |

---

## Téléchargement et flux SIG

### `GET /rasters/{raster_type}/`

Téléchargement des rasters GeoTIFF (`image/tiff`, en pièce jointe).

| `raster_type`          | Fichier                              |
| ---------------------- | ------------------------------------ |
| `plantability`         | Plantabilité (valeurs)               |
| `plantability_colors`  | Plantabilité (couleurs)              |
| `vegestrate`           | Strates de végétation                |
| `vegestrate_ndsm`      | Hauteur de végétation                |
| `vulnerability`        | Vulnérabilité (valeurs)              |
| `vulnerability_colors` | Vulnérabilité (couleurs)             |
| `lcz`                  | Zones climatiques locales (valeurs)  |
| `lcz_colors`           | Zones climatiques locales (couleurs) |

### `GET /wfs/`

Flux OGC WFS (`django-gisserver`) pour QGIS et autres clients SIG.

| Couche                                  | Champs                                                                                        |
| --------------------------------------- | --------------------------------------------------------------------------------------------- |
| `iarbre:plantability`                   | `geometry`, `plantability_indice`, `plantability_normalized_indice`, `city_code`, `city_name` |
| `iarbre:vegestrate`                     | `geometry`, `strate`, `surface`                                                               |
| `iarbre:biosphere_functional_integrity` | `geometry`, `indice`                                                                          |

Projections : EPSG:2154, EPSG:4326 (CRS84), EPSG:3857. Requêtes standards (`GetCapabilities`, `DescribeFeatureType`, `GetFeature` avec `BBOX`, `COUNT`, `STARTINDEX`), plus `REQUEST=GetTypes` qui renvoie la liste des couches en JSON.

```bash
curl "https://carte.iarbre.fr/api/wfs/?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=iarbre:plantability&BBOX=4.83,45.75,4.84,45.76,urn:ogc:def:crs:EPSG::4326&COUNT=100&OUTPUTFORMAT=geojson"
```

### `GET /wms/`

Flux OGC WMS 1.1.1 / 1.3.0 sur les GeoTIFF présents dans `media/rasters/WMS/`.

| `REQUEST`         | Réponse                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| `GetCapabilities` | XML des capacités (cache 1 heure)                                                                             |
| `GetMap`          | Image PNG. Paramètres `LAYERS`, `BBOX`, `CRS` (1.3.0) ou `SRS` (1.1.1), `WIDTH`, `HEIGHT`, `FORMAT=image/png` |
| `GetLayers`       | Liste JSON `[{"name": "iarbre:lcz", "title": "lcz"}]`                                                         |

Ordre des axes du `BBOX` : en WMS 1.3.0 avec EPSG:4326, `min_lat,min_lon,max_lat,max_lon`. Dans les autres cas, `ouest,sud,est,nord`.

---

## Application

### `POST /feedback/`

Envoie un retour utilisateur par e-mail à l'équipe.

Corps : `{"email": "optionnel@exemple.fr", "feedback": "texte"}`. Réponse `201` avec `email`, `feedback`, `created`.

### `POST /short-links/`

Crée (ou retrouve) un lien court vers un chemin de la carte. Limité à 10 requêtes/minute.

Corps : `{"path": "/plantability/14/45.76/4.83?layers=qpv"}`. Le chemin doit commencer par `/` (pas `//`) et faire au plus 2000 caractères.

Réponse : `{"code": "aB3dE_fG"}`, `201` si créé, `200` s'il existait.

### `GET /short-links/{code}/`

Réponse : `{"path": "/..."}`, `404` si le code est inconnu.

### `POST /dashboard/export-pdf/`

Génère le PDF du tableau de bord (`application/pdf`, pièce jointe `rapport.pdf`). Le corps est le scope d'export du frontend, stocké 5 minutes sous un jeton, puis rendu par un navigateur headless qui ouvre le frontend. `504` en cas de dépassement de délai.

### `GET /dashboard/export-scope/{token}/`

Usage interne au rendu PDF : renvoie le scope stocké, `404` après expiration.

### `GET /metadata/`

Date de génération des données : `{"generationDate": "2026-10"}`. Cache : 24 heures.

### `GET /health-check/`

Vérifie la connexion à la base. Réponse `"OK"`.

---
