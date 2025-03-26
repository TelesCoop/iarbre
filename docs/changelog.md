# Journal de changements

## 0.2.0 (2025-03-26) - Stabilisations des semaines précédentes

### Refacto tailwind

Nettoyage dans le `main.css` et les éléments non généraux ont été re-transférés dans les composants.

&rarr; Commit []()

### Fix: MapPopUp

Il n'existait qu'une PopUp pour le calque de plantabilité, il y en a maintenant une aussi pour les ZCLs. Correction aussi des bugs de fonctionnement.

&rarr; Commit [8434d74](https://github.com/TelesCoop/iarbre/commit/8434d74d075c34e27da6d116aafdc152931d927f)

&rarr; Commit [b87264a](https://github.com/TelesCoop/iarbre/commit/b87264a624db2e5b6bdb9aac6794dafaf2be69dc)

### Feat: Création du changelog

Création d'un fichier Markdown et un onglet dans le doc pour tenir au courant des changements chaque semaine.

&rarr; Commit [68cc328](https://github.com/TelesCoop/iarbre/commit/68cc3282727f7868ff45f2e2a73241c61ea71728)

### Feat: Bouton feedback

Ajout dans la navbar d'un bouton qui ouvre une popin permettant d'envoyer des feedbacks qui sont enregistrés en base.

&rarr; Commit [c8dfdc0](https://github.com/TelesCoop/iarbre/commit/c8dfdc0ed35f1615cae58dc20759d525653fbcbe)

### Feat: Légende ZCL + sources des données

Mise à jour de la légende des ZCLs et ajout d'un lien vers la source des données dans le `AttributionControl` de `MapLibre`.

&rarr; Commit [7f45234](https://github.com/TelesCoop/iarbre/commit/7f45234d702382348a10a9cbaed87496445497e0)

### Refacto API: DjangoRestFramework

Les routes d'API étaient définies à la main, maintenant nous utilisant une API REST à l'aide de DjangoRestFramework

&rarr; Commit []()

### Devops: CI deploy automatique

Quand une PR est prête pour review, une instance est deploy par la CI pour visualiser en ligne la nouvelle feature.

&rarr; Commit [fa1e56a](https://github.com/TelesCoop/iarbre/commit/fa1e56aa56141eb19b57174fab599b51f5ca2a7e)

### Test: Updates sur la grille

On test maintenant sur des villes fictives (et plus petites) que les tuiles couvrent bien toutes la surface et qu'elles ne se chevauchent pas. Ca été aussi à l'occasion de revoir la génération de grille pour réduire le nombre de tuiles inutiles créées.

&rarr; Commit [af7ac23](https://github.com/TelesCoop/iarbre/commit/af7ac23391666c34ebb5127712d217da1c3bd9f8)

## 0.1.0 (2025-03-12) - Première version

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

Un CI sur GitHub déploie automatiquement la branche `dev` sur l'instance de [`preprod`](https://preprod-carte.iarbre.fr) et la branche `main` surl'instance de [`prod`](https://carte.iarbre.fr), après avoir fait tourner l'intégralité des tests (front et back).
Il existe aussi une instance [`feature`](https://feature-carte.iarbre.fr) pour tester une feature en ligne.

&rarr; Commit [f78b230
](https://github.com/TelesCoop/iarbre/commit/f78b230d08168eddf18c6d2fa52ab133b58eea9d)

> Le suivi des changements a été créé en février 2025 mais le projet a commencé en novembre 2024 !
