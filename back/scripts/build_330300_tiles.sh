set -euo pipefail

SRC=${1:-file_data/330300/Data}
OUT=${2:-media/330300}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

to_4326() {
    ogr2ogr -t_srs EPSG:4326 -dim XY -lco COORDINATE_PRECISION=7 "$@"
}

to_4326 -select classe_arbres "$TMP/buildings.geojson" "$SRC/batiments_nb_arbres_visibles_mdl.gpkg" batiments_resultats
to_4326 -select pourcentage_arbo "$TMP/quartiers.geojson" "$SRC/quartiers_30.geojson"
to_4326 -select "" -where "pct_vegetation >= 30 AND pct_canopee >= 40 AND surface_parc >= 5000" "$TMP/parks.geojson" "$SRC/parcs_300.geojson"
to_4326 -select "" -where "color = '#2ecc71'" "$TMP/isochrones.geojson" "$SRC/isochrones_by_park_sans_trou.geojson"
to_4326 -select "" "$TMP/trees.geojson" "$SRC/arbres_complets_mdl.geojson"

tippecanoe -e "$OUT" --force -Z10 -z15 --no-tile-compression --drop-densest-as-needed --quiet \
    -L buildings:"$TMP/buildings.geojson" \
    -L quartiers:"$TMP/quartiers.geojson" \
    -L parks:"$TMP/parks.geojson" \
    -L isochrones:"$TMP/isochrones.geojson" \
    -L trees:"$TMP/trees.geojson"
