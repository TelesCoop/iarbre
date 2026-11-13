# Audit comparatif EVA 2023 / Végéstrate 2023

## Synthèse

Deux inventaires de la végétation 2023 de la Métropole de Lyon sont comparés sur 527,964 km² : **EVA 2023**, photo-interprétation manuelle en polygones, et **Végéstrate 2023**, raster à 0,2 m issu du LiDAR et des orthophotographies. **L'audit mesure l'accord entre les deux sources, pas leur exactitude** : aucune n'est une vérité terrain. Les pourcentages portent sur la surface comparée.

- **Végétal / non végétal : 92,5 % d'accord.** Les deux sources voient la végétation aux mêmes endroits.
- **Ligneux / herbacé : 84,6 % d'accord ; arbre / arbuste / herbe : 80,2 %.** Plus la comparaison entre dans le détail des strates, plus les définitions diffèrent (arbuste dès 1 m pour EVA, végétation moyenne dès 1,5 m pour le LiDAR de Végéstrate).
- **Forêts (EVA 311) : 98,3 % de la surface conforme** à la règle de couverture du guide EVA selon Végéstrate.
- **Le désaccord est concentré sur les contours.** À l'intérieur des zones végétales EVA, Végéstrate voit de la végétation sur 71,3 % des pixels à moins de 1 m du bord et sur 98,7 % à plus de 10 m.
- **Végéstrate voit la végétation que l'unité minimale d'EVA (100 m²) écarte** : 37,3 % de la végétation ligneuse Végéstrate située en zone EVA non végétale est en taches de moins de 100 m² (arbres isolés, alignements), soit 2,957 km².

