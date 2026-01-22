# TelesCoop Deploy

Ensemble de scripts et templates Ansible pour automatiser le déploiement et la maintenance de nos applications.

Structure

```
telescoop-deploy/
├── tasks/                           #
|   ├── templates/                   # templates ansible génériques
|   │   ├── nginx.conf.j2            # Pour configurer des sites statiques en https
|   │   └── nginx.http.conf.j2       # Pour servir en http le temps de générer le certificat
│   ├── create-https-certificate.yml # Pour configurer des sites statiques en https
│   └── ...
├── handlers/                        #
│   └── nginx.yml                    # Pour servir en http le temps de générer le certificat
```

## Usage

Créer des playbooks mono-fichiers avec la structure suivante

```yml
---
- name: <Nom du playbook>
  hosts: all # À adapter en fonction du contexte
  vars: # Faire ici le lien entre les variables définies dans `/vars` et celles requises dans les `tasks`
    repo: "{{ frontend_repo }}"
    <variable des /tasks>: "{{ <variable de /vars }}"
  handlers:
    - import_tasks: telescoop-deploy/handlers/XXX.yml
  tasks:
    # Importez les blocs de tâches, dans le bon ordre
    - import_tasks: telescoop-deploy/tasks/XXX.yml
    - import_tasks: telescoop-deploy/tasks/YYY.yml
    # Vous pouvez aussi mettre les votres
    - name: Build code
      # yamllint disable-line rule:line-length
      shell: "source /root/.nvm/nvm.sh && nvm exec {{ node_version.stdout }} npm run build"
      # ...
    # Et potentiellement importer les dernières tâches
    - import_tasks: telescoop-deploy/tasks/YYY.yml
```

## Développement

Principes généraux :

- Assurer une rétro-compatibilité sur les différents projets lorsqu'un fichier de tâche (fichiers `/tasks/*.yml`) est mis à jour ;
- Les noms des fichiers de tâches commencent par un verbe d'action, et en snake-case
