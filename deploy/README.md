# Deploy IArbre

## Gunicorn supervisors

Il y a 2 gunicorn qui tournent, le classique et un deuxième `-gisserver` qui ne s'occupe que des requêtes sur `api/wfs/` et `api/wms`. L'objectif est de ne pas saturer les workers de la carto avec ces requêtes.

## Premier déploiement certbot

```
sudo certbot certonly \
  --dns-ovh \
  --dns-ovh-credentials /etc/telescoop/iarbre/dns-ovh-credentials.ini \
  -d "*.iarbre.fr"
```
