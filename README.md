# 🌳 IA.rbre

Bienvenue sur la documentation de IA.rbre !

Vous trouverez plus de détails sur le projet sur notre [page](https://iarbre.fr).

Vous pouvez aussi accéder à la [carte](https://carte.iarbre.fr) 🗺️ !

La documentation est aussi accessible [ici](https://docs.iarbre.fr) 📚.

## 📁 Structure du Projet

Voici comment le dépôt est organisé :

```
IArbre/
├── back/      # Code backend (Python Django)
├── front/     # Code frontend (Vue.js)
├── static/     # Page web statique du projet (HTML,CSS)
├── deploy/    # Configuration de déploiement (Ansible)
├── docs/    # Documentation (Markdown)
└── .pre-commit-config.yaml  # Configuration des hooks pré-commit
```

### **back/**

![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ludovicdmt/86d9b33a236f4e03bca8799858fc7f6d/raw/coverage-badge.json)

Ce répertoire contient le backend d'IArbre, construit avec **Django** 🐍.
Il traite les données SIG pour calculer l'occupation des sols (OCS). Il existe ensuite diverses applications Django
pour calculer les indices (plantabilité, etc.) et servir ces données à travers des APIs.

### **front/**

Le frontend est construit avec **Vue.js** 🌟. Principalement ce frontend sert la carte..

### **static/**

Page web statique utilisant **HTML/CSS** 🌐. Pour donner des informations générales sur le projet.

### **deploy/**

Le déploiement est géré à l'aide d'**Ansible** 🛠️.

### **docs/**

La documentation utilise des fichiers Markdown et est construite avec **Mkdocs** 📚.

### **.pre-commit-config.yaml**

Nous nous souçions de la qualité du code ! Le fichier `.pre-commit-config.yaml` garantit que tous les contributeurs
respectent les meilleures pratiques en exécutant des vérifications automatisées avant de permettre un commit.

## 🛠️ Configuration de Pre-Commit

1. **Installer pre-commit** :

```bash
pip install pre-commit
```

2. **Installer les hooks** :

```bash
pre-commit install
```

3. **Exécuter manuellement les hooks (optionnel)** :

```bash
pre-commit run --all-files
```

C'est tout ! Maintenant, à chaque commit, `pre-commit` vérifiera automatiquement votre code. 🧹✨

## 🤝 Contribution

Si vous avez des idées, des bugs ou des demandes de fonctionnalités, n'hésitez pas à ouvrir une [issue](https://github.com/TelesCoop/iarbre/issues).

Vous pouvez également contribuer directement en proposant de nouvelles fonctionnalités :

1. **Forker le dépôt**
2. **Créer une branche de fonctionnalité** : `git checkout -b ma-fonctionnalite-geniale`
3. **Valider vos modifications** : `git commit -m "Ajouter une fonctionnalité géniale"`
4. **Pousser votre branche** : `git push origin ma-fonctionnalite-geniale`
5. **Ouvrir une Pull Request**
