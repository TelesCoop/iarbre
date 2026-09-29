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

## Dépannage

Procédures pour déployer, revenir en arrière et résoudre les incidents courants (API indisponible, disque plein, redémarrages en boucle, WFS lent, certificat, mise à jour des données) : [Dépannage et procédures techniques](mco/depannage.md).

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

- Écrire sous quel délais sous traités les alertes
