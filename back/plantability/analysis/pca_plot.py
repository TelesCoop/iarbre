"""
Generate publication-quality visualizations from PCA analysis results.
Creates two illustrations for blog post on plantability factors.

Run pca_analysis.py first to generate the data, then run this script.
"""

import os
import sys
import django
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import random
import json

# Setup Django
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

# Set style for publication-quality figures
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.4)
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "IBM Plex Sans"
plt.rcParams["font.size"] = 11


def load_and_process_data(sample_size=100000):
    """Load data and perform PCA analysis."""
    print("Loading tile data...")

    # Sample tiles
    matching_ids = list(
        Tile.objects.filter(
            details__isnull=False, plantability_normalized_indice__isnull=False
        ).values_list("id", flat=True)
    )

    actual_sample_size = min(sample_size, len(matching_ids))
    sampled_ids = random.sample(matching_ids, actual_sample_size)

    tiles = Tile.objects.filter(id__in=sampled_ids).values(
        "id", "details", "plantability_normalized_indice"
    )

    # Parse into DataFrame
    data_rows = []
    for tile in tiles:
        details = tile["details"]
        details = tile["details"]
        if isinstance(details, str):
            details = json.loads(details)
        if "land_uses" not in details:
            continue

        row = {
            "tile_id": tile["id"],
            "plantability": tile["plantability_normalized_indice"],
        }
        row.update(details["land_uses"])
        data_rows.append(row)

    df = pd.DataFrame(data_rows).fillna(0)
    print(f"Loaded {len(df):,} tiles with {len(df.columns)-2} land use factors")

    # Prepare features
    feature_cols = [col for col in df.columns if col not in ["tile_id", "plantability"]]
    X = df[feature_cols]
    y = df["plantability"]

    # Standardize and run PCA
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)

    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    pc_cols = [f"PC{i+1}" for i in range(pca.n_components_)]
    df_pca = pd.DataFrame(X_pca, columns=pc_cols, index=X_scaled.index)

    loadings = pd.DataFrame(pca.components_.T, columns=pc_cols, index=feature_cols)

    return X, y, df_pca, loadings, pca.explained_variance_ratio_


def create_r2_chart(y, df_pca):
    """
    Create R² predictive power chart.
    """
    print("\nCreating R² predictive power chart...")

    fig, ax = plt.subplots(figsize=(8, 6))

    # Calculate R² for increasing number of PCs
    r2_scores = []
    max_pcs = min(10, df_pca.shape[1])
    for n in range(1, max_pcs + 1):
        pc_subset = df_pca.iloc[:, :n].values
        reg = LinearRegression()
        reg.fit(pc_subset, y)
        r2 = r2_score(y, reg.predict(pc_subset))
        r2_scores.append(r2)

    x_pos_r2 = np.arange(1, len(r2_scores) + 1)
    colors_r2 = [
        "#025400" if i == 1 else "#BF5A16" if i == 0 else "#DDAD14"
        for i in range(len(r2_scores))
    ]

    ax.bar(
        x_pos_r2,
        np.array(r2_scores) * 100,
        color=colors_r2,
        alpha=0.8,
        edgecolor="white",
        linewidth=1,
    )

    ax.set_xlabel("Nombre de composantes", fontsize=11, fontweight="bold")
    ax.set_ylabel("R² - Plantabilité prédite (%)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Pouvoir prédictif des composantes", fontsize=12, fontweight="bold", pad=10
    )
    ax.set_xticks(x_pos_r2)
    ax.set_xticklabels([f"{i}" for i in x_pos_r2])
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Add annotation for PC1+PC2
    if len(r2_scores) >= 2:
        ax.annotate(
            f"PC1+PC2:\n{r2_scores[1]*100:.1f}% de R²",
            xy=(2, r2_scores[1] * 100),
            xytext=(4, r2_scores[1] * 100 - 8),
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#E8F5E9", alpha=0.9),
            arrowprops=dict(arrowstyle="->", color="#025400", lw=2),
        )

    plt.tight_layout()

    # Save
    output_path = Path(__file__).parent / "plantability_r2.png"
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    print(f"✓ Saved: {output_path}")

    return fig


