# Dépannage et procédures techniques

Accès SSH au serveur puis commandes Django : `iarbre-ctl <commande>` (`iarbre_preprod-ctl` en preprod).

## Déployer

1. Merger `dev` dans `main` et pousser. `deploy-prod.yml` déploie uniquement ce qui a changé (`back/` et/ou `front/`).
2. Suivre le workflow dans l'onglet Actions. Le smoke test prod se lance à la fin.
3. Dérouler la [checklist post-déploiement](../mco.md#checklist-post-deploiement).

Forcer un déploiement back sans changement de code, depuis `deploy/` :

```bash
ansible-playbook backend.yml -l prod -e force_update=true --vault-password-file vault.key
```

## Revenir à une version précédente des données

1. Lister les versions : `iarbre-ctl backup_db list`.
2. Mettre les noms voulus dans `back/.db_recover_target` (`<dump>, <media.zip>`), committer, pousser sur `main`.

Détails : [gestion des sauvegardes](../back/backend.md#gestion-des-sauvegardes-de-base-de-donnees).

## API ou front indisponible (alerte Uptime Kuma)

1. `sudo supervisorctl status` : `iarbre-backend` (API) et `iarbre-backend-gisserver` (WFS/WMS) doivent être `RUNNING`.
2. Si non : `sudo supervisorctl restart <nom>`, puis lire les logs dans `/var/log/telescoop/iarbre/`.
3. DB : `sudo systemctl status postgresql`.
4. Front ou tout le site : `sudo systemctl status nginx` et `sudo nginx -t`.
5. Vérifier la dernière erreur dans Rollbar et le dernier déploiement dans GitHub Actions. Si le problème suit une MEP, [revenir en arrière](#revenir-en-arriere-code).

## Disque plein (alerte Grafana > 95 %)

1. `df -h` puis `sudo du -xh --max-depth=2 / | sort -h | tail -20`.
2. Nettoyages sûrs :
   - cache nginx API : `sudo find /var/cache/nginx/api -mindepth 1 -delete`
   - cache Django : `iarbre-ctl clear_cache`
   - journaux système : `sudo journalctl --vacuum-time=14d`
3. Si le disque se remplit encore, regarder les logs dans `telescoop/iarbre/backend/back/logs/errors.log`.

## Redémarrages en boucle (alerte supervisor)

1. `sudo supervisorctl tail -f iarbre-backend stderr` (ou `iarbre-backend-gisserver`).
2. Causes fréquentes : mémoire (voir Grafana), migration non appliquée (`iarbre-ctl migrate`), DB indisponible.

## WFS lent

1. Dashboard Grafana WFS : repérer les requêtes à grande `bbox_area` ou gros `feature_count`.
2. Le WFS tourne sur son propre gunicorn (`iarbre-backend-gisserver`) et ne bloque pas la carte. Redémarrer ce seul service si les workers sont saturés.

## Certificat qui expire (alerte Uptime Kuma)

1. `sudo certbot certificates` pour voir la date.
2. `sudo certbot renew`, puis `sudo systemctl reload nginx`. Commande du premier déploiement : [Déploiement](../deploy.md).

## Mise à jour annuelle des données

1. Lancer le pipeline en local : `python manage.py run_pipeline` (voir [Pipeline de plantabilité](../back/backend.md#pipeline-de-plantabilite)).
2. Publier : `python manage.py backup_db backup_db_and_media --zipped`.
3. Mettre à jour `back/.db_recover_target`, déployer en preprod, valider, puis MEP.
4. Mettre à jour le [changelog data](../changelog/database.md).
