## Origine des données

Les données ont été produites par un travail conjoint entre [TelesCoop](https://www.telescoop.fr/) et le [LIRIS](https://liris.cnrs.fr/). Le LIRIS a produit une note sur les méthodes permettant de produire un inventaire de végétation en contexte urbain qui se trouve [ici](https://github.com/VCityTeam/UD-IArbre-Research/blob/master/vegetalisation/Pr%C3%A9sentation%20Cotech%2020-11-2025%20Segmentation%20V%C3%A9g%C3%A9talisation.pdf). Puis chez TelesCoop nous avons industrialisé la démarche et proposé un pipeline automatisé.

Actuellement les données affichées ont été générées avec le code provenant de cette [release](https://github.com/TelesCoop/vegestrate/releases/tag/v2.0-metropole-lyon-ir-2023). Les différents paramètres du pipeline peuvent se retrouver dans [ce fichier de configuration](https://github.com/TelesCoop/vegestrate/blob/main/pipeline_config.yaml).

### Données d'entrées

Les données d'entrée proviennent de data.grandlyon :

- Les nuages de point [LIDAR de 2023](https://data.grandlyon.com/portail/fr/jeux-de-donnees/nuage-de-points-lidar-2023-de-la-metropole-de-lyon/info);
- Les [orthophotos 2023](https://data.grandlyon.com/files/grandlyon/imagerie/ortho2023/infrarouge/tiff/Vue_ensemble_5cm_CC46/IR2023_Dalle_unique_5cm_CC46.tif") avec infrarouge.

## Méthode

Nous utilisons d'un côté la classification des nuages de points LIDAR et par ailleurs la classification des orthophotos (avec infrarouge) à l'aide de FLAIR-HUB(https://github.com/IGNF/FLAIR-HUB) de l'IGN puis les 2 classifications sont fusionnées.
La précision de la classification, taille d'un pixel, est un carré de **20cmsx20cms**. Cette résolution a été choisie car le modèle FLAIR-HUB a été entraîné sur des images à cette résolution.

### Classification des nuages de points LIDAR

Les nuages de points sont déjà classées, nous récupérons donc les points correspondants aux catégories 4 `végétation moyenne de 1,5-5 m`, 5 `végétation haute 5-15 m` et 8 `végétation haute > 15 m`. 5 et 8 sont rassemblées pour définir une seule catégorie végétation haute. Le reste est dans la catégorie `Autre`.
La classification des végétation basses ne fonctionne pas bien avec le LIDAR, nous ne l'utilisons pas.
Le nuage de point est rasterisé en utilisant une résolution de 0.2m.

### Classification des orthophotos avec FLAIR-HUB

Nous utilisons la version avec encoder Swin large, decoder UPerNet et en IRGB. Les poids sont disponibles sur [HuggingFace)(https://huggingface.co/IGNF/FLAIR-HUB_LC-A_IR_swinlarge-upernet).
La résolution des orthophotos est réduite à l'aide d'une interpolation bi-cubique pour passer d'une résolution de 5cms à 20cms. Ce choix s'eplique de deux façons :

- Garder une résolution existante dans les années précédentes afin de pouvoir avoir des analyses diachroniques;
- Avoir la même résolution que les données d'entraînement de FLAIR-HUB afin de maximiser les performances.

Les dalles d'orthophotos sont dans un premier temps élargis avec les 8 dalles voisines (à une résolution de 0.2m, on passe d'une dalle 625x625 à une dalle 1875x1875). C'est sur cette _mosaic_ que la prédiciton est faites sur des patchs de 512 pixels et le recouvrement entre patchs est de 256 pixels. Les patchs utilisent les données de plusieurs dalles afin d'éviter les effets de bord lorsque les dalles sont fusionnées. On ne conserve que la prédiction au centre de la dalle. Nous utilisons une test-time augmentation (TTA) avec des flips horizontaux et verticaux pour plus de robustesse. Parmis les 20 classes, nous ne conservons que celles relatives à la végétation haute, moyenne et basse.

### Fusion des résultats

Nous partons des résultats LIDAR pour la végétation moyenne et haute, auquelle on ajoute le résultat de végétation basse de FLAIR-HUB. Finalement on met à jour les zones classées comme `Autre` par le LIDAR mais qui sont de la végétation moyenne et haute pour FLAIR-HUB. Ces zones correspondent souvent à des zones proches des bâtiments qui sont mal détectées par le LIDAR et mieux avec les orhtophotos.

### Postprocessing

Pour nettoyer les artefacts de classifications, on procède d'abord à une fermeture morphologique (dilation, erosion puis dilation) puis dans un second temps on applique l'algorithme de [Sieve](https://gdal.org/en/stable/programs/gdal_sieve.html).

## Limites

La qualité du résultat est très dépendante du LIDAR qui reste la meilleure manière de classifier la végétation, hors zones herbacées, de manière précise (résolution de l'ordre du mètre).
La métropole de Lyon produit une couverture du territoire en THD (100 points par m2 en zone urbaine dense et 30 ailleurs) ce qui permet une classification très précise. En zone urbaine dense, c'est parfois trop car on a des points qui traversent le couvert arboré et se retrouvent classés en zone herbacée qui est en dessous.
Comme évoqué plus haut, le LIDAR pert en précision dans les zones proches des bâtiments.

Le modèle FLAIR-HUB permet à une résolution très compétitive, 20cm, des détections de zones herbacés très précises. Le modèle se comporte également très bien dans les zones proches des bâtiments où le LIDAR est moins bon.

Le passage d'orthophotos RGB à IRGB a permis un très leger gain de précision, ce qui est conforme avec les discussions du [papier Flair-Hub](https://arxiv.org/abs/2506.07080).

Il y a des petits artefacts aux limites de la métropole car il n'y a plus de données plus loin qui permettent de les réduire.

Nous ne disposons pas de vérité terrain à l'échelle de la Métropole, car cette donnée n'existe pas, qui permetterait de calculer des métriques quantitatives de performance. Pour évaluer la performance nous sommes dépendants d'évaluations qualitatives avec les orthophotos en dessous de plan ou à l'aide d'experts d'un territoire précis.

### Performances

Nous nous sommes placés au plus proches des conditions d'entraînement de FlairHub, donc les performances attendues sont proches (la vérification n'est que qualitative nous n'avons pas de vérité terrain).

| Metric           | Value  |
| ---------------- | ------ |
| mIoU             | 64.80% |
| Overall Accuracy | 77.73% |
| F-score          | 77.40% |
| Precision        | 77.68% |
| Recall           | 77.44% |

| Class                 | IoU (%) | F-score (%) | Precision (%) | Recall (%) |
| --------------------- | ------- | ----------- | ------------- | ---------- |
| building              | 84.07   | 91.35       | 91.80         | 90.90      |
| greenhouse            | 77.35   | 87.23       | 84.06         | 90.65      |
| swimming pool         | 61.55   | 76.20       | 75.82         | 76.58      |
| impervious surface    | 75.86   | 86.27       | 86.15         | 86.40      |
| pervious surface      | 57.55   | 73.06       | 71.24         | 74.97      |
| bare soil             | 64.14   | 78.16       | 75.27         | 81.28      |
| water                 | 90.44   | 94.98       | 96.04         | 93.95      |
| snow                  | 68.55   | 81.34       | 93.67         | 71.88      |
| herbaceous vegetation | 54.37   | 70.44       | 72.85         | 68.18      |
| agricultural land     | 58.20   | 73.58       | 69.77         | 77.82      |
| plowed land           | 36.07   | 53.02       | 51.80         | 54.29      |
| vineyard              | 78.95   | 88.24       | 85.52         | 91.14      |
| deciduous             | 71.66   | 83.49       | 82.72         | 84.29      |
| coniferous            | 63.00   | 77.30       | 79.44         | 75.27      |
| brushwood             | 30.22   | 46.42       | 49.08         | 44.02      |
