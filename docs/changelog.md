# Journal de changements

## 🔖 0.4.0 (2025-xx-xx)

### ✨ feat: Intégration de [Sveltia CMS](https://github.com/sveltia/sveltia-cms) pour modifier le site statique

Le contenu du site statique [iarbre.fr](https://iarbre.fr/) peut désormais être modifié sans coder en se connectant avec ses identifiants Github à l'interface d'administration [iarbre.fr/admin](https://iarbre.fr/admin).

Cette interface permettra à l’avenir de modifier et de publier des articles de blog.

![Capture d’écran de Sveltia CMS](assets/images/changelog/v0.4.0/cms_screenshot.png)

&rarr; Ticket [#43](https://github.com/TelesCoop/iarbre/issues/43)

## 🔖 0.3.0 (2025-09-04) - Mise à jour de données et ajout calque vulnérabilité à la chaleur

### ✨ feat: Possibilité d'ouvrir la carte sur un calque spécifique

Le nom du calque est désormais codé dans l'url, ce qui permet de partager une vue spécifique de la carte, voilà par ex. l'url centrée sur Lyon centre avec les données de vulnérabilité à la chaleur : [carte.iarbre.fr/vulnerability/16/45.75773/4.85377](https://carte.iarbre.fr/vulnerability/16/45.75773/4.85377)

&rarr; Ticket [#183](https://github.com/TelesCoop/iarbre/issues/183)

### 🛠️ enhance: Données d'occupation des sols

- Ajout de nouvelles données : place PMR et d'autopartage.
- Mise à jour des données de fibre et de signalisation lumineuse et tricolore.
- Modifications sur certainnes OCS notamment sur les ponts pour lesquelles des tuiles apparaissaient comme plantables

|                           Avant                            |                           Après                            |
| :--------------------------------------------------------: | :--------------------------------------------------------: |
| ![Avant MAJ](assets/images/changelog/v0.3.0/avant_MAJ.png) | ![Après MAJ](assets/images/changelog/v0.3.0/apres_MAJ.png) |

&rarr; Ticket [#178](https://github.com/TelesCoop/iarbre/issues/178)

### ✨ feat: Calque vulnérabilité à la chaleur

Nous avons commencé l'intégration des [travaux](https://geoweb.grandlyon.com/portal/apps/storymaps/collections/7e7862ec92694601a7085074dcaf7481?item=3) de Maurine Di Tommaso (Direction Environnement, Écologie, Énergie). Le travail est en cours pour la séparation jour/nuit et une lisibilité accrue des scores.

![Capture d'écran pour le calque vulnérabilité à la chaleur](assets/images/changelog/v0.3.0/vulnerabilite_chaleur.png)

&rarr; Commit [6c24673](https://github.com/TelesCoop/iarbre/commit/6c24673d4c96230d58d588f56dc54a5d376638ec)

### ✨ feat: Possibilité d'ouvrir la carte à des coordonnées spécifiques

Les coordonnées GPS sont désormais codées dans l'url, ce qui permet de partager une vue spécifique de la carte, voilà par ex. l'url centrée sur le Lac du Bourget : [carte.iarbre.fr/11/45.72454/5.88074](https://carte.iarbre.fr/11/45.72454/5.88074)

&rarr; Commit [0103e77](https://github.com/TelesCoop/iarbre/commit/0103e7703c3934f8eeba012fe80b6f64fa2e319f)

### 👷 devops: Génération de données fictives de tests

Nous sommes désormais en mesure de générer en quelques secondes des données pour tester l'application. Cela signifie en particulier que les tests qui vérifient que la carte est correctement affichée vont désormais être exécutés automatiquement.

&rarr; Commit [7435604](https://github.com/TelesCoop/iarbre/commit/7435604852342895fbf08791261524c58e45b8f8)

### ⚡️ perf: Amélioration de la performance de la génération des tuiles

La fonction de transformation des géométries entre les système Lambert-93 et Pseudo-Mercator a été accélérée en supposant que la transformation d'un polygone est équivalente au polygone formé de la projection de chacun de ces sommets.

&rarr; Commit [7435604](https://github.com/TelesCoop/iarbre/commit/7435604852342895fbf08791261524c58e45b8f8)

### 🧹 chore: Refacto du Tailwind

Nous utilisons Tailwind comme framework CSS sur le projet. Une refacto a été faite afin d'améliorer la maintabilité.

&rarr; Commit [b7ff4cc](https://github.com/TelesCoop/iarbre/commit/b7ff4cc4c4002b0cab206e3f72d319bca2727cc1)

## 🔖 0.2.0 (2025-03-26) - Stabilisations des semaines précédentes

### 🐛 fix: MapPopUp

Il n'existait qu'une PopUp pour le calque de plantabilité, il y en a maintenant une aussi pour les ZCLs. Correction aussi des bugs de fonctionnement.

![Capture d'écran de la popup pour les Zones Climatiques Locales](assets/images/changelog/v0.2.0/lcz-popup.png)

&rarr; Commits [8434d74](https://github.com/TelesCoop/iarbre/commit/8434d74d075c34e27da6d116aafdc152931d927f) et [b87264a](https://github.com/TelesCoop/iarbre/commit/b87264a624db2e5b6bdb9aac6794dafaf2be69dc)

### ✨ feat: Création du changelog

Création d'un fichier Markdown et un onglet dans le doc pour tenir au courant des changements chaque semaine.

&rarr; Commit [68cc328](https://github.com/TelesCoop/iarbre/commit/68cc3282727f7868ff45f2e2a73241c61ea71728)

### ✨ feat: Bouton feedback

Ajout dans la navbar d'un bouton qui ouvre une fenêtre permettant d'envoyer des feedbacks qui sont enregistrés en base.

![Capture d’écran de la vue "Feedback"](assets/images/changelog/v0.2.0/feedback.png)

&rarr; Commit [c8dfdc0](https://github.com/TelesCoop/iarbre/commit/c8dfdc0ed35f1615cae58dc20759d525653fbcbe)

### ✨ feat: Légende ZCL + sources des données

Mise à jour de la légende des ZCLs et ajout d'un lien vers la source des données dans le `AttributionControl` de `MapLibre` : [ERASME](https://datagora.erasme.org/projets/calque-de-plantabilite/) pour le Calque de Plantabilité et le [CEREMA] (https://www.data.gouv.fr/en/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/)pour les Zones Climatiques Locales

![Capture d'écran de la mention du CEREMA](assets/images/changelog/v0.2.0/mention-cerema.png)

&rarr; Commit [7f45234](https://github.com/TelesCoop/iarbre/commit/7f45234d702382348a10a9cbaed87496445497e0)

### ✨ feat: Standardisation de l'API avec DjangoRestFramework

Les routes d'API étaient définies à la main, maintenant nous utilisant une API REST à l'aide de DjangoRestFramework

&rarr; Ticket [#98](https://github.com/TelesCoop/iarbre/issues/98)

### 👷 devops: CI déploiement automatique des branches de développement

Quand une PR est prête pour review, une instance est deployée par la CI pour visualiser en ligne la nouvelle feature.

&rarr; Commit [fa1e56a](https://github.com/TelesCoop/iarbre/commit/fa1e56aa56141eb19b57174fab599b51f5ca2a7e)

### ✅ test: Meilleurs tests de génération des tuiles sur la grille

On teste maintenant sur des villes fictives (et plus petites) que les tuiles couvrent bien toutes la surface et qu'elles ne se chevauchent pas. Ca été aussi à l'occasion de revoir la génération de grille pour réduire le nombre de tuiles inutiles créées.

&rarr; Commit [af7ac23](https://github.com/TelesCoop/iarbre/commit/af7ac23391666c34ebb5127712d217da1c3bd9f8)

## 🔖 0.1.0 (2025-03-12) - Première version

### ✨ feat: Calque de plantabilité

Affiche le calque de plantabilité à la maille 20x20m avec des tuiles hexagonales et des données remises à jour. La [méthodologie](https://www.data.gouv.fr/fr/datasets/cartographie-des-zones-https://github.com/TelesCoop/iarbre/issues/178
Affiche les Zones Climatique Locales, telle que calculées par le [CEREMA](https://www.data.gouv.fr/fr/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/).
Le changement entre les calques se fait à l'aide

### ✨ feat: Site vitrine

Le [site](https://iarbre.fr) de présentation du projet est en ligne. Il est généré à partir des fichiers présents dans le dossier `static`.

### 📝 doc: Création d'une documentation avec MkDocs

La doc est en [ligne](https://docs.iarbre.fr) et est générée à l'aide `MkDocs`.

### ✨ feat: Popup au clic du score de plantabilité

En cliquant sur le calque de plantabilité, un popup apparaît pour afficher le score de la tuile.

![Capture d'écran de la popup](assets/images/changelog/v0.1.0/popup.png)

### ✨ feat: CI et deploy

Un CI sur GitHub déploie automatiquement la branche `dev` sur l'instance de [`preprod`](https://preprod-carte.iarbre.fr) et la branche `main` surl'instance de [`prod`](https://carte.iarbre.fr), après avoir fait tourner l'intégralité des tests (front et back).
Il existe aussi une instance [`feature`](https://feature-carte.iarbre.fr) pour tester une feature en ligne.

&rarr; Commit [f78b230
](https://github.com/TelesCoop/iarbre/commit/f78b230d08168eddf18c6d2fa52ab133b58eea9d)

> Le suivi des changements a été créé en février 2025 mais le projet a commencé en novembre 2024 !
