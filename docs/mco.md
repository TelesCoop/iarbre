# Maintien en conditions opérationnelles

Serveurs : `carte.iarbre.fr` (prod, branche `main`), `preprod-carte.iarbre.fr` (preprod, branche `dev`).
Mise en production hebdomadaire le mercredi.

## Dispositif en place

| Domaine                                                                   | Outil                                                                                                                   | Alerte                              |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Disponibilité front + `api/health-check/` (vérifie la DB)                 | Uptime Kuma, toutes les minutes                                                                                         | Slack                               |
| Expiration certificats TLS                                                | Uptime Kuma                                                                                                             | Slack                               |
| Ressources serveur (CPU, disque > 95 %, restarts supervisor)              | Grafana                                                                                                                 | Slack                               |
| Temps de réponse WFS                                                      | Grafana (dashboard, logger `wfs`)                                                                                       | Aucune                              |
| Erreurs Django                                                            | Rollbar                                                                                                                 | Slack + email                       |
| Parcours critiques en prod (API, WFS, tuiles de chaque calque, dashboard) | Cypress `front/cypress/prod/`, workflow `prod-smoke.yml`, quotidien 05:00 UTC + après chaque déploiement prod           | Slack                               |
| Dépendances (pip, npm, GitHub Actions)                                    | Dependabot, PRs le lundi, mergées dans la MEP du mercredi                                                               | GitHub                              |
| Patchs de sécurité OS                                                     | unattended-upgrades                                                                                                     | -                                   |
| Sauvegarde DB + médias                                                    | Bucket S3 S (`telescoop_backup`), versions figées produites hors prod                                                   | -                                   |
| Restauration DB                                                           | Chaque déploiement back restaure la version de `back/.db_recover_target` : la restauration est donc testée à chaque MEP | Échec du workflow `deploy-prod.yml` |

Les données ne sont pas modifiées en prod : pas de sauvegarde continue, aucune perte possible au-delà de la dernière version publiée dans le bucket.

## Planning

