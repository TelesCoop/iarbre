# Project Guidelines for Claude Code

## 📖 Documentation

**Read the README files for detailed setup and usage instructions:**

- Main project: [README.md](./README.md)
- Frontend: [front/README.md](./front/README.md)
- Backend: [back/README.md](./back/README.md)

## 📁 Project Overview

IA.rbre is a collaborative platform for production, analysis and visualization of territorial data to support urban adaptation to climate change.

**Key URLs:**

- Production: https://carte.iarbre.fr
- Documentation: https://docs.iarbre.fr

### Quick Start

**Always use the Makefile** to run commands - it handles environment setup automatically (requires `.env` file at project root).

Common commands:

```bash
make run_front          # Frontend dev server
make run_back           # Backend dev server
make tests_unit         # Run tests
```

See [Development Commands](#development-commands) section for the full list.

## 🎨 Frontend (Vue.js + Tailwind)

**Tech Stack:** Vue 3, TypeScript, Tailwind CSS v4, PrimeVue, Pinia, MapLibre GL, Vitest, Cypress

### Styling Guidelines

- **Use Tailwind classes directly** in templates instead of creating scoped CSS classes
- Reusable component classes are defined in `front/src/styles/components.css` and imported in `main.css`
  - Use `.btn-primary` for primary action buttons (green theme)
  - Add new reusable component classes to this file when a pattern is used multiple times across components
- **Important**: We want to remove VeeValidate

### Component Guidelines

- **Use PrimeVue components first** before creating custom components
  - Check [PrimeVue documentation](https://primevue.org/) for available components
  - Only create custom components when PrimeVue doesn't provide the needed functionality
- **Use PrimeVue component props** instead of custom classes when possible
  - Examples: `severity`, `size`, `variant`, `outlined`, `rounded`, etc.
  - Only use custom classes for styling that can't be achieved with built-in props
  - Example: `<Button severity="success" size="large" />` instead of `<Button class="btn-green btn-lg" />`

### Color Scheme

- Primary green: `bg-light-green` (#92a48d)
- Hover green: `bg-green-500` (#78c679)
- Background: `bg-off-white` (#efefed)
- Text: `text-brown` (#32312d)

### Fonts

- Main font: IBM Plex Mono (`font-sans`)
- Accent font: Sligoil (`font-accent`)

### Development Commands

**Use the Makefile** at the project root to run commands (preferred method):

```bash
# Frontend
make install_front       # Install frontend dependencies
make run_front           # Dev server with hot reload
make build_front         # Build for production
make lint_front          # Lint and fix with ESLint
make tests_unit          # Run unit tests
make tests_cypress       # Run e2e tests with coverage
make tests_cypress_dev   # Run e2e tests in dev mode

# Backend
make install_back        # Install backend dependencies
make run_back            # Run Django dev server
make back_migrate        # Run migrations
make back_makemigration  # Create new migrations
make back_shell          # Django shell
make back_cmd cmd="..."  # Run custom Django command

# Database
make safe_recovery                    # Recover DB without deleting models
make back_recover_db_and_media        # Recover DB from backup
make back_backup_db_and_media         # Backup DB and media
make back_backup_list                 # List available backups
```

## 🐍 Backend (Django + PostGIS)

**Tech Stack:** Django 5.2+, PostgreSQL, PostGIS, GDAL

**Django Apps:**

- `iarbre_data`: Land occupation calculations
- `plantability`: Plantability index calculations
- `api`: MVT tile generation and REST API

## 📋 Code Quality

- **Pre-commit hooks**: Install with `pip install pre-commit && pre-commit install`
- **Testing**: Frontend (Vitest + Cypress), Backend (Django tests)
- See [README.md](./README.md) for contribution workflow

## 📝 Important Notes

- Project is primarily in French (UI, docs, comments)
- IDE: VSCode + Volar (disable Vetur)
- Data: Requires `file_data/` folder with non-open-data (contact contact@telescoop.fr)
