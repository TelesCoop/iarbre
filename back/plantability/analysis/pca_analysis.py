"""Analysis which factors influence mostly on the plantability index"""

import os
import sys
import json
import django
import numpy as np
import pandas as pd
import random
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iarbre_data.settings")
django.setup()


def get_tile_model():
    """Avoid E402 from flake8"""
    from iarbre_data.models import Tile

    return Tile


Tile = get_tile_model()


def extract_land_use_data(sample_size: int = 10000) -> list[dict]:
    """Extract a random sample of tiles.

    Args:
        sample_size: Number of random tiles to sample (default: 100,000)

    Returns:
        List of dictionaries containing tile data with land use information
    """

    print("=" * 80)
    print("STEP 1: QUERYING DATABASE")
    print("=" * 80)

    print(
        f"\nSampling {sample_size:,} random tiles with land use and plantability data..."
    )

    print("Fetching matching tile IDs...")
    matching_ids = list(
        Tile.objects.filter(
            details__isnull=False, plantability_normalized_indice__isnull=False
        ).values_list("id", flat=True)
    )

    total_matching = len(matching_ids)
    print(f"Found {total_matching:,} tiles matching criteria")

    actual_sample_size = min(sample_size, total_matching)
    if actual_sample_size < sample_size:
        print(
            f"Warning: Only {actual_sample_size:,} tiles available, using all of them"
        )

    print(f"Randomly sampling {actual_sample_size:,} IDs...")
    sampled_ids = random.sample(matching_ids, actual_sample_size)

    print("Fetching full records for sampled IDs...")
    tiles = Tile.objects.filter(id__in=sampled_ids).values(
        "id", "details", "plantability_normalized_indice"
    )

    tiles_list = list(tiles)
    print(f"Successfully extracted: {len(tiles_list):,} tiles")

    return tiles_list


def parse_land_uses(tiles_data: list[dict]) -> pd.DataFrame:
    """Parse land_uses from details JSON and create a structured DataFrame.

    Args:
        tiles_data: List of dictionaries containing tile data with land use information

    Returns:
        DataFrame containing parsed land use data with plantability indices
    """
    print("\n" + "=" * 80)
    print("STEP 2: PARSING LAND USE DATA")
    print("=" * 80)

    data_rows = []
    parse_errors = 0
    missing_land_uses = 0

    for tile in tiles_data:
        try:
            tile_id = tile["id"]
            plantability = tile["plantability_normalized_indice"]

            details = tile["details"]
            if isinstance(details, str):
                details = json.loads(details)

            if "land_uses" not in details:
                missing_land_uses += 1
                continue

            land_uses = details["land_uses"]

            row = {"tile_id": tile_id, "plantability": plantability}
            row.update(land_uses)
            data_rows.append(row)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(e)
            parse_errors += 1
            continue

    print(f"\nSuccessfully parsed: {len(data_rows):,} tiles")
    print(f"Parse errors: {parse_errors}")
    print(f"Tiles missing land_uses: {missing_land_uses}")

    df = pd.DataFrame(data_rows)

    print(f"\nDataFrame shape: {df.shape}")
    print(
        f"Total columns: {len(df.columns)} (tile_id + plantability + {len(df.columns)-2} land use factors)"
    )
    print(
        f"\nLand use factors found: {sorted([c for c in df.columns if c not in ['tile_id', 'plantability']])}"
    )

    return df


