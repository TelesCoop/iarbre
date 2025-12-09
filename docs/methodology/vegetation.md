# Inventaire stratifié du végétal

## Origine des données

Les données ont été produites par un travail conjoint entre [TelesCoop](https://www.telescoop.fr/) et le [LIRIS](https://liris.cnrs.fr/). Le LIRIS a produit une note sur les méthodes permettant de produire un inventaire de végétation en contexte urbain qui se trouve [ici](https://github.com/VCityTeam/UD-IArbre-Research/blob/master/vegetalisation/Pr%C3%A9sentation%20Cotech%2020-11-2025%20Segmentation%20V%C3%A9g%C3%A9talisation.pdf). Puis chez TelesCoop nous avons industrialisé la démarche et proposé un pipeline automatisé.

### Données d'entrées

Les données d'entrée proviennent de data.grandlyon :

- Les nuages de point [LIDAR de 2023](https://data.grandlyon.com/portail/fr/jeux-de-donnees/nuage-de-points-lidar-2023-de-la-metropole-de-lyon/info);
- Les [orthophotos 2023](https://data.grandlyon.com/portail/fr/jeux-de-donnees/orthophotographie-2023-de-la-metropole-de-lyon/info).

## Méthode

Nous utilisons d'un côté la classification des nuages de points LIDAR et par ailleurs la classification des orthophotos à l'aide de FLAIR-HUB(https://github.com/IGNF/FLAIR-HUB) de l'IGN puis les 2 classifications sont fusionnées.

### Classification des nuages de points LIDAR

Les nuages de points sont déjà classées, nous récupérons donc les points correspondants aux catégories 4 `végétation moyenne de 1,5-5 m`, 5 `végétation haute 5-15 m` et 8 `végétation haute > 15 m`. 5 et 8 sont rassemblées pour définir une seule catégorie végétation haute. Le reste est dans la catégorie `Autre`.
La classification des végétation basses ne fonctionne pas bien avec le LIDAR, nous ne l'utilisons pas.
Le nuage de point est rasterisé en utilisant une résolution de 0.8m.

### Classification des orthophotos avec FLAIR-HUB

Nous utilisons la version avec encoder Swin large, decoder UPerNet et en RGB. Les poids sont disponibles sur [HuggingFace)(https://huggingface.co/IGNF/FLAIR-HUB_LC-A_RGB_swinlarge-upernet).
Les orhtophotos sont découpées en patch de 384 pixels et le recouvrement entre patchs est de 256 pixels. Les patchs utilisent les données de plusieurs dalles afin d'éviter les effets de bord. Nous utilisons une test-time augmentation (TTA) avec des flips horizontaux et verticaux pour plus de robustesse. Parmis les 20 classes, nous ne conservons que celles relatives à la végétation haute, moyenne et basse.

### Fusion des résultats

Nous partons des résultats LIDAR pour la végétation moyenne et haute, auquelle on ajoute le résultat de végétation basse de FLAIR-HUB. Finalement on met à jour les zones classées comme `Autre` par le LIDAR mais qui sont de la végétation moyenne et haute pour FLAIR-HUB. Ces zones correspondent souvent à des zones proches des bâtiments qui sont mal détectées par le LIDAR et mieux avec les orhtophotos.