def create_pca_components_chart(loadings, explained_variance):
    """
    Create PCA components loadings chart (PC1 and PC2).
    """
    print("\nCreating PCA components chart...")

    fig = plt.figure(figsize=(16, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], hspace=0.3, wspace=0.5)

    # ============ Subplot 1: PC1 Top Loadings ============
    ax1 = fig.add_subplot(gs[0, 0])

    pc1_loadings = loadings["PC1"].sort_values(key=abs, ascending=False).head(10)
    y_pos1 = np.arange(len(pc1_loadings))
    colors1 = ["#BF5A16" if v < 0 else "#025400" for v in pc1_loadings.values]

    ax1.barh(
        y_pos1,
        pc1_loadings.values,
        color=colors1,
        alpha=0.8,
        edgecolor="white",
        linewidth=0.8,
    )
    ax1.set_yticks(y_pos1)
    ax1.set_yticklabels(pc1_loadings.index, fontsize=10)
    ax1.set_xlabel("Contribution à la composante 1", fontsize=11, fontweight="bold")
    ax1.set_title(
        f"Composante 1: Réseaux urbains \n({explained_variance[0]*100:.1f}% de la variance expliqué)",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    ax1.axvline(x=0, color="black", linewidth=1.5, linestyle="-", alpha=0.4)
    ax1.grid(axis="x", alpha=0.3, linestyle="--")

    # ============ Subplot 2: PC2 Top Loadings ============
    ax2 = fig.add_subplot(gs[0, 1])

    pc2_loadings = loadings["PC2"].sort_values(key=abs, ascending=False).head(10)
    y_pos2 = np.arange(len(pc2_loadings))
    colors2 = ["#BF5A16" if v < 0 else "#025400" for v in pc2_loadings.values]

    ax2.barh(
        y_pos2,
        pc2_loadings.values,
        color=colors2,
        alpha=0.8,
        edgecolor="white",
        linewidth=0.8,
    )
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(pc2_loadings.index, fontsize=10)
    ax2.set_xlabel("Contribution à la composante 2", fontsize=11, fontweight="bold")
    ax2.set_title(
        f"Composante 2: Bâtiments \n ({explained_variance[1]*100:.1f}% de la variance expliqué).",
        fontsize=12,
        fontweight="bold",
        pad=10,
        color="#BF5A16",
    )
    ax2.axvline(x=0, color="black", linewidth=1.5, linestyle="-", alpha=0.4)
    ax2.grid(axis="x", alpha=0.3, linestyle="--")

    # Add overall title
    fig.suptitle(
        "Analyse en Composantes Principales (ACP): Structure des facteurs de plantabilité",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    plt.tight_layout()

    # Save
    output_path = Path(__file__).parent / "plantability_pca_components.png"
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    print(f"✓ Saved: {output_path}")

    return fig


def create_conditional_analysis(X, y):
    """
    Conditional analysis: mean factor values by plantability ranges.
    Shows how factor levels change across different plantability groups.
    """
    print("\nCreating conditional analysis by plantability ranges...")

    # Define plantability ranges
    ranges = {
        "Très faible (0-2)": (0, 2),
        "Faible (2-4)": (2, 4),
        "Moyen (4-6)": (4, 6),
        "Élevé (6-8)": (6, 8),
        "Très élevé (8-10)": (8, 10),
    }

    # For each range, compute mean of each factor
    range_means = {}

    for range_name, (low, high) in ranges.items():
        mask = (y >= low) & (y < high)
        if mask.sum() > 10:  # Need at least 10 samples
            subset = X[mask]
            range_means[range_name] = subset.mean()

    # Create figure with single plot
    fig, ax = plt.subplots(figsize=(16, 8))

    mean_df = pd.DataFrame(range_means)

    # Select top 12 factors with highest mean variance across ranges
    top_factors = [
        "Rsx gaz",
        "Rsx souterrains ERDF",
        "Réseau Fibre",
        "Pistes cyclable",
        "Tracé de bus",
        "Assainissement",
        "Bâtiments",
        "Proximité façade",
        "Signalisation tricolore et lumineuse matériel",
        "Espaces agricoles",
        "Espaces artificialisés",
        "Parcs et jardins publics",
        "Plan eau",
    ]

    mean_subset = mean_df.loc[top_factors]

    x_pos = np.arange(len(top_factors))
    width = 0.15
    colors_ranges = ["#8B0000", "#FF4500", "#FFD700", "#90EE90", "#006400"]

    for idx, (range_name, color) in enumerate(zip(mean_subset.columns, colors_ranges)):
        offset = (idx - 2) * width
        ax.bar(
            x_pos + offset,
            mean_subset[range_name],
            width,
            label=range_name,
            color=color,
            alpha=0.8,
        )

    ax.set_xlabel("Facteurs", fontsize=11, fontweight="bold")
    ax.set_ylabel(
        "Pourcentage d'occupation de la tuile 5x5m.", fontsize=11, fontweight="bold"
    )
    ax.set_title(
        "Pourcentage d'occupation des tuiles par facteurs et par niveau de plantabilité.",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(top_factors, rotation=45, ha="right", fontsize=9)
    ax.legend(loc="upper right", fontsize=10, ncol=2)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()

    # Save
    output_path = Path(__file__).parent / "plantability_conditional_analysis.png"
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    print(f"✓ Saved: {output_path}")

    return fig


def main():
    """Main execution function."""
    print("=" * 80)
    print("GENERATING PLANTABILITY FACTOR VISUALIZATIONS FOR BLOG POST")
    print("=" * 80)

    # Load data and perform analysis
    X, y, df_pca, loadings, explained_variance = load_and_process_data()

    # Generate visualizations
    print("\n" + "=" * 80)
    print("CREATING ILLUSTRATIONS")
    print("=" * 80)

    # Plot 1: R² predictive power
    create_r2_chart(y, df_pca)
    plt.close()

    # Plot 2: PCA components loadings
    create_pca_components_chart(loadings, explained_variance)
    plt.close()

    # Plot 3: Conditional analysis by plantability ranges
    create_conditional_analysis(X, y)
    plt.close()

    print("\n" + "=" * 80)
    print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 80)
    print("\nOutput files:")
    print("  1. plantability_r2.png - R² predictive power chart")
    print("  2. plantability_pca_components.png - PCA components loadings")
    print("  3. plantability_conditional_analysis.png - Conditional analysis by ranges")


if __name__ == "__main__":
    main()
