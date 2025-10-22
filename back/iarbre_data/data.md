# Calque de plantabilité

Ce calque provient d'un travail de [Exo-Dev](https://exo-dev.fr/) en 2022 qui a été documenté dans cette [notice](https://documents.exo-dev.fr/notice_utilisation_calque_plantabilite_lyon_V1.pdf).

Les scores actuellement affichées sur la [carte](https://carte.iarbre.fr/plantability) ont été calculés en _juillet 2025_ à l'aide des dernières données présentes sur data.grandlyon. Seulement les données de réseaux GRDF/ENEDIS (2022) et d'espaces verts (EVA 2015) ne sont pas à jour de 2025.

## Pondération des facteurs

La pondération de chaque `FACTORS` représente à quelle point il permet une plantation. Plus il est haut plus, c'est plantable et inversement une pondération négative indique une contrainte à la plantation. Ces poids ont été fixés lors d'ateliers
organisés par [Exo-Dev](https://exo-dev.fr/) avec les services de terrains en 2022, voir la [notice](https://documents.exo-dev.fr/notice_utilisation_calque_plantabilite_lyon_V1.pdf) du projet.
Ensuite [Exo-Dev](https://exo-dev.fr/) a cherché à traduire ces **facteurs** en données correspondantes. Par exemple, dire que les transports en commun sont un facteur se traduit en donnée par le jeux de données sur les tracés de bus, tramway ainsi que les arrêts correspondants.

## Données correspondantes

### Données open-data

Toues les données de https://data.grandlyon.com sont récupérées sur leur `geoserver` en utilisant le `WFS` (Web Feature Service).
Les données sont donc récupérées au format `GML3` (Geography Markup Language), un subset de XML. On récupère les données directement dans le référentiel (EPSG) 2154, Lambert-93. Pour le format de l'URL, il est spécifié en suivant les liens de chaque données.

Pour les données BD TOPO et Cartofriches, voir le [lien](https://github.com/TelesCoop/iarbre/blob/dev/back/iarbre_data/data_config.py#L397) pour les paramètres de l'API.

### Données autres

Les données qui ne sont pas disponibles sur Data Grand Lyon et ont été récupéres directement auprès des services métropolitains.

### Tableau récapitulatif

| Nom                                           | Facteur                                                                                          | Source                       | Lien                                                                                                                                       |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Statio Vélov                                  | Statio Vélov                                                                                     | Transport et Mobilité        | https://data.grandlyon.com/portail/fr/jeux-de-donnees/stations-velo-v-metropole-lyon/info                                                  |
| Arbres d’alignement                           | - Souches ou emplacements libres - Arbres                                                        | Environnement Energie Climat | https://data.grandlyon.com/portail/fr/jeux-de-donnees/arbres-alignement-metropole-lyon/info                                                |
| Points d'arrets TCL                           | Arrêt transport en commun                                                                        | SYTRAL                       | https://data.grandlyon.com/portail/fr/jeux-de-donnees/points-arret-reseau-transports-commun-lyonnais/info                                  |
| La Fibre Grand Lyon                           | Réseau fibre                                                                                     | Grand Lyon THD               | https://data.grandlyon.com/portail/fr/jeux-de-donnees/reseau-initiative-publique-fibre-grand-lyon/info                                     |
| Marchés forains                               | Marchés forains                                                                                  | Agriculture et alimentation  | https://data.grandlyon.com/portail/fr/jeux-de-donnees/marches-forains-metropole-lyon/info                                                  |
| Pistes cyclables                              | Pistes cyclables                                                                                 | Transport et Mobilité        | https://data.grandlyon.com/portail/fr/jeux-de-donnees/amenagements-cyclables-metropole-lyon/info                                           |
| Plan d’eau de détail                          | Plan d’eau                                                                                       | Territoire Infrastructures   | https://data.grandlyon.com/portail/fr/jeux-de-donnees/plans-eau-detail-metropole-lyon/info                                                 |
| Plan d'eau et fleuves                         | Plan d’eau                                                                                       | Territoire Infrastructures   | https://data.grandlyon.com/portail/fr/jeux-de-donnees/plans-eau-importants-metropole-lyon/info                                             |
| Ponts                                         | Ponts                                                                                            | Territoire Infrastructures   | https://data.grandlyon.com/portail/fr/jeux-de-donnees/ponts-metropole-lyon/info                                                            |
| Voies ferrées                                 | Voies ferrées                                                                                    | Territoire Infrastructures   | https://data.grandlyon.com/portail/fr/jeux-de-donnees/voies-ferrees-metropole-lyon/info                                                    |
| Tracé du métro                                | Tracé du métro                                                                                   | SYTRAL                       | https://data.grandlyon.com/portail/fr/jeux-de-donnees/lignes-metro-funiculaire-reseau-transports-commun-lyonnais-v2/info                   |
| Tracé du tramway                              | Tracé du tramway                                                                                 | SYTRAL                       | https://data.grandlyon.com/portail/fr/jeux-de-donnees/lignes-tramway-reseau-transports-commun-lyonnais-v2/info                             |
| Tracé de bus                                  | Tracé de bus                                                                                     | SYTRAL                       | https://apidf-preprod.cerema.fr/swagger/#/Cartofriches%20(acc%C3%A8s%20libre)                                                              |
| Cartofriches                                  | Friches                                                                                          | CEREMA                       | https://apidf-preprod.cerema.fr/swagger/#/Cartofriches%20(acc%C3%A8s%20libre)                                                              |
| Réseau de chaleur urbain                      | Réseau de chaleur urbain                                                                         | Environnement Energie Climat | https://data.grandlyon.com/portail/fr/jeux-de-donnees/canalisations-des-reseaux-de-chaleur-et-de-froid-de-la-metropole-de-lyon--copie/info |
| Parkings surfaciques                          | Parkings                                                                                         | Transport et Mobilité, EFFIA | Service voirie                                                                                                                             |
| Batiments                                     | - Bâtiment - Proximité façade                                                                    | IGN BD TOPO                  | https://geoservices.ign.fr/bdtopo                                                                                                          |
| EVA 2015                                      | - Strate arborée - Strate basse et pelouse - Espaces agricoles - Forêts - Espaces artificalisées | Géomatique                   | Géomatique                                                                                                                                 |
| Signalisation tricolore et lumineuse matériel | Signalisation tricolore et lumineuse matériel                                                    | Territoire Infrastructures   | Service voirie                                                                                                                             |
| Assainissement                                | Assainissement                                                                                   | Eau                          | Service eau                                                                                                                                |
| Espace public                                 | - Parcs et jardins publics - Giratoires - Espaces jeux et pietonnier - Friche naturelle          | Territoire Infrastructures   | Service voirie                                                                                                                             |
| Réseau gaz                                    | Rsx gaz                                                                                          | GRDF                         | GRDF                                                                                                                                       |
| Lignes souterraines basse et moyenne tension  | Rsx souterrains ERDF                                                                             | Enedis                       | Enedis                                                                                                                                     |
| Ligne aérienne basse et moyenne tension       | Rsx aériens ERDF                                                                                 | Enedis                       | Enedis                                                                                                                                     |
| Place stationnement PMR                       | PMR                                                                                              | Territoire Infrastructures   | Service voirie                                                                                                                             |
| Station autopartage                           | Auto-partage                                                                                     | Territoire Infrastructures   | Service voirie                                                                                                                             |
| Complément à Fibre Grand Lyon open-source     | Réseau fibre                                                                                     | Territoire Infrastructures   | Service voirie                                                                                                                             |

## Génération calque de plantabilité

Voir [ici](https://docs.iarbre.fr/back/backend/) pour la génération du calque de plantabilité.

## Format données

### Structuration de la donnée

Les données que l'on récupère sont des géométries de type `POLYGON`, `LINESTRING` ou `POINT`. Un certain nombre de transformation
sont appliquées pour transformer en un `POLYGON` qui représente l'occupation au sol du facteur.