| Fréquence               | Action                                                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quotidien               | Smoke test Cypress prod (automatique)                                                                                                                     |
| Hebdomadaire (mercredi) | Merge Dependabot, MEP, [checklist post-déploiement](#checklist-post-deploiement), revue Rollbar de la semaine                                             |
| Trimestriel             | [Passe manuelle complète](#passe-manuelle-trimestrielle), revue du tableau [fin de vie](#fin-de-vie-des-composants)                                       |
| Annuel                  | Mise à jour des données (pipeline, lancé manuellement), montée de version Ubuntu / Python / PostgreSQL si besoin, revue des accès et rotation des secrets |

## Runbooks

Accès SSH : voir l'inventaire Ansible. Commandes Django : `iarbre-ctl <commande>` (`iarbre_preprod-ctl` en preprod).

### Déployer

1. Merger `dev` dans `main` et pousser. `deploy-prod.yml` déploie uniquement ce qui a changé (`back/` et/ou `front/`).
2. Suivre le workflow dans l'onglet Actions. Le smoke test prod se lance à la fin.
3. Dérouler la [checklist post-déploiement](#checklist-post-deploiement).

Forcer un déploiement back sans changement de code, depuis `deploy/` :

```bash
ansible-playbook backend.yml -l prod -e force_update=true --vault-password-file vault.key
```

### Revenir en arrière (code)

1. `git revert <commit>` sur `main`, puis pousser.
2. Le déploiement rejoue et restaure la DB : vérifier que `back/.db_recover_target` pointe toujours sur la bonne version.

### Revenir à une version précédente des données

1. Lister les versions : `iarbre-ctl backup_db list`.
2. Mettre les noms voulus dans `back/.db_recover_target` (`<dump>, <media.zip>`), committer, pousser sur `main`.

Détails : [gestion des sauvegardes](back/backend.md#gestion-des-sauvegardes-de-base-de-donnees).

### API ou front indisponible (alerte Uptime Kuma)

1. `sudo supervisorctl status` : `iarbre-backend` (API) et `iarbre-backend-gisserver` (WFS/WMS) doivent être `RUNNING`.
2. Si non : `sudo supervisorctl restart <nom>`, puis lire les logs dans `/var/log/telescoop/iarbre/`.
3. DB : `sudo systemctl status postgresql`.
4. Front ou tout le site : `sudo systemctl status nginx` et `sudo nginx -t`.
5. Vérifier la dernière erreur dans Rollbar et le dernier déploiement dans GitHub Actions. Si le problème suit une MEP, [revenir en arrière](#revenir-en-arriere-code).

### Disque plein (alerte Grafana > 80 %)

1. `df -h` puis `sudo du -xh --max-depth=2 / | sort -h | tail -20`.
2. Nettoyages sûrs :
   - cache nginx API : `sudo find /var/cache/nginx/api -mindepth 1 -delete`
   - tuiles MVT et cache Django : `iarbre-ctl clean_mvt_files && iarbre-ctl clear_cache`
   - journaux système : `sudo journalctl --vacuum-time=14d`
3. Si le disque se remplit encore, regarder les logs dans `/var/log/telescoop/iarbre/` et les médias dans `/telescoop/iarbre/backend/back/media`.

### Redémarrages en boucle (alerte supervisor)

1. `sudo supervisorctl tail -f iarbre-backend stderr` (ou `iarbre-backend-gisserver`).
2. Causes fréquentes : mémoire (voir Grafana), migration non appliquée (`iarbre-ctl migrate`), DB indisponible.

### WFS lent

1. Dashboard Grafana WFS : repérer les requêtes à grande `bbox_area` ou gros `feature_count`.
2. Le WFS tourne sur son propre gunicorn (`iarbre-backend-gisserver`) et ne bloque pas la carte. Redémarrer ce seul service si les workers sont saturés.

### Certificat qui expire (alerte Uptime Kuma)

1. `sudo certbot certificates` pour voir la date.
2. `sudo certbot renew`, puis `sudo systemctl reload nginx`. Commande du premier déploiement : [Déploiement](deploy.md).

### Mise à jour annuelle des données

1. Lancer le pipeline en local : `python manage.py run_pipeline` (voir [Pipeline de plantabilité](back/backend.md#pipeline-de-plantabilite)).
2. Publier : `python manage.py backup_db backup_db_and_media --zipped`.
3. Mettre à jour `back/.db_recover_target`, déployer en preprod, valider, puis MEP.
4. Mettre à jour le [changelog data](changelog/database.md).

## Checklist post-déploiement

Environ 10 minutes, après chaque MEP du mercredi, sur [carte.iarbre.fr](https://carte.iarbre.fr) en navigation privée.

- [ ] Workflows `deploy-prod.yml` et `prod-smoke.yml` au vert
- [ ] Aucune nouvelle erreur Rollbar depuis la MEP
- [ ] La carte s'affiche, calque plantabilité par défaut
- [ ] Changer de calque : vulnérabilité, LCZ, végéstrate, plantabilité x vulnérabilité, biodiversité
- [ ] Cliquer sur un carreau : le score et le détail s'affichent
- [ ] Changer de fond de carte (OSM, satellite, orthophoto)
- [ ] Recherche d'adresse
- [ ] Dashboard : les widgets se chargent
- [ ] Vérifier à la main chaque changement livré dans la MEP
- [ ] Si nouvelle version de données : date de génération correcte sur `https://carte.iarbre.fr/api/metadata/`

## Passe manuelle trimestrielle

Environ 1 heure. Desktop (Firefox et Chrome) puis mobile (iOS ou Android).

**Carte**

- [ ] Chaque calque : affichage, légende, filtre de légende, clic sur un carreau / une zone
- [ ] Couches : QPV, cadastre (jusqu'au zoom max), limites communales, Panoramax (vue immersive)
- [ ] Fonds de carte : OSM, satellite, orthophoto
- [ ] Dessin d'une zone et score dans le polygone
- [ ] Hauteur de végétation (végéstrate)
- [ ] Recherche d'adresse, partage d'URL (la position et le calque sont conservés)
- [ ] Message d'accueil à la première visite, lien expérimentations

**Dashboard**

- [ ] Widgets et sections narratives
- [ ] Dashboard sur un polygone
- [ ] Export PDF : le fichier se télécharge et la mise en page est correcte

**Formulaires et pages**

- [ ] Envoi d'un retour utilisateur (feedback) : il arrive bien à l'équipe
- [ ] Mentions légales, bannière cookies (refuser puis accepter)
- [ ] Téléchargement des rasters

**SIG**

- [ ] QGIS : ajouter le flux WFS (`https://carte.iarbre.fr/api/wfs/`) et charger une couche
- [ ] QGIS : ajouter le flux WMS (`https://carte.iarbre.fr/api/wms/`)

**Transverse**

- [ ] Mobile : panneau, sélecteur de calques, couches
- [ ] Documentation [docs.iarbre.fr](https://docs.iarbre.fr) accessible et à jour
- [ ] Performance : Lighthouse sur la page d'accueil, comparer au trimestre précédent

## Fin de vie des composants

À revoir chaque trimestre. Planifier la montée de version 6 mois avant l'échéance.

| Composant            | Version     | Fin de support |
| -------------------- | ----------- | -------------- |
| Ubuntu (serveur)     | à compléter | -              |
| Python               | 3.10        | octobre 2026   |
| PostgreSQL / PostGIS | 14 / 3      | novembre 2026  |
| Django               | 5.2 LTS     | avril 2028     |
| Node.js              | 24          | avril 2028     |

## Pistes d'amélioration

- Rollbar côté front Vue : les erreurs JavaScript en prod ne remontent pas aujourd'hui.
- Alerte Grafana sur le p95 du WFS et le taux de 5xx (métriques déjà exposées par `django-prometheus`).
- Écrire qui répond aux alertes, et sous quel délai.
