
# Mise en production et maintenance avec Ansible d'un site avec Stack Django Vue

## Stack technique

Principaux outils open-sources

- frontend:
  - Serveur nginx
  - framework Nuxt 3
- backend: framework Django, gunicorn pour le wsgi

Outils externes potentiellement payants

- Mailgun pour les mails
- Service compatible S3 pour la sauvegarde de la BDD
- Rollbar pour le suivi des bogues en production

Ce considère donc :

- Que vous utilisez `Nuxt` ou un autre projet qui se compile avec
  `yarn generate/build` pour le frontend. Adapter
  `roles/frontend/tasks/main.yml:Build frontend code` si nécessaire.
  Il est possible d'utiliser les modes statiques et SSR de Nuxt, en fonction
  de la variable `frontend_mode`.
- Que vous utilisez `Django` pour le backend.
- Que vous utilisez les outils externes sus-mentionnés (s'il y en a
  un ou plusieurs que vous n'utilisez pas, il suffit de les supprimer de
  `roles/backend/templates/settings.ini.j2`).
- Que vous utilisez `gunicorn` comme outil `wsgi` pour le backend. À adapter
  dans `roles/backend/teamplte/supervisor.conf.j2`.
- Que vous utilisez
  [telescoop-backup](https://github.com/TelesCoop/telescoop-backup)
  pour sauvegarder votre base de donnée. À adapter dans `roles/backend/tasks/main.yml`.

## Les différents rôles/playbook

Pour un nouveau serveur ou projet, ils sont à lancer dans cet ordre.

- Si c'est un nouveau serveur, utiliser le playbook de
  [ce dépôt](https://github.com/TelesCoop/ansible-ssh-config)
  d'abord pour la configuration ssh

- `base` : Installe les dépendances devops du projet. Configure les mises à jour
  automatiques et les roulements de log nginx
  N'est pas nécessaire en cas d'ajout d'un projet sur le même serveur.

- `backend` : Télécharge le code back, installe les dépendances du backend et paramètre
  `supervisord`.

- `frontend` : Télécharge le code front, installe les dépendances du frontend,
  paramètre `supervisord` en cas de mode `SSR` et paramètre `nginx`.

## Procédure de maintenance

La maintenance est toujours faite via Ansible. Il est donc
nécessaire d'installer Ansible sur son PC, en version 2.9.

Pour pouvoir utiliser Ansible, il faut avoir la clé du
"vault" qui contient des informations sensibles.
Cette clé peut être récupérée auprès du développeur de l'application ou
de vos collègues.
Elle doit être copiée en local, à la racine de ce dépôt, dans un fichier
nommé `vault.key`.

Installation du serveur ou mise à jour de tout :

- `ansible-playbook bootstrap.yml`
- `ansible-playbook base.yml`

### MAJ ou installation du frontend et / ou du backend frontend

`ansible-playbook frontend.yml` et/ou `ansible-playbook backend.yml`

Pour forcer la mise à jour des dépendances et de relancer les process et éventuels
build, ajouter `-e force_update=1` à la fin de la commande.

## Adapter ce template pour un nouveau projet

Commencer par installer, si nécessaire, [`pre-commit`](https://pre-commit.com/)
et l'activer `pre-commit install`. Cela permet d'avoir des vérifications avant
chaque commit.

- modifier le fichier `hosts` pour indiquer sur quel nom de domain ou IP se trouve
  le serveur à manager.
- modifier les variables dans `group_vars/all/vars.yml`, notamment
  `organization_slug`, `project_slug`, `main_user`, `public_hostnames`, `django_project_name`
- modifier les variables dans `group_vars/all/cross_env_vars.yml`, notamment :
  - le port ssh
- vérifier les variables dans `roles/backend/vars/main.yml` et `roles/frontend/vars/main.yml`.
- générer des identifiants Mailgun, S3 et Rollbar pour le projet.
- modifier la clé du coffre-fort Ansible avec une clé générée aléatoirement en
  lançant `bash generate_vault_key_on_first_install.sh`. Cela crée un fichier
  `vault.key` qui contient la clé du coffre-fort Ansible. Sauvegarder cette clé
  en endroit sûr et la partager de manière sûre avec les collègues
  (par ex via un gestionnaire de mot de passe, chez TelesCoop nous utilisons Bitwarden).
- modifier les valeurs du vault: `ansible-vault edit group_vars/all/cross_env_vault.yml`
- Si besoin, ajouter un environnement :

  - Choisir un nouveau nom, par exemple `preprod`.
  - créer un nouveau dossier `preprod` dans group_vars, en partant de `prod` comme
  modèle
  - ajouter une section `preprod` dans `hosts`

## TODO

- Comprendre et adapter dans `base` les règles `iptables` et `RAID`.
