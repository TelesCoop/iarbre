import os

import pandas as pd
import numpy as np
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from sklearn.linear_model import SGDRegressor, RidgeCV
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
    d2_absolute_error_score,
)
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
from tqdm import tqdm

from iarbre_data.management.commands.utils import load_geodataframe_from_db, select_city
from iarbre_data.models import Tile, TileFactor
from scipy.spatial import cKDTree


def city_local_reg(city):
    city_geometry = city.geometry
    tiles_queryset = Tile.objects.filter(
        geometry__intersects=GEOSGeometry(city_geometry.wkt)
    )
    tile_data = load_geodataframe_from_db(
        tiles_queryset, ["id", "plantability_indice"]
    )  # Get Tiles and indice values
    tile_data.crs = 2154

    factor_queryset = TileFactor.objects.filter(
        tile_id__in=tile_data["id"]
    )  # Get factor values for these tiles
    fields = ["tile_id", "factor", "value"]
    factor_scores = pd.DataFrame(
        [
            dict(**{field: getattr(data, field) for field in fields})
            for data in factor_queryset
        ]
    )
    factor_scores.fillna(0, inplace=True)  # Replace NA for no factor by 0

    # Pivot table to have columns corresponding to each factor
    restructured_df = factor_scores.pivot_table(
        index="tile_id",  # Rows: unique tile IDs
        columns="factor",  # Columns: unique factors
        values="value",  # Values for the factor columns
    ).reset_index()  # Convert the tile_id index back to a column
    restructured_df.fillna(0, inplace=True)

    target = (
        tile_data.set_index("id")
        .loc[restructured_df["tile_id"], "plantability_indice"]
        .values
    )
    neighbor_features = pd.DataFrame(index=restructured_df["tile_id"])
    print(f"Neighboor features: {len(neighbor_features)}")
    X = restructured_df.drop(columns=["tile_id"])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(
        X_scaled, columns=X.columns, index=restructured_df["tile_id"]
    )

    # Cross validation
    models = {
        "SGDRegressor(loss='huber', penalty='l2', shuffle=False)": SGDRegressor(
            loss="huber", penalty="l2", shuffle=False
        ),
        "SGDRegressor(penalty='l2', shuffle=False)": SGDRegressor(
            penalty="l2", shuffle=False
        ),
        "SGDRegressor(loss='huber', penalty='elasticnet', shuffle=False)": SGDRegressor(
            loss="huber", penalty="elasticnet", shuffle=False
        ),
        "RidgeCV()": RidgeCV(),
        "SGDRegressor(loss='huber', penalty='l2', shuffle=True)": SGDRegressor(
            loss="huber", penalty="l2", shuffle=True
        ),
        "DummyRegressor()": DummyRegressor(),
    }
    for model_name, model in models.items():
        print(model_name)
        kf = KFold(n_splits=5, shuffle=False)  # No shuffling for spatial consistency
        mae_scores = []
        r2_scores = []
        map_scores = []
        d2_scores = []
        for train_index, test_index in kf.split(X_scaled_df):
            X_train, X_test = (
                X_scaled_df.iloc[train_index],
                X_scaled_df.iloc[test_index],
            )
            y_train, y_test = target[train_index], target[test_index]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            map_score = mean_absolute_percentage_error(y_test, y_pred)
            d2 = d2_absolute_error_score(y_test, y_pred)
            mae_scores.append(mae)
            r2_scores.append(r2)
            map_scores.append(map_score)
            d2_scores.append(d2)

        mean_mae = np.mean(mae_scores)
        mean_r2 = np.mean(r2_scores)
        mean_map = np.mean(map_scores)
        mean_d2 = np.mean(d2_scores)

        print(f"Cross-Validated Mean Absolute Error (MAE): {mean_mae:.4f}")
        print(f"Cross-Validated R² Score: {mean_r2:.4f}")
        print(f"Cross-Validated Mean Absolute Percentage Error (MAPE): {mean_map:.4f}")
        print(f"Cross-Validated D2 Absolute Error Score: {mean_d2:.4f}")
        print()

    if os.path.exists("X_final.csv"):
        X_final = pd.read_csv("X_final.csv")
    else:
        # Build a spatial index for faster neighbor search
        tile_data["centroid"] = tile_data["geometry"].centroid
        tile_tree = cKDTree(
            np.vstack(tile_data["centroid"].apply(lambda p: (p.x, p.y)))
        )

        # Create a lookup dictionary for tile geometries
        tile_geom_dict = tile_data.set_index("id")["geometry"].to_dict()

        for idx, tile_id in tqdm(enumerate(restructured_df["tile_id"])):
            tile_geometry = tile_geom_dict.get(tile_id, None)
            if tile_geometry is None:
                continue

            # Find touching tiles
            tile_centroid = tile_geometry.centroid
            _, neighbor_idx = tile_tree.query(
                (tile_centroid.x, tile_centroid.y), k=10
            )  # Look only in the 10 closest
            neighbor_ids = tile_data.iloc[neighbor_idx]["id"].tolist()
            neighbor_ids = [
                nid
                for nid in neighbor_ids
                if tile_geom_dict[nid].touches(tile_geometry)
            ]
            filtered_neighbor_ids = [
                nid for nid in neighbor_ids if nid in X_scaled_df.index
            ]
            if len(filtered_neighbor_ids) > 0:
                try:
                    neighbor_means = X_scaled_df.loc[filtered_neighbor_ids].mean(axis=0)
                except Exception as e:
                    print(e)
                    continue
            else:
                print("No neighbors")
                neighbor_means = np.zeros(
                    X_scaled.shape[1]
                )  # If no neighbors, set to 0

            for idx_feat, feature in enumerate(X_scaled_df.columns):
                neighbor_features.loc[
                    idx, f"neighbor_mean_{feature}"
                ] = neighbor_means.iloc[idx_feat]

        # Merge neighbor features into X
        neighbor_features.dropna(inplace=True)
        X_final = pd.concat(
            [
                X_scaled_df.reset_index(drop=True),
                neighbor_features.reset_index(drop=True),
            ],
            axis=1,
        ).fillna(0)
        X_final.to_csv("X_final.csv", index=False)

    # Cross validation
    models = {
        "SGDRegressor(loss='huber', penalty='l2', shuffle=False)": SGDRegressor(
            loss="huber", penalty="l2", shuffle=False
        ),
        "SGDRegressor(penalty='l2', shuffle=False)": SGDRegressor(
            penalty="l2", shuffle=False
        ),
        "SGDRegressor(loss='huber', penalty='elasticnet', shuffle=False)": SGDRegressor(
            loss="huber", penalty="elasticnet", shuffle=False
        ),
        "RidgeCV()": RidgeCV(),
        "SGDRegressor(loss='huber', penalty='l2', shuffle=True)": SGDRegressor(
            loss="huber", penalty="l2", shuffle=True
        ),
        "DummyRegressor()": DummyRegressor(),
    }
    for model_name, model in models.items():
        print(model_name)
        kf = KFold(n_splits=5, shuffle=False)  # No shuffling for spatial consistency
        mae_scores = []
        r2_scores = []
        map_scores = []
        d2_scores = []
        for train_index, test_index in kf.split(X_final):
            X_train, X_test = (
                X_final.iloc[train_index],
                X_final.iloc[test_index],
            )
            y_train, y_test = target[train_index], target[test_index]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            map_score = mean_absolute_percentage_error(y_test, y_pred)
            d2 = d2_absolute_error_score(y_test, y_pred)
            mae_scores.append(mae)
            r2_scores.append(r2)
            map_scores.append(map_score)
            d2_scores.append(d2)

        mean_mae = np.mean(mae_scores)
        mean_r2 = np.mean(r2_scores)
        mean_map = np.mean(map_scores)
        mean_d2 = np.mean(d2_scores)

        print(f"Cross-Validated Mean Absolute Error (MAE): {mean_mae:.4f}")
        print(f"Cross-Validated R² Score: {mean_r2:.4f}")
        print(f"Cross-Validated Mean Absolute Percentage Error (MAPE): {mean_map:.4f}")
        print(f"Cross-Validated D2 Absolute Error Score: {mean_d2:.4f}")
        print()


class Command(BaseCommand):
    help = "Local regression"

    def add_arguments(self, parser):
        parser.add_argument(
            "--insee_code_city",
            type=str,
            required=False,
            default=None,
            help="The INSEE code of the city or cities to process. If multiple cities, please separate with comma (e.g. --insee_code='69266,69382')",
        )

    def handle(self, *args, **options):
        insee_code_city = options["insee_code_city"]
        selected_city = select_city(insee_code_city)
        nb_city = len(selected_city)
        for city in selected_city.itertuples():
            print(f"Selected city: {city.name} (on {nb_city} city).")
            city_local_reg(city)
