# Plantability at 1 m - ongoing work

Started 2026-10-21 on branch `planta2026`.

## Goal

Users want a 1 m plantability map. The 5 m grid was kept to avoid being over-optimistic about data accuracy.

Constraints:

- The expert weights in `FACTORS` (`iarbre_data/data_config.py`) are fixed and must not change.
- The only levers are how each layer is represented: buffer width, graded zones, aggregation and resolution.

## Principles agreed

- Lean pessimistic for uncertain data: assume larger errors and penalize more widely rather than risk marking a spot plantable when a network may be there.
- Resolution is a grid property and uncertainty is a per-layer property. The caution must sit in each layer's zone, not in the grid.
- Averaging over 5 m never absorbed errors larger than the buffer. Example: a vector at the tile centre with a 2 m buffer gives 80 % coverage in that tile, while a pipe really 3 m away sits in a 0 % tile. Only the buffer width absorbs position error.
- Negative factor: pessimistic means growing the zone. Positive factor: pessimistic means shrinking it.
- Super-resolution (ViT) is rejected: the vectors already carry the detail, and Enedis has no reference to calibrate against.

## Findings: network position accuracy

Method: the open data lines are compared with PCRS access points (`affleurants`). They carry `idnaturereseau` (GAZ, ELEC, AEP, ASSA..., INCE) and are surveyed to 5-10 cm. Source: Grand Lyon WFS `pub_pcrs.affleurantpointpcrs` and `pub_pcrs.affleurantenveloppepcrs`.

### Gas (Rsx Gaz, ORE): measured

- The lines are not simplified: about 60 % of interior vertices are collinear within 1 cm, with no tolerance plateau.
- Topology is intact: 89 % of line ends touch another line within 2 cm. There is no per-vertex or per-feature jitter.
- Gas valve boxes (`idnatureaffleurant` 04) more than 3 m from a facade are probably on mains (n = 820 in Lyon centre):
  - They are unbiased relative to the line (median -0.02 m).
  - The IQR is about 1.4 m, so sigma is about 1 m perpendicular. This is an upper bound.
- The result is consistent over 6 areas of 3x3 km:
  - The bias is between -0.02 and +0.16 m and the core sigma is 0.6-0.9 m, with a heavy tail.
  - 35-49 % of valve boxes sit within 1 m of a main, against 14-21 % for the water control.
- **Working value: ±1 m.**
- About 2/3 of gas valve boxes are within 2 m of a facade. They are probably service connections, which are absent from the open data.
  - "Proximité façade" (2 m) plus the gas buffer mostly cover them.
  - They are not covered where the main is more than 4 m from the facade: about 40 % of main length with the current buffer, and about 20 % with a 4 m gas buffer.

### Enedis BT / HTA underground (Rsx souterrains ERDF): unknown

- PCRS ELEC chambers are no closer to BT or HTA lines than water valves are, so they are at chance level everywhere.
- Only about 45 % of BT line ends are connected, against about 85 % for gas.
- **Accuracy is unknown and cannot be validated with PCRS.**

### Other

- `espacepublic` (voirie.gpkg) holds public squares, not sidewalks (3215 features).

### Test areas (EPSG:2154)

| Area              | minx   | miny    | maxx   | maxy    |
| ----------------- | ------ | ------- | ------ | ------- |
| Lyon centre       | 842000 | 6518000 | 845000 | 6521000 |
| Vénissieux        | 845200 | 6511100 | 848200 | 6514100 |
| Rillieux          | 845900 | 6524800 | 848900 | 6527800 |
| Écully            | 836600 | 6519500 | 839600 | 6522500 |
| Meyzieu           | 854200 | 6519000 | 857200 | 6522000 |
| Saint-Genis-Laval | 838000 | 6510800 | 841000 | 6513800 |

The analysis scripts (`simplif.py`, `endpoints.py`, `affl.py`, `affl2.py`, `multi.py`, `compare.py`) only lived in a session scratchpad and are not versioned.

## Step 1: 1 m test run

Changes made (not present in the working tree any more, to redo if needed):

- `data_to_raster`:
  - Added `--bbox MINX MINY MAXX MAXY` (EPSG:2154) and `--output-dir`.
  - A bbox run writes a blank raster for absent factors instead of raising.
  - `--grid-size 1` gives native 1 m.
- `compute_plantability_raster`: added `--raster-dir`, and outputs are written there.

Test on Villeurbanne centre, bbox `845100 6519560 847100 6521560`. Outputs are in `media/rasters/test_villeurbanne/{5m,1m}/`:

