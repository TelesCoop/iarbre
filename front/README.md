# Frontend IA.rbre

Ces instructions vont vous aider à installer et servir le frontend.

## Configuration IDE recommandée

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (et désactiver Vetur).

## Support des types pour les importations `.vue` en TS

TypeScript ne gère pas par défaut les informations de type pour les importations `.vue`, donc nous remplaçons le CLI
`tsc` par `vue-tsc` pour la vérification des types. Dans les éditeurs, nous avons besoin de [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)
pour que le service de langage TypeScript soit conscient des types `.vue`.

## Personnaliser la configuration

Voir [Référence de configuration Vite](https://vitejs.dev/config/).

## Configuration du projet

```sh
yarn
```

### Compiler et rechargement à chaud pour le développement

```sh
yarn dev
```

### Vérification des types, compilation pour la production

```sh
yarn build
```

### Exécuter des tests unitaires avec [Vitest](https://vitest.dev/)

Cela exécute les tests end to end avec le serveur de développement Vite.
C'est beaucoup plus rapide que la version de production.

Il est tout de même recommandé de tester la version de production avec `test:e2e` avant le déploiement (par exemple dans les environnements CI) :

```sh
yarn build
yarn test:e2e
```

### Lint avec [ESLint](https://eslint.org/)

```sh
yarn lint
```
