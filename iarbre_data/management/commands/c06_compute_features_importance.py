import pandas as pd
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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
            tile_data = load_geodataframe_from_db(tiles_queryset, ["id", "indice"]) # Get Tiles and indice values
            tile_data = pd.DataFrame(tile_data.drop(columns='geometry'))
            factor_queryset = TileFactor.objects.filter(
                tile_id__in=tile_data.id
            ) # Get factor values for these tiles
            fields = ["tile_id", "factor", "value"]
            factor_scores = pd.DataFrame(
                [
                    dict(
                        **{field: getattr(data, field) for field in fields}
                    )
                    for data in factor_queryset
                ]
            )
            factor_scores["indice"] = tile_data.indice

            # Compute correlation between factor values and indice (explainability)
            grouped_corr = (
                factor_scores.groupby("factor")
                .apply(lambda group: group["value"].corr(group["indice"]))
                .reset_index(name="pearson_correlation")
            )
            print(grouped_corr)

            # Use PCA to compute features importance (some factors may be correlated)
            # Pivot table to have columns corresponding to each factor
            restructured_df = (
                factor_scores.pivot_table(
                    index="tile_id",  # Rows: unique tile IDs
                    columns="factor",  # Columns: unique factors
                    values="value"  # Values for the factor columns
                )
                .reset_index()  # Convert the tile_id index back to a column
            )

            restructured_df.fillna(0, inplace=True)

            X = restructured_df.drop(columns=["tile_id"])  # Features (factors)

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            pca = PCA()
            pca.fit(X_scaled)

            # Factor importance on PC1
            factor_importance = pd.DataFrame({
                "factor": X.columns,
                "importance": np.abs(pca.components_[0])  # PC1
            })

            factor_importance = factor_importance.sort_values(by="importance", ascending=False)

            # Output the results
            print(factor_importance)

            plt.figure(figsize=(10, 8))
            sns.barplot(x="importance", y="factor", data=factor_importance, palette="viridis")

            # Add labels and title
            plt.title("Feature Importance Based on PCA Decomposition", fontsize=14)
            plt.xlabel("Importance", fontsize=12)
            plt.ylabel("Factors", fontsize=12)

            # Adjust layout
            plt.tight_layout()
            plt.show()
