# Inventaire stratifié du végétal

## Origine des données

Les données ont été produites par un travail conjoint entre [TelesCoop](https://www.telescoop.fr/) et le [LIRIS](https://liris.cnrs.fr/). Le LIRIS a produit une note sur les méthodes permettant de produire un inventaire de végétation en contexte urbain qui se trouve [ici](https://github.com/VCityTeam/UD-IArbre-Research/blob/master/vegetalisation/Pr%C3%A9sentation%20Cotech%2020-11-2025%20Segmentation%20V%C3%A9g%C3%A9talisation.pdf). Puis chez TelesCoop nous avons industrialisé la démarche et proposé un pipeline automatisé.

Actuellement les données affichées ont été générées avec le code provenant de cette [release](https://github.com/TelesCoop/vegestrate/releases/tag/v1.0-metropole-lyon-2023).

### Données d'entrées

Les données d'entrée proviennent de data.grandlyon :

- Les nuages de point [LIDAR de 2023](https://data.grandlyon.com/portail/fr/jeux-de-donnees/nuage-de-points-lidar-2023-de-la-metropole-de-lyon/info);
- Les [orthophotos 2023](https://data.grandlyon.com/portail/fr/jeux-de-donnees/orthophotographie-2023-de-la-metropole-de-lyon/info).

## Méthode

Nous utilisons d'un côté la classification des nuages de points LIDAR et par ailleurs la classification des orthophotos à l'aide de FLAIR-HUB(https://github.com/IGNF/FLAIR-HUB) de l'IGN puis les 2 classifications sont fusionnées.
La précision de la classification, taille d'un pixel, est un carré de **20cmsx20cms**. Cette résolution a été choisie car le modèle FLAIR-HUB a été entraîné sur des images à cette résolution.

### Classification des nuages de points LIDAR

Les nuages de points sont déjà classées, nous récupérons donc les points correspondants aux catégories 4 `végétation moyenne de 1,5-5 m`, 5 `végétation haute 5-15 m` et 8 `végétation haute > 15 m`. 5 et 8 sont rassemblées pour définir une seule catégorie végétation haute. Le reste est dans la catégorie `Autre`.
La classification des végétation basses ne fonctionne pas bien avec le LIDAR, nous ne l'utilisons pas.
Le nuage de point est rasterisé en utilisant une résolution de 0.2m.

### Classification des orthophotos avec FLAIR-HUB

Nous utilisons la version avec encoder Swin large, decoder UPerNet et en RGB. Les poids sont disponibles sur [HuggingFace)(https://huggingface.co/IGNF/FLAIR-HUB_LC-A_RGB_swinlarge-upernet).
La résolution des orthophotos est réduite à l'aide d'une interpolation bi-cubique pour passer d'une résolution de 5cms à 20cms. Ce choix s'eplique de deux façons :

- Garder une résolution existante dans les années précédentes afin de pouvoir avoir des analyses diachroniques;
- Avoir la même résolution que les données d'entraînement de FLAIR-HUB afin de maximiser les performances.

Les dalles d'orthophotos sont dans un premier temps élargis avec les 8 dalles voisines (à une résolution de 0.2m, on passe d'une dalle 625x625 à une dalle 1875x1875). C'est sur cette _mosaic_ que la prédiciton est faites sur des patchs de 512 pixels et le recouvrement entre patchs est de 256 pixels. Les patchs utilisent les données de plusieurs dalles afin d'éviter les effets de bord lorsque les dalles sont fusionnées. On ne conserve que la prédiction au centre de la dalle. Nous utilisons une test-time augmentation (TTA) avec des flips horizontaux et verticaux pour plus de robustesse. Parmis les 20 classes, nous ne conservons que celles relatives à la végétation haute, moyenne et basse.

### Fusion des résultats

Nous partons des résultats LIDAR pour la végétation moyenne et haute, auquelle on ajoute le résultat de végétation basse de FLAIR-HUB. Finalement on met à jour les zones classées comme `Autre` par le LIDAR mais qui sont de la végétation moyenne et haute pour FLAIR-HUB. Ces zones correspondent souvent à des zones proches des bâtiments qui sont mal détectées par le LIDAR et mieux avec les orhtophotos.

### Postprocessing

Pour nettoyer les artefacts de classifications, on procède d'abord à une fermeture morphologique (dilation, fusion puis érosion) puis dans un second temps on applique l'algorithme de [Sieve](https://gdal.org/en/stable/programs/gdal_sieve.html).

## Limites

La qualité du résultat est très dépendante du LIDAR qui reste la meilleure manière de classifier la végétation, hors zones herbacées, de manière précise (résolution de l'ordre du mètre).
La métropole de Lyon produit une couverture du territoire en THD (100 points par m2 en zone urbaine dense et 30 ailleurs) ce qui permet une classification très précise. En zone urbaine dense, c'est parfois trop car on a des points qui traversent le couvert arboré et se retrouvent classés en zone herbacée qui est en dessous.
Comme évoqué plus haut, le LIDAR pert en précision dans les zones proches des bâtiments.

Le modèle FLAIR-HUB permet à une résolution très compétitive, 20cm, des détections de zones herbacés très précises. Le modèle se comporte également très bien dans les zones proches des bâtiments où le LIDAR est moins bon.

Nous ne disposons pas de vérité terrain à l'échelle de la Métropole, car cette donnée n'existe pas, qui permetterait de calculer des métriques quantitatives de performance. Pour évaluer la performance nous sommes dépendants d'évaluations qualitatives avec les orthophotos en dessous de plan ou à l'aide d'experts d'un territoire précis.