```bash
python manage.py data_to_raster --grid-size 1 --bbox 845100 6519560 847100 6521560 --output-dir media/rasters/test_villeurbanne/1m/
python manage.py compute_plantability_raster --raster-dir media/rasters/test_villeurbanne/1m/
```

| Metric       | 5 m    | 1 m    |
| ------------ | ------ | ------ |
| Blocked area | 49.2 % | 35.9 % |
| Top class    | 6.7 %  | 10.9 % |
| Mean score   | -2.51  | -1.96  |

For each factor, the 5 m mean coverage equals the 1 m footprint.

## Next steps

1. Settle the open questions on blocking and vegetation (Q1, Q2).
2. Gas: a 2 m buffer plus a margin, with graded zones. Full penalty to about 3 m, fading to 0 at about 4-5 m.
3. Enedis (BT underground, possibly aerial): a wide buffer (about 4-5 m), documented as an assumption.
4. Compute option E as a reference, then compare it with the new 1 m map:
   - Option E is the current logic shown at 1 m: the coverage of a 5x5 m window centred on each 1 m pixel.
   - Compare the share of area penalized per factor, and the class changes, so the experts see the effective weight shift.
5. Check how the class thresholds behave at 1 m (`PLANTABILITY_THRESHOLDS` in `plantability/constants.py`). Scores pile up at the extremes more than at 5 m.
6. Show the Villeurbanne maps (5 m, E, new 1 m) to the experts.
7. Later: Enedis street-side zone (option F).
   - Penalize the sidewalk sections (20-30 m) along the street side the cable runs on.
   - This needs sidewalk polygons, built from PCRS "Limite de voirie" plus facades, or from "Chaussées et trottoirs" if it records widths.
8. Later: storage at 1 m. `raster_plantability_to_geom` creates one Tile per pixel, which would be about 1.2 billion tiles for the Métropole.

## Open questions

- [ ] **Q1 Blocking dilation.**
  - At 5 m, `build_blocked_mask` blocks any tile touching a weight -5 factor. This acts as an implicit building dilation of up to 5 m.
  - At 1 m this is lost, and 13 % of the area becomes unblocked.
  - Should blocking factors be grown by about 2-3 m at 1 m to keep that pessimism, or should the shift be accepted?
- [ ] **Q2 Vegetation strata** (Strate arborée +1, Strate basse +3, Espaces agricoles, Forêts, Espaces artificialisés).
  - They come from `new_all_eva.shp` (2015), simplified with a 3 m tolerance in the pipeline.
  - They are positive factors, so they risk optimism at 1 m.
  - Shrink them, or replace them with `vegestrate_lyonmetro_02m` (0.2 m, more recent)?
- [ ] **Q3 Reliability table** for every factor, to validate. Draft:

  | Category                     | Factors                                                                                                                   |
  | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
  | Precise                      | SLT, PMR, Auto-partage, Arbres/Souches, Ponts, Voies ferrées, Plan eau, espacepublic factors                              |
  | Precise but derived          | Bâtiments (BD TOPO), Proximité façade                                                                                     |
  | Measured                     | Gas                                                                                                                       |
  | Unknown                      | Enedis underground and aerial                                                                                             |
  | Indicative networks          | Assainissement, Réseau de chaleur, Réseau Fibre (could be measured against PCRS sewer and district heating access points) |
  | Line drawn on the route axis | Bus, tram, metro, cycle paths (what does the buffer stand for?)                                                           |
  | Point plus fixed radius      | Arrêts TC, Vélo'v, Entrée parking                                                                                         |
  | Coarse or old                | Vegetation strata                                                                                                         |
  | Areas                        | Parkings, Marchés forains, Friches, Aerodrome                                                                             |

- [ ] **Q4 Enedis margin.** What total width for the wide buffer (4 m? 5 m?)? Does it also apply to aerial BT (currently 1 m)?
- [ ] **Q5 Gas margin values.**
  - Confirm the full-penalty radius (about 3 m) and the fade end (about 4-5 m).
  - Confirm the NF P98-332 distances: under 1 m forbidden, 1-2 m with root barrier, over 2 m free. These are from memory and need checking.
- [ ] **Q6 Gas service connections.** Two options:
  - Accept the gap where the main is more than 4 m from the facade as a documented limit.
  - Or draw segments from PCRS facade-side valve boxes. Coverage would be partial in the suburbs.
- [ ] **Q7 Other networks.** Run the PCRS calibration on Assainissement and Réseau de chaleur as well?
- [ ] **Q8 Effective weight shift.** How large a change in class distribution versus option E is acceptable before the experts must re-validate?