![Cinq lieux d'exemple : orthophotographie, EVA 2023, Végéstrate 2023 et accord végétation](figures/lieux.jpg)

![Part des pixels vus végétaux (ou ligneux) par Végéstrate selon la distance au bord des zones EVA](figures/distance_bord.png)

## Données

| Donnée                    | Description                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| EVA 2023                  | Produit par Geofit pour la Métropole par photo-interprétation manuelle. Polygones, champs `COD3` (classe) et `CODH` (classe de hauteur), EPSG:3946. Unité minimale de collecte (UMC) 100 m², largeur minimale de collecte (LMC) 3 m, taux de couverture propre à chaque classe (guide de photo-interprétation Geofit).                                             |
| Végéstrate 2023, classes  | Produit par TelesCoop et le LIRIS. Raster 0,2 m, EPSG:3946. 0 autre, 1 herbacé (FLAIR-HUB), 2 végétation moyenne (LiDAR 1,5-5 m), 3 végétation haute (LiDAR > 5 m). Les zones « Autre » du LiDAR reconnues comme végétation moyenne ou haute par FLAIR-HUB sont complétées (`src/postprocessing/merge_classifications.py`), puis un filtre modal 3x3 est appliqué. |
| Végéstrate 2023, hauteurs | Modèle numérique de hauteur (nDSM) à 0,2 m sur les seuls pixels de végétation, hauteur maximale du pixel arrondie au mètre (`src/core/utils.py`).                                                                                                                                                                                                                  |
| IRIS, communes, LCZ       | Base de données IA.rbre (IRIS INSEE, zones climatiques locales).                                                                                                                                                                                                                                                                                                   |

Le domaine est l'union des IRIS de la Métropole : les deux sources y sont découpées.

**Zone exclue.** L'orthophotographie 2023 est vide sur le camp militaire du Mont Verdun : Végéstrate n'y a pas de donnée, EVA si. Le contour est tracé à partir des pixels transparents de l'orthophotographie Grand Lyon 2023 (WMS `ortho_2023`, 0,5 m). Ces 5,865 km² sont retirés pour les deux sources ; leur contenu EVA est dans `zone_exclue.csv`.

![Zone exclue](figures/zone_exclue.jpg)

## Harmonisation des classes

EVA mêle des classes de couverture et des classes d'usage du sol ; Végéstrate ne décrit que la couverture physique. Chaque classe EVA est rattachée à un groupe de couverture attendue :

| groupe         | libellé                                                 | codes EVA (page du guide)                                                                                                                                  |
| -------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| arbore         | Strate arborée (> 3 m)                                  | 111 (p. 3)                                                                                                                                                 |
| arbustif       | Strate arbustive (1-3 m)                                | 112 (p. 4)                                                                                                                                                 |
| herbace        | Herbacé                                                 | 113 (p. 5), 221 (p. 15), 222 (p. 16), 223 (p. 17), 224 (p. 18), 225 (p. 19), 361 (p. 30), 362 (p. 31), 411 (p. 37)                                         |
| boise_mixte    | Boisé multistrate (forêts, haies, fourrés)              | 241 (p. 21), 311 (p. 22), 312 (p. 23), 321 (p. 24), 322 (p. 25), 331 (p. 26), 341 (p. 27), 342 (p. 28), 351 (p. 29), 371 (p. 32), 372 (p. 33), 374 (p. 34) |
| non_vegetal    | Non végétalisé                                          | 121 (p. 8), 122 (p. 9), 381 (p. 35), 382 (p. 36)                                                                                                           |
| eau            | Eau                                                     | 511 (p. 39), 521 (p. 40), 522 (p. 41), 523 (p. 42), 524 (p. 43), 525 (p. 44), 531 (p. 45), 532 (p. 46), 533 (p. 47)                                        |
| non_comparable | Non comparable (usage du sol, strates mêlées, cultures) | 114 (p. 6), 115 (p. 7), 211 (p. 10), 212 (p. 11), 213 (p. 12), 214 (p. 13), 215 (p. 14), 231 (p. 20), 412 (p. 38)                                          |

Les classes « non comparable » (cultures classées à partir du RPG, friches, jardins collectifs, vergers) sont laissées hors des matrices. Comptées comme végétales, l'accord végétal / non végétal passe à 93,4 %.

## Recoupage des hauteurs

EVA distingue < 1 m, 1-3 m et > 3 m ; Végéstrate distingue la végétation moyenne (1,5-5 m) et haute (> 5 m). Pour comparer les strates, Végéstrate est recoupé sur les seuils d'EVA (variante `principal` : lecture littérale sur hauteurs arrondies : < 1 m herbe, 1 à 3 m arbuste, > 3 m arbre, soit arbuste dès 1 m arrondi et arbre dès 4 m arrondi) :

- les pixels herbacés (classe 1, FLAIR-HUB) restent de l'herbe ;
- les zones de végétation moyenne ou haute (classes 2 et 3) sont reclassées selon leur hauteur médiane ;
- une zone de classe 2 ou 3 dont la hauteur médiane est nulle n'a pas de hauteur mesurée : elle garde sa classe Végéstrate native. C'est le cas de la végétation reconnue par FLAIR-HUB là où le LiDAR ne donne pas de hauteur, notamment autour du camp militaire du Mont Verdun, où la lacune du LiDAR semble plus large que celle de l'orthophotographie.

Une zone est un ensemble 4-connexe de pixels de même classe, comme un polygone de la version vectorielle de Végéstrate. Sa hauteur est la médiane du nDSM sur ses pixels, comme l'attribut `median_height` des polygones Végéstrate publiés dans IA.rbre (`compute_zone_elevation` dans `src/postprocessing/apply_vegetation_elevation.py`). Un recoupage pixel par pixel classerait en arbuste le bord bas des houppiers ; il reste disponible (`height_source: pixel`). Les zones sont calculées par bloc de 2048 pixels avec une marge de 20 m : un massif plus grand prend la médiane de sa partie visible.

Un pixel herbacé de Végéstrate est un pixel où le LiDAR n'a pas vu de végétation et où FLAIR-HUB a reconnu de l'herbe. Les deux sources sont des vues du dessus : là où EVA voit une strate arborée et Végéstrate de l'herbe, c'est un houppier manqué par le LiDAR et lu comme herbe. Ce désaccord pèse contre Végéstrate.

Le nDSM est arrondi au mètre, chaque seuil n'est donc connu qu'à ± 0,5 m. Selon la variante de seuils (`principal`, `seuils_bas`, `seuils_hauts`), l'accord par strate varie de 79,4 % à 80,2 % ; le détail est dans `indicateurs_accord.csv`.

## Niveaux, échelles et indicateurs

Trois niveaux, du plus au moins aligné entre les définitions : **végétation** (végétal / non végétal), **ligneux / herbacé**, **strates** (arbre / arbuste / herbe, sur les seules classes EVA à strate unique : forêts, haies et fourrés sont exclus de ce niveau).

Deux échelles : **le pixel** de 0,2 m (EVA rastérisé sur la grille Végéstrate) et **le polygone EVA**, l'échelle pour laquelle EVA a été conçue.

- **Accord global** et **décomposition du désaccord** selon Pontius et Millones (2011) : désaccord de **quantité** (surfaces totales différentes) et d'**allocation** (surfaces semblables à des endroits différents). Le kappa de Cohen est donné pour mémoire.
- **Conformité des polygones** : part des polygones EVA (et de leur surface) dont la composition Végéstrate respecte la règle de couverture du guide, pour les polygones dont au moins la moitié est dans le domaine.
- **Accord selon la distance au bord** des zones EVA, dedans et dehors.
- **Petites taches** : végétation Végéstrate en taches 4-connexes de moins de 100 m² (l'UMC d'EVA). Une tache qui touche le bord de la fenêtre de calcul est comptée comme grande.
- **Couverture par commune**, et **accord par zone climatique locale (LCZ)** dans `accord_lcz.csv`.

## Résultats

### Accord global

| niveau          | version_vegestrate | surface_km2 | accord | desaccord_quantite | desaccord_allocation | kappa |
| --------------- | ------------------ | ----------- | ------ | ------------------ | -------------------- | ----- |
| vegetation      | natif              | 445,823     | 92,5 % | 0,9 %              | 6,6 %                | 0,848 |
| ligneux_herbace | natif              | 445,823     | 84,6 % | 3,0 %              | 12,4 %               | 0,762 |
| ligneux_herbace | principal          | 445,823     | 84,6 % | 3,0 %              | 12,4 %               | 0,762 |
| strates         | natif              | 380,897     | 80,0 % | 3,0 %              | 17,0 %               | 0,690 |
| strates         | principal          | 380,897     | 80,2 % | 4,3 %              | 15,4 %               | 0,694 |

Au niveau ligneux / herbacé, la variante `principal` donne le même résultat que les classes natives : avec un seuil arbuste à 1 m, seule une hauteur nulle ferait passer une zone moyenne ou haute en herbe, et ces zones gardent leur classe native.

### Matrices de confusion

Part de chaque classe EVA (ligne) selon la classe Végéstrate (colonne), aux niveaux végétation, ligneux / herbacé et strates (variante `principal`).

![Niveau végétation](figures/matrice_vegetation.png) ![Niveau ligneux / herbacé](figures/matrice_ligneux.png) ![Niveau strates](figures/matrice_strates.png)

### Conformité des polygones EVA à leur règle de couverture

La règle porte sur la part du polygone occupée par la strate cible selon Végéstrate (« ligneux » = arbre + arbuste), variante `principal`. Les forêts sont conformes à 98,3 % en surface, la strate arborée à 65,6 % ; la strate arbustive à 4,7 % seulement, ce qui est cohérent avec la différence de définition de l'arbuste (dès 1 m pour EVA, 1,5 m pour le LiDAR de Végéstrate). Détail par classe, avec la page du guide et la médiane, dans `regles_couverture.csv`.

![Conformité des polygones EVA](figures/regles_couverture.png)

### Accord selon la distance au bord des zones EVA

Voir la figure de la synthèse. Dans les zones EVA végétales, Végéstrate voit de la végétation sur 71,3 % des pixels à moins de 1 m du bord, 98,7 % à plus de 10 m. Hors des zones EVA végétales, il en voit sur 35,6 % des pixels à moins de 1 m du bord, 4,1 % à plus de 10 m. Le désaccord se concentre dans les premiers mètres autour des contours.

### Végétation en petites taches (< 100 m²)

Sur toute la végétation Végéstrate, 1,1 % est en taches de moins de 100 m². Dans les zones EVA non végétales, cette part monte à 37,3 % pour la végétation ligneuse : arbres isolés et alignements qu'EVA n'a pas à cartographier.

![Petites taches](figures/petites_taches.png)

### Couverture par commune

Parts calculées sur la surface comparable de chaque commune, une commune par point, taille proportionnelle à la surface. Détail dans `couverture_communes.csv` et `couverture_iris.csv`.

![Couverture par commune](figures/communes.png)

## Limites

- Accord n'est pas exactitude : sans vérité terrain, un désaccord peut venir de l'une, de l'autre ou des deux sources.
- EVA cartographie la couverture dominante de polygones d'au moins 100 m² avec un taux de couverture de 60 à 75 % : jusqu'à un quart d'un polygone « strate arborée » peut légitimement être autre chose. La comparaison au pixel pénalise EVA pour un détail qu'elle ne cherche pas à représenter, d'où la comparaison à l'échelle du polygone.
- Le guide EVA n'indique ni précision de positionnement, ni date ou source des images interprétées.
- Le nDSM est arrondi au mètre et ne porte que sur les pixels que Végéstrate classe en végétation : là où EVA voit un arbre et Végéstrate rien, aucune hauteur ne permet de distinguer un écart de définition d'un écart de détection.
- Les LCZ sont elles-mêmes dérivées en partie de la végétation ; l'accord par LCZ décrit des contextes, pas des causes.

## Reproduire

Ce document est généré à partir de `audit/methodology_template.md` et de `audit/config.yaml` ; les chiffres proviennent des tableaux CSV produits dans le dossier de sortie de l'audit.

```bash
python -m audit.run --config audit/config.yaml
```

Étapes : `audit.prepare` (zone exclue, export IRIS et LCZ depuis la base IA.rbre), `audit.compute` (comptages pixel par blocs), `audit.examples` (rasters des lieux d'exemple), `audit.report` (tableaux et ce document), `audit.figures` (figures), `audit.publish` (PDF et copies vers la documentation et le site). `python -m audit.selfcheck` vérifie les fonctions de calcul sur des cas simples.

Tableaux complets dans le dossier de sortie :

- `indicateurs_accord.csv` : accord et désaccord pour tous les niveaux et toutes les variantes de seuils ;
- `matrices.csv` : matrices en km², parts par ligne et par colonne ;
- `regles_couverture.csv`, `polygones_composition.csv.gz` : conformité par classe et composition de chaque polygone ;
- `distance_bord.csv`, `petites_taches.csv` ;
- `couverture_communes.csv`, `couverture_iris.csv`, `accord_lcz.csv` ;
- `zone_exclue.csv`, `exemples_stats.csv` et les rasters `exemples/<lieu>_*.tif` avec leurs styles QGIS `.qml`.

## Sources

- Geofit, _Guide de photo-interprétation des données EVA_, Métropole de Lyon, version 1 (pages citées dans `audit/config.yaml`).
- Pontius R. G. Jr., Millones M. (2011), _Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment_, International Journal of Remote Sensing, 32(15), 4407-4429.
- Végéstrate : ce dépôt, `README.md` et code cité ci-dessus.
