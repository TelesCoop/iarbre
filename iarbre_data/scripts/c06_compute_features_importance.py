import pandas as pd
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform

from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.models import City, Tile, TileFactor


class Command(BaseCommand):
    help = "Explore features importance"

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
        if insee_code_city is not None:  # Perform selection only for a city
            insee_code_city = insee_code_city.split(",")
            selected_city_qs = City.objects.filter(insee_code__in=insee_code_city)
            if not selected_city_qs.exists():
                raise ValueError(f"No city found with INSEE code {insee_code_city}")
            selected_city = load_geodataframe_from_db(
                selected_city_qs, ["name", "insee_code"]
            )
        else:
            selected_city = load_geodataframe_from_db(
                City.objects.all(), ["name", "insee_code"]
            )
        nb_city = len(selected_city)

        for city in selected_city.itertuples():
            print(f"Selected city: {city.name} (on {nb_city} city).")
            city_geometry = city.geometry
            tiles_queryset = Tile.objects.filter(
                geometry__intersects=GEOSGeometry(city_geometry.wkt)
            )
            tile_data = load_geodataframe_from_db(
                tiles_queryset, ["id", "indice"]
            )  # Get Tiles and indice values
            tile_data = pd.DataFrame(tile_data.drop(columns="geometry"))
            factor_queryset = TileFactor.objects.filter(
                tile_id__in=tile_data.id
            )  # Get factor values for these tiles
            fields = ["tile_id", "factor", "value"]
            factor_scores = pd.DataFrame(
                [
                    dict(**{field: getattr(data, field) for field in fields})
                    for data in factor_queryset
                ]
            )
            factor_scores["indice"] = tile_data.indice
            factor_scores.fillna(0, inplace=True)
            # Compute correlation between factor values and indice (explainability)
            grouped_corr = (
                factor_scores.groupby("factor")
                .apply(lambda group: group["value"].corr(group["indice"]))
                .reset_index(name="pearson_correlation")
            )
            print(grouped_corr)

            # Use PCA to study maximum variance in the data
            # Pivot table to have columns corresponding to each factor
            restructured_df = factor_scores.pivot_table(
                index="tile_id",  # Rows: unique tile IDs
                columns="factor",  # Columns: unique factors
                values="value",  # Values for the factor columns
            ).reset_index()  # Convert the tile_id index back to a column
            restructured_df.fillna(0, inplace=True)
            y = tile_data[
                np.isin(tile_data["id"], restructured_df["tile_id"].values)
            ].indice
            X = restructured_df.drop(columns=["tile_id"])

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            pca = PCA()
            pca.fit(X_scaled)

            # Factor importance on PC1
            factor_importance = pd.DataFrame(
                {"factor": X.columns, "importance": np.abs(pca.components_[0])}  # PC1
            )

            factor_importance = factor_importance.sort_values(
                by="importance", ascending=False
            )

            # Output the results
            print(factor_importance)

            plt.figure(figsize=(10, 8))
            sns.barplot(
                x="importance",
                y="factor",
                data=factor_importance,
                hue="factor",
                palette="viridis",
            )

            # Add labels and title
            plt.title("Features with maximum variance", fontsize=14)
            plt.xlabel("Importance", fontsize=12)
            plt.ylabel("Factors", fontsize=12)

            # Adjust layout
            plt.tight_layout()
            plt.show()

            # Explore collinearity of features
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
            corr = spearmanr(X_scaled).correlation

            # Ensure the correlation matrix is symmetric
            corr = (corr + corr.T) / 2
            np.fill_diagonal(corr, 1)

            # We convert the correlation matrix to a distance matrix before performing
            # hierarchical clustering using Ward's linkage.
            distance_matrix = 1 - np.abs(corr)
            dist_linkage = hierarchy.ward(squareform(distance_matrix))
            dendro = hierarchy.dendrogram(
                dist_linkage, labels=X.columns.to_list(), ax=ax1, leaf_rotation=90
            )
            dendro_idx = np.arange(0, len(dendro["ivl"]))

            ax2.imshow(corr[dendro["leaves"], :][:, dendro["leaves"]])
            ax2.set_xticks(dendro_idx)
            ax2.set_yticks(dendro_idx)
            ax2.set_xticklabels(dendro["ivl"], rotation="vertical")
            ax2.set_yticklabels(dendro["ivl"])
            fig.suptitle("Colinear features")
            _ = fig.tight_layout()
            plt.show()

            # Feature importance to predict indice
            # Based on RandomForest modeling
            forest = RandomForestRegressor(random_state=42)
            forest.fit(X, y)
            importances = forest.feature_importances_
            std = np.std(
                [tree.feature_importances_ for tree in forest.estimators_], axis=0
            )
            forest_importances = pd.DataFrame(
                data={
                    "feature": np.array(X.columns),
                    "importance": importances,
                    "std": std,
                }
            )

            forest_importances.sort_values(
                by="importance", ascending=False, inplace=True
            )

            plt.figure(figsize=(10, 6))
            sns.barplot(
                x="importance",
                y="feature",
                data=forest_importances,
                hue="feature",
                palette="viridis",
            )
            plt.title("Feature Importances using MDI", fontsize=16)
            plt.xlabel("Mean Decrease in Impurity", fontsize=14)
            plt.ylabel("Features", fontsize=14)
            plt.tight_layout()
            plt.show()

            X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
            forest = RandomForestRegressor(random_state=42)
            forest.fit(X_train, y_train)
            result = permutation_importance(
                forest, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
            )
            forest_importances = pd.DataFrame(
                data={
                    "feature": np.array(X.columns),
                    "importance": result.importances_mean,
                }
            )

            forest_importances.sort_values(
                by="importance", ascending=False, inplace=True
            )

            plt.figure(figsize=(10, 6))
            sns.barplot(
                x="importance",
                y="feature",
                data=forest_importances,
                hue="feature",
                palette="viridis",
            )
            plt.title(
                "Feature importances using permutation on full model (RandomForest regressor)",
                fontsize=16,
            )
            plt.xlabel("Mean accuracy decrease", fontsize=14)
            plt.ylabel("Features", fontsize=14)
            plt.tight_layout()
            plt.show()
