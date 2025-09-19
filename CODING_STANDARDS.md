# 🌳 iArbre Coding Standards

This document outlines the coding standards and conventions used in the iArbre project to ensure consistency, maintainability, and code quality across both backend (Django/Python) and frontend (Vue.js/TypeScript) components.

## 📋 Table of Contents

- [General Principles](#general-principles)
- [Project Structure](#project-structure)
- [Backend Standards (Django/Python)](#backend-standards-djangopython)
- [Frontend Standards (Vue.js/TypeScript)](#frontend-standards-vuejstypescript)
- [Geographic/GIS Standards](#geographicgis-standards)
- [Testing Standards](#testing-standards)
- [Git & Development Workflow](#git--development-workflow)
- [Documentation](#documentation)

## 🎯 General Principles

### Code Quality

- **Readability First**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns within the codebase
- **DRY (Don't Repeat Yourself)**: Avoid code duplication through proper abstraction
- **SOLID Principles**: Apply SOLID principles where appropriate
- **Security**: Never commit secrets, keys, or sensitive information

### Naming Conventions

- Use descriptive and meaningful names for variables, functions, and classes
- Avoid abbreviations unless they are widely understood
- Be consistent with naming patterns within each language/framework

## 📁 Project Structure

```
iarbre-back/
├── back/                 # Django backend
│   ├── api/             # API endpoints and views
│   ├── iarbre_data/     # Main Django app with models
│   ├── plantability/    # Plantability calculations
│   └── requirements.txt # Python dependencies
├── front/               # Vue.js frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── composables/ # Reusable logic
│   │   ├── stores/      # Pinia state management
│   │   ├── types/       # TypeScript type definitions
│   │   └── utils/       # Utility functions
│   └── package.json     # Node.js dependencies
├── docs/                # MkDocs documentation
├── deploy/              # Ansible deployment scripts
└── static/              # Static website
```

## 🐍 Backend Standards (Django/Python)

### File Organization

- **Separate concerns**: Use separate directories for `views/`, `serializers/`, `tests/`
- **Model organization**: Keep related models in the same app
- **Management commands**: Place custom commands in `management/commands/`

### Python Code Style

- **PEP 8 compliance**: Follow Python PEP 8 style guidelines
- **Line length**: Maximum 88 characters (Black formatter default)
- **Import organization**:

  ```python
  # Standard library imports
  from django.db import models
  from django.contrib.gis.db.models import PolygonField

  # Third-party imports
  from rest_framework import serializers

  # Local imports
  from api.constants import GeoLevel, DataType
  ```

### Django Patterns

#### Models

```python
class Tile(models.Model):
    """Elementary element on the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=TARGET_MAP_PROJ, null=True, blank=True)
    plantability_indice = models.FloatField(null=True)

    def get_layer_properties(self):
        """Return the properties of the tile for the MVT datatype."""
        return {
            "id": self.id,
            "indice": self.plantability_normalized_indice,
        }
```

#### Views

```python
class TileView(generics.RetrieveAPIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        try:
            return HttpResponse(
                self.get_object().mvt_file,
                content_type="application/x-protobuf"
            )
        except MVTTile.DoesNotExist:
            raise Http404
```

#### Serializers

```python
class TileSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = Tile
        fields = (
            "id",
            "plantability_normalized_indice",
            "details",
        )

    def get_details(self, obj):
        """Parse JSON string details if needed."""
        if isinstance(obj.details, str):
            try:
                return json.loads(obj.details)
            except json.JSONDecodeError:
                return None
        return obj.details
```

### Constants and Enums

```python
class GeoLevel(TextChoices):
    TILE = "tile", "Tile"
    CITY = "city", "City"
    IRIS = "iris", "Iris"

DEFAULT_ZOOM_LEVELS = (10, 18)
ZOOM_TO_GRID_SIZE = {10: 100, 11: 75, 12: 75}
```

### Error Handling

- Use appropriate Django/DRF exceptions
- Provide meaningful error messages
- Log errors appropriately for debugging

## 🌟 Frontend Standards (Vue.js/TypeScript)

### File Naming Conventions

- **Components**: PascalCase (`MapContextData.vue`)
- **Composables**: camelCase with `use` prefix (`useMapFilters.ts`)
- **Utilities**: camelCase (`enum.ts`, `constants.ts`)
- **Types**: camelCase (`map.ts`, `plantability.ts`)

### Vue Component Structure

```vue
<script lang="ts" setup>
import { useMapStore } from "@/stores/map";
import { DataType } from "@/utils/enum";
import type { PlantabilityData } from "@/types/plantability";

const mapStore = useMapStore();

defineProps({
  fullHeight: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div class="map-context-data-container w-full" data-cy="map-context-data">
    <map-context-data-plantability
      v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
      :data="mapStore.contextData.data as PlantabilityData"
    />
  </div>
</template>
```

### TypeScript Patterns

#### Type Definitions

```typescript
export interface MapScorePopupData {
  lng: number;
  lat: number;
  id: string;
  properties: any;
  score: string;
}

export interface MapParams {
  lng: number;
  lat: number;
  zoom: number;
  dataType: DataType | null;
}
```

#### Enums

```typescript
export enum DataType {
  PLANTABILITY = "plantability",
  VULNERABILITY = "vulnerability",
  CLIMATE_ZONE = "lcz",
}

export const DataTypeToLabel: Record<DataType, string> = {
  [DataType.PLANTABILITY]: "🌳 Score de plantabilité",
  [DataType.CLIMATE_ZONE]: "🌆 Zones climatiques locales",
  [DataType.VULNERABILITY]: "🌡️ Vulnérabilité chaleur",
};
```

#### Composables

```typescript
export function useMapFilters() {
  const filteredValues = ref<(number | string)[]>([]);

  const hasActiveFilters = computed(() => filteredValues.value.length > 0);
  const activeFiltersCount = computed(() => filteredValues.value.length);

  const toggleFilter = (value: number | string) => {
    const index = filteredValues.value.indexOf(value);
    if (index > -1) {
      filteredValues.value.splice(index, 1);
    } else {
      filteredValues.value.push(value);
    }
  };

  return {
    filteredValues,
    toggleFilter,
    hasActiveFilters,
    activeFiltersCount,
  };
}
```

### State Management (Pinia)

```typescript
export const useMapStore = defineStore("map", () => {
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY);
  const currentZoom = ref<number>(14);

  return {
    selectedDataType,
    currentZoom,
  };
});
```

### CSS/Styling

- **Tailwind CSS**: Use Tailwind utility classes for styling
- **PrimeVue**: Use PrimeVue components for UI elements
- **Component scoping**: Avoid global styles, scope styles to components

## 🗺️ Geographic/GIS Standards

### Coordinate Systems

- **Storage**: Use SRID 2154 (Lambert 93) for data storage in PostGIS
- **Display**: Transform to Web Mercator (SRID 3857) for map display
- **API responses**: Include both `geometry` and `map_geometry` fields

### Spatial Data Handling

```python
# Models with spatial fields
class Tile(models.Model):
    geometry = PolygonField(srid=2154)  # Storage projection
    map_geometry = PolygonField(srid=TARGET_MAP_PROJ, null=True, blank=True)  # Display projection

# Automatic geometry transformation
@receiver(pre_save, sender=Tile)
def before_save(sender, instance, **kwargs):
    if instance.map_geometry is None:
        instance.map_geometry = instance.geometry.transform(TARGET_MAP_PROJ, clone=True)
```

### MVT (Mapbox Vector Tiles)

- Store MVT files using Django FileField
- Implement caching for tile endpoints
- Use proper MIME type: `application/x-protobuf`

## 🧪 Testing Standards

### Backend Testing (Django)

```python
class TileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test data
        square = Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), srid=2154)
        self.tile = Tile.objects.create(geometry=square)

    def test_valid_tile_retrieval(self):
        url = "/api/tiles/city/test/10/512/256.mvt"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/x-protobuf")
```

### Frontend Testing

#### Unit Tests (Vitest)

```typescript
import { test, expect } from "vitest";

test("toggleFilter adds and removes values", () => {
  const { filteredValues, toggleFilter } = useMapFilters();

  toggleFilter("test");
  expect(filteredValues.value).toContain("test");

  toggleFilter("test");
  expect(filteredValues.value).not.toContain("test");
});
```

#### E2E Tests (Cypress)

```typescript
describe("Map", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543");
  });

  it("loads with plantability layer", () => {
    cy.getBySel("plantability-legend").should("exist");
    cy.getBySel("map-component").should("exist");
  });
});
```

### Test Data Attributes

- Use `data-cy` attributes for Cypress selectors
- Keep test data separate from production data
- Mock external APIs in tests

## 🔄 Git & Development Workflow

### Branch Naming

- **Feature branches**: `feature/description` or `feat/description`
- **Bug fixes**: `fix/issue-description`
- **Hotfixes**: `hotfix/description`

### Commit Messages

- Use conventional commit format when possible
- Be descriptive and concise
- Reference issue numbers when applicable

```
feat: add vulnerability filtering by day/night mode

- Add vulnerability mode toggle in UI
- Implement filtering logic in useMapFilters composable
- Update map layer rendering based on selected mode

Closes #123
```

### Pre-commit Hooks

- **Python**: Black, isort, flake8
- **JavaScript/TypeScript**: ESLint, Prettier
- **General**: File formatting, trailing whitespace

### Pull Request Guidelines

- Provide clear description of changes
- Include screenshots for UI changes
- Ensure all tests pass
- Request appropriate reviewers

## 📚 Documentation

### Code Documentation

- **Python**: Use docstrings for classes and functions
- **TypeScript**: Use JSDoc comments for complex functions
- **API**: Document endpoints with proper HTTP status codes

### README Files

- Each major component should have a README
- Include setup instructions and examples
- Keep documentation up to date

### Comments

- Use comments sparingly - prefer self-documenting code
- Explain **why**, not **what**
- Remove commented-out code before committing

## 🔧 Tools and Configuration

### Development Tools

- **Backend**: Django, PostgreSQL with PostGIS, pytest
- **Frontend**: Vue 3, TypeScript, Vite, Vitest, Cypress
- **Linting**: ESLint, Prettier, Black, isort
- **Documentation**: MkDocs

### IDE Configuration

- Configure your IDE to use the project's linting rules
- Set up format-on-save for consistent code formatting
- Use appropriate extensions for Django and Vue development

## 🚀 Performance Considerations

### Backend Performance

- Use database indexes appropriately
- Implement caching for expensive operations
- Optimize spatial queries with proper SRID usage

### Frontend Performance

- Lazy load components when appropriate
- Use computed properties for expensive calculations
- Implement proper error boundaries

## 🔒 Security Guidelines

### Backend Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper authentication and authorization
- Validate and sanitize all inputs

### Frontend Security

- Sanitize user inputs
- Use HTTPS for all API calls
- Implement proper error handling to avoid information leakage

---

## 📝 Conclusion

These coding standards are living guidelines that should evolve with the project. When in doubt, follow the existing patterns in the codebase and discuss proposed changes with the team.

For questions or suggestions about these standards, please open an issue or discussion in the project repository.

**Remember**: The goal is to write code that is readable, maintainable, and follows the established patterns of the iArbre project. Consistency is key! 🌳
