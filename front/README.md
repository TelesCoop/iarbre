# Frontend IA.rbre ![Frontend coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ludovicdmt/767df5613fc8e7b99ac2a773f5253463/raw/coverage-front-badge.json)

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

```

### Compiler et rechargement à chaud pour le développement

```sh
npm run dev
```

### Vérification des types, compilation pour la production

```sh
npm run  type-check
```

### Exécuter des tests unitaires avec [Vitest](https://vitest.dev/)

```sh
npx cypress run --component
```

### Exécuter des tests end to end avec [Cypress](https://www.cypress.io/)

```sh
cd ../back && python manage.py runserver && cd ../front && npx vite --port=4173 && npx cypress run --e2e
```

#### Code coverage

Pour générer le rapport de coverage, ajouter `CYPRESS_COVERAGE=true` avant `npx cypress run --e2e`
Un dossier `coverage` va être généré.

### Lint avec [ESLint](https://eslint.org/)

```sh
npm run lint
```