def prepare_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Prepare feature matrix for PCA.

    Args:
        df: DataFrame containing land use data and plantability indices

    Returns:
        Tuple containing:
        - X: DataFrame of land use factors (features)
        - y: Series of plantability indices (target)
        - feature_cols: List of column names for the features
    """
    print("\n" + "=" * 80)
    print("STEP 3: PREPARING FEATURES")
    print("=" * 80)

    # Separate target (plantability) from features (land use factors)
    feature_cols = [col for col in df.columns if col not in ["tile_id", "plantability"]]

    print("\n*** TARGET VARIABLE: plantability ***")
    print(f"\nLand use factors for PCA ({len(feature_cols)} features):")
    for i, col in enumerate(feature_cols, 1):
        print(f"  {i}. {col}")

    X = df[feature_cols].copy()
    y = df["plantability"].copy()

    print("\nLand use factor ranges:")
    for col in X.columns:
        print(f"  {col}: [{X[col].min():.2f}, {X[col].max():.2f}]")

    print(f"\nTarget (plantability) range: [{y.min():.2f}, {y.max():.2f}]")
    print(f"Target mean: {y.mean():.2f}, std: {y.std():.2f}")

    return X, y, feature_cols


def standardize_features(X: pd.DataFrame) -> pd.DataFrame:
    """Standardize features (mean=0, std=1) using sklearn StandardScaler.

    Args:
        X: DataFrame of land use factors to be standardized

    Returns:
        X_scaled: DataFrame with standardized features
    """
    print("\n" + "=" * 80)
    print("STEP 4: STANDARDIZING FEATURES")
    print("=" * 80)

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)

    print("\nOriginal data:")
    print(f"  Mean: {X.mean().mean():.2f}")
    print(f"  Std:  {X.std().mean():.2f}")

    print("\nScaled data:")
    print(f"  Mean: {X_scaled.mean().mean():.6f} (should be ~0)")
    print(f"  Std:  {X_scaled.std().mean():.6f} (should be ~1)")

    return X_scaled


def perform_pca(
    X_scaled: pd.DataFrame, feature_cols: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    """Perform PCA analysis.

    Args:
        X_scaled: DataFrame of standardized land use factors
        feature_cols: List of column names for the features

    Returns:
        Tuple containing:
        - df_pca: DataFrame with principal components
        - loadings: DataFrame of component loadings
        - explained_variance: Array of explained variance ratios
        - cumulative_variance: Array of cumulative explained variance
    """
    print("\n" + "=" * 80)
    print("STEP 5: PERFORMING PCA")
    print("=" * 80)

    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    n_components = pca.n_components_
    print(f"\nNumber of components: {n_components}")

    pc_cols = [f"PC{i+1}" for i in range(n_components)]
    df_pca = pd.DataFrame(X_pca, columns=pc_cols, index=X_scaled.index)

    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)

    print("\nExplained variance by component:")
    for i in range(min(5, n_components)):  # Show first 5
        print(
            f"  PC{i+1}: {explained_variance[i]*100:6.2f}% (cumulative: {cumulative_variance[i]*100:6.2f}%)"
        )

    n_for_90 = np.argmax(cumulative_variance >= 0.90) + 1
    print(f"\nComponents needed for 90% variance: {n_for_90}")

    loadings = pd.DataFrame(pca.components_.T, columns=pc_cols, index=feature_cols)

    print("\nLoadings on first 3 components:")
    print(loadings.iloc[:, : min(3, n_components)].to_string())

    return df_pca, loadings, explained_variance, cumulative_variance


def analyze_relationships(
    X: pd.DataFrame,
    y: pd.Series,
    df_pca: pd.DataFrame,
    loadings: pd.DataFrame,
    explained_variance: np.ndarray,
) -> tuple[dict[str, float], dict[str, float]]:
    """Analyze relationships between land use factors, PCs, and plantability.

    Args:
        X: DataFrame of land use factors
        y: Series of plantability indices
        df_pca: DataFrame of principal components
        loadings: DataFrame of component loadings
        explained_variance: Array of explained variance ratios

    Returns:
        Tuple containing:
        - factor_correlations: Dictionary mapping land use factors to their correlation with plantability
        - pc_correlations: Dictionary mapping principal components to their correlation with plantability
    """
    print("\n" + "=" * 80)
    print("STEP 6: ANALYZING RELATIONSHIPS WITH PLANTABILITY")
    print("=" * 80)

    print("\n" + "=" * 60)
    print("LAND USE FACTORS AND PLANTABILITY CORRELATIONS (sorted by strength)")
    print("=" * 60)

    factor_correlations = {}
    for col in X.columns:
        corr = X[col].corr(y)
        factor_correlations[col] = corr

    sorted_corrs = sorted(
        factor_correlations.items(), key=lambda x: abs(x[1]), reverse=True
    )

    for feat, corr in sorted_corrs:
        direction = "positive" if corr > 0 else "negative"
        strength = (
            "STRONG" if abs(corr) > 0.5 else "moderate" if abs(corr) > 0.3 else "weak"
        )
        print(f"  {feat:30s}: {corr:+.4f}  ({strength:8s} {direction})")

    strongest_factor = sorted_corrs[0]
    print(f"\n>>> STRONGEST: {strongest_factor[0]} with r={strongest_factor[1]:+.4f}")

    print("\n" + "=" * 60)
    print("PRINCIPAL COMPONENTS AND PLANTABILITY CORRELATIONS")
    print("=" * 60)

    pc_correlations = {}
    for i, pc_col in enumerate(df_pca.columns[:5]):  # Show first 5 PCs
        corr = df_pca[pc_col].corr(y)
        pc_correlations[pc_col] = corr
        var_explained = explained_variance[i] * 100
        print(f"  {pc_col:5s} (explains {var_explained:5.2f}% var): {corr:+.4f}")

    print("\n" + "=" * 60)
    print("PC1 INTERPRETATION")
    print("=" * 60)
    print(f"PC1 explains {explained_variance[0]*100:.1f}% of land use variance")
    print(f"PC1 → plantability correlation: {pc_correlations['PC1']:+.4f}")
    print("\nTop contributing land use factors to PC1:")

    pc1_loadings = loadings["PC1"].sort_values(key=abs, ascending=False)
    for feat, loading in pc1_loadings.head(5).items():
        direction = "+" if loading > 0 else "-"
        print(f"  {direction} {feat:30s}: {loading:+.4f}")

    if len(explained_variance) > 1:
        print("\n" + "=" * 60)
        print("PC2 INTERPRETATION")
        print("=" * 60)
        print(f"PC2 explains {explained_variance[1]*100:.1f}% of land use variance")
        print(f"PC2 → plantability correlation: {pc_correlations['PC2']:+.4f}")
        print("\nTop contributing land use factors to PC2:")

        pc2_loadings = loadings["PC2"].sort_values(key=abs, ascending=False)
        for feat, loading in pc2_loadings.head(5).items():
            direction = "+" if loading > 0 else "-"
            print(f"  {direction} {feat:30s}: {loading:+.4f}")

    return factor_correlations, pc_correlations


def print_summary(
    explained_variance: np.ndarray,
    cumulative_variance: np.ndarray,
    factor_correlations: dict[str, float],
    pc_correlations: dict[str, float],
    n_samples: int,
    n_features: int,
) -> None:
    """Print final summary."""
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)

    print("\nDataset:")
    print(f"  Samples: {n_samples:,}")
    print(f"  Land use factors: {n_features}")

    print("\nPCA Results:")
    n_for_90 = np.argmax(cumulative_variance >= 0.90) + 1
    n_for_95 = np.argmax(cumulative_variance >= 0.95) + 1
    print(f"  Total components: {len(explained_variance)}")
    print(f"  Components for 90% variance: {n_for_90}")
    print(f"  Components for 95% variance: {n_for_95}")
    print(f"  PC1 explains: {explained_variance[0]*100:.2f}%")
    print(f"  PC1+PC2 explain: {cumulative_variance[1]*100:.2f}%")

    print("\nPlantability Correlations:")
    strongest = max(factor_correlations.items(), key=lambda x: abs(x[1]))
    print(f"  Strongest land use factor: {strongest[0]} (r={strongest[1]:+.4f})")
    print(f"  PC1 correlation: {pc_correlations['PC1']:+.4f}")

    print("\n" + "=" * 80)
    print("Analysis complete! Run pca_plot.py to generate visualizations.")
    print("=" * 80)


def main() -> None:
    """Main execution function."""
    print("\n" + "=" * 80)
    print("PCA ANALYSIS: Land Use Factors vs Plantability Index")
    print("=" * 80 + "\n")

    try:
        tiles_data = extract_land_use_data()
        if not tiles_data:
            print("\nERROR: No tiles found with land use data.")
            return

        df = parse_land_uses(tiles_data)
        if df.empty:
            print("\nERROR: Failed to parse land use data.")
            return
        # If not data means land use = 0
        df.fillna(0, inplace=True)

        X, y, feature_cols = prepare_features(df)

        X_scaled = standardize_features(X)

        df_pca, loadings, explained_variance, cumulative_variance = perform_pca(
            X_scaled, feature_cols
        )

        factor_correlations, pc_correlations = analyze_relationships(
            X, y, df_pca, loadings, explained_variance
        )

        print_summary(
            explained_variance,
            cumulative_variance,
            factor_correlations,
            pc_correlations,
            len(df),
            len(feature_cols),
        )

    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    main()
