# Journal de changements

## 0.0.1 (2025-03-12) - Première version

### Commit correspondant:

- https://github.com/TelesCoop/iarbre/commit/f78b230d08168eddf18c6d2fa52ab133b58eea9d

### Feat: Calque de plantabilité

Affiche le calque de plantabilité à la maille 20x20m avec des tuiles hexagonales et des données remises à jour. La [méthodologie](https://www.data.gouv.fr/fr/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/) provient de Exo-Dev et ERASME. Il y a eu quelques optimisations pour le calcul des facteurs.

### Feat: Calque des ZCLs

Affiche les Zones Climatique Locales, telle que calculées par le [CEREMA](https://www.data.gouv.fr/fr/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/).
Le changement entre les calques se fait à l'aide

### Feat: Site vitrine

Le [site](https://iarbre.fr) de présentation du projet est en ligne.

### Docs: MkDocs

La doc est en [ligne](https://docs.iarbre.fr) et est générée à l'aide `MkDocs`.

### Feat: Popup au clique du score de plantabilité

En cliquant sur le calque de plantabilité, un popup apparait pour afficher le score de la tuile.

### Feat: CI et deploy

Un CI sur GitHub déploie automatiquement la branche `dev` sur preprod-carte.iarbre.fr et la branche `main` sur carte.iarbre.fr, après avoir fait tourner l'intégralité des tests (front et back).
Il existe aussi feature-carte.iarbre.fr pour tester une feature en ligne.

> Le suivi des changements a été créé en février 2025 mais le projet a commencé en novembre 2024 !
