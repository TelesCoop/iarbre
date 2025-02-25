# Sources de données

# Format données

## Données open-data

Toues les données de https://data.grandlyon.com sont récupérées sur leur `geoserver` en utilisant le `WFS` (Web Feature Service).
Les données sont donc récupérées au format `GML3` (Geography Markup Language), un subset de XML. On récupère les données directement dans le référentiel (EPSG) 2154, Lambert-93. Pour le format de l'URL, il est spécifié en suivant les liens de chaque données.

Pour les données BD TOPO et Cartofriches, voir le lien pour les paramètres de l'API.

## Données autres

Les autres données ne sont pas disponibles sur Data Grand Lyon et ont été récupéres directement auprès des services métropolitains.

## Tableau récapitulatif

| Nom                                           | Facteur                                                                                          | Source                       | Lien                                                                                                                                       |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Statio Vélov                                  | Statio Vélov                                                                                     | Transport et Mobilité        | https://data.grandlyon.com/portail/fr/jeux-de-donnees/stations-velo-v-metropole-lyon/info                                                  |
| Arbres d’alignement                           | - Souches ou emplacements libres - Arbres                                                        | Environnement Energie Climat | https://data.grandlyon.com/portail/fr/jeux-de-donnees/arbres-alignement-metropole-lyon/info                                                |
| Points d'arrets TCL                           | Arrêt transport en commun                                                                        | SYTRAL                       | https://data.grandlyon.com/portail/fr/jeux-de-donnees/points-arret-reseau-transports-commun-lyonnais/info                                  |
| La Fibre Gran Lyon                            | Réseau fibre                                                                                     | Grand Lyon THD               | https://data.grandlyon.com/portail/fr/jeux-de-donnees/reseau-initiative-publique-fibre-grand-lyon/info                                     |
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

# Pondération des facteurs

La pondération de chaque `FACTORS` représente à quelle point il permet une plantation. Plus il est haut plus, c'est plantable
et inversement une pondération négative indique une contrainte à la plantation. Ces poids ont été fixés lors d'ateliers
organisés par Exo-Dev avec les services de terrains en 2022, voir la [notice](https://file.notion.so/f/f/28f51d61-2938-4b1f-bb08-f39f2b1a7fd2/7875e500-461e-4f0e-8a23-efed65d71677/Synthse_du_projet_-_Calque_de_plantabilit.pdf?table=block&id=8db6b6bb-0c64-4ba2-9b19-f9e67a7c1583&spaceId=28f51d61-2938-4b1f-bb08-f39f2b1a7fd2&expirationTimestamp=1722952800000&signature=831-UAU2J3u-l8MOptA2UXHN3MVC9AZQOs9soaTNFOo&downloadName=Synth%C3%A8se+du+projet+-+Calque+de+plantabilit%C3%A9.pdf)
du projet.
