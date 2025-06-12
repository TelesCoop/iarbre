# Deploy IArbre

## Premier déploiement certbot

```
sudo certbot certonly \
  --dns-ovh \
  --dns-ovh-credentials /etc/telescoop/iarbre/dns-ovh-credentials.ini \
  -d "*.iarbre.fr"
```
