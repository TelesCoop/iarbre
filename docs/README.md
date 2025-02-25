# Documentation

La documentation du projet est construite avec [Mkdocs 📚](https://www.mkdocs.org/).

## Développement & modifications

Pour pouvoir lancer `Mkdocs` en local, vous avez besoin d’installer plusieurs dépendances Python :

```
mkdocs
mkdocs-material
mkdocstrings[python]
mkdocs-git-revision-date-localized-plugin
mkdocs-minify-plugin
pymdown-extensions
```

Vous pouvez ensuite lancer la documentation en local avec la commande suivante :

```
mkdocs serve -a localhost:8001
```

Le port `8000` par défaut de mkdocs étant utilisé par le back de IA·rbre, vous risqueriez un conflit.

!!! warning "Plusieurs fichiers Markdown sont des liens symboliques"

    Afin d'éviter de dupliquer du texte, de nombreux fichiers markdown présents dans le dossier `docs` sont en réalité des liens symboliques vers des fichiers `README.md`. C'est par exemple le cas de `docs/backend/index.md` qui est un lien symbolique vers `back/README.md`.
