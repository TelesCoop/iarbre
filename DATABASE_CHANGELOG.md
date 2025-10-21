# Database Backup Changelog

This document tracks all database backups and the changes included in each version.

---

## Backups

### 2025-10-17T13:06_postgres_backup.dump

**Changes:**

- **Reference File** - Complete database with all 30 migrations (0001-0030)
- **Core Models:** City, Data, Tile, TileFactor
- **Geometry:** Dual projection support (SRID 2154 and 3857 for web mapping)
- **Plantability:** Plantability indices with raw and normalized values
- **MVT Tiles:** Mapbox Vector Tiles for efficient map rendering
- **Geographic Subdivisions:** IRIS model (French statistical areas)
- **Relationships:** Complete City-Tile-IRIS hierarchy
- **City Tracking:** tiles_generated and tiles_computed boolean flags
- **Climate Zones:** LCZ (Local Climate Zones) with climate classification data
- **Vulnerability Assessment:** Day/night vulnerability indices (vulnerability, exposure, capaf, sensibility)
- **Flexible Data:** JSON detail fields on Lcz, Tile, and Vulnerability models
- **Metadata:** Tile meta_factors JSONField for extensible metadata
- **Cadastre:** Land parcel registry with parcel_id and city relationships
- **HotSpots:** Point-based locations of interest linked to cities
- **Data Types:** MVTTile supports lcz, plantability, vulnerability, cadastre
- **Geo Levels:** MVTTile supports tile, city, iris, lcz, cadastre levels
- **Foreign Keys:** Tile vulnerability_idx with SET_NULL cascade behavior

---

## Template for New Backups

Copy this template when adding a new backup entry:

```
## YYYY-MM-DDTHH:MM_postgres_backup.dump

**Changes:**
-
-
-

---
```

## Notes

- Backups are listed in reverse chronological order (newest first)
- Include migration numbers if applicable (e.g., "Applied migration 0030")
- Note any major data imports or updates
- Record backup size to track database growth
