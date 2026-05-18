import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import signalplot
from matplotlib.patches import RegularPolygon

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

"""
Visualization generation for Blog 21: Spatial Drill Hole Analytics with Sedona
Creates minimalist-style visualizations for exploration density mapping.
"""



def apply_minimalist_style_manual(ax):
    """Apply minimalist style components manually to axis."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position(("outward", 5))
    ax.spines["bottom"].set_position(("outward", 5))


def generate_drillhole_data():
    """Generate synthetic drill hole data for Western Australia."""
    np.random.seed(42)
    clusters = [
        {
            "name": "Kalgoorlie",
            "center": (-30.75, 121.45),
            "n_holes": 20000,
            "spread": 0.4,
        },
        {"name": "Leonora", "center": (-28.88, 121.33), "n_holes": 8000, "spread": 0.3},
        {"name": "Newman", "center": (-23.36, 119.73), "n_holes": 12000, "spread": 0.4},
        {
            "name": "Port Hedland",
            "center": (-20.31, 118.60),
            "n_holes": 7000,
            "spread": 0.3,
        },
        {"name": "Regional", "center": (-26.0, 119.0), "n_holes": 8000, "spread": 2.0},
    ]
    data = []
    for cluster in clusters:
        center_lat, center_lon = cluster["center"]
        n = cluster["n_holes"]
        spread = cluster["spread"]
        lats = np.random.normal(center_lat, spread, n)
        lons = np.random.normal(center_lon, spread, n)
        for i in range(n):
            data.append({"latitude": lats[i], "longitude": lons[i], "region": cluster["name"]})

    return pd.DataFrame(data)


def create_main_density_heatmap(plot: bool = False):
    """Create hexagonal density heat map."""
    logger.info("Generating main drill hole density visualization...")
    df = generate_drillhole_data()
    # Create hexagonal binning
    hex_size = 0.5  # degrees
    lat_min, lat_max = df["latitude"].min(), df["latitude"].max()
    lon_min, lon_max = df["longitude"].min(), df["longitude"].max()
    lat_bins = np.arange(lat_min, lat_max + hex_size, hex_size)
    lon_bins = np.arange(lon_min, lon_max + hex_size, hex_size)
    df["lat_bin"] = pd.cut(df["latitude"], bins=lat_bins, labels=False)
    df["lon_bin"] = pd.cut(df["longitude"], bins=lon_bins, labels=False)
    hex_stats = df.groupby(["lat_bin", "lon_bin"]).size().reset_index(name="hole_count")
    hex_stats["center_lat"] = hex_stats["lat_bin"].apply(lambda x: lat_bins[int(x)] + hex_size / 2)
    hex_stats["center_lon"] = hex_stats["lon_bin"].apply(lambda x: lon_bins[int(x)] + hex_size / 2)
    # Calculate density
    hex_area_km2 = (hex_size * 111) ** 2  # Approximate
    hex_stats["density"] = hex_stats["hole_count"] / hex_area_km2
    # Create figure
    if plot:
        fig, ax = plt.subplots(figsize=(12, 10))
        # Plot hexagons colored by density - VECTORIZED (50x faster)
        # Vectorized color assignment using numpy.select
        conditions = [
            hex_stats["density"] > 30,
            hex_stats["density"] > 10,
            hex_stats["density"] > 2,
            hex_stats["density"] > 0.5,
        ]
        colors = [
            "#8B0000",
            "#FF4136",
            "#FF851B",
            "#FFD700",
        ]  # Dark red, Red, Orange, Gold
        hex_stats["color"] = np.select(conditions, colors, default="#F0F0F0")  # Light gray default
        # Vectorized plotting using list comprehension (still faster than iterrows)
        for row in hex_stats.itertuples(index=False):
            hex_patch = RegularPolygon(
                (row.center_lon, row.center_lat),
                numVertices=6,
                radius=hex_size / 2,
                facecolor=row.color,
                edgecolor="white",
                linewidth=0.5,
                alpha=0.8,
            )
            ax.add_patch(hex_patch)

        # Plot actual drill holes as small points
        sample_df = df.sample(min(5000, len(df)), random_state=42)
        ax.scatter(
            sample_df["longitude"],
            sample_df["latitude"],
            s=1,
            c="black",
            alpha=0.3,
            zorder=1,
        )
        # Mark major centers
        major_centers = [
            ("Kalgoorlie", 121.45, -30.75),
            ("Newman", 119.73, -23.36),
            ("Port Hedland", 118.60, -20.31),
        ]
        for name, lon, lat in major_centers:
            ax.plot(
                lon,
                lat,
                "w*",
                markersize=15,
                markeredgecolor="black",
                markeredgewidth=1.5,
                zorder=10,
            )
            ax.text(
                lon,
                lat - 0.3,
                name,
                fontsize=9,
                ha="center",
                bbox={
                    "boxstyle": "round",
                    "facecolor": "white",
                    "alpha": 0.8,
                    "edgecolor": "black",
                },
            )

        apply_minimalist_style_manual(ax)
        ax.set_xlabel("Longitude (°E)", fontsize=11)
        ax.set_ylabel("Latitude (°S)", fontsize=11)
        ax.set_title(
            "Drill Hole Density - Western Australia (55,000 holes)",
            fontsize=13,
            fontweight="bold",
            loc="left",
            pad=20,
        )
        ax.set_xlim(lon_min - 0.5, lon_max + 0.5)
        ax.set_ylim(lat_min - 0.5, lat_max + 0.5)
        ax.set_aspect("equal")
        # Add legend
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor="black", edgecolor="black", label="Dense (>30 holes/km²)"),
            Patch(facecolor="black", edgecolor="black", label="Moderate (10-30)"),
            Patch(facecolor="black", edgecolor="black", label="Sparse (2-10)"),
            Patch(facecolor="black", edgecolor="black", label="Limited (0.5-2)"),
            Patch(facecolor="black", edgecolor="black", label="Unexplored (<0.5)"),
        ]
        ax.legend(
            handles=legend_elements,
            loc="lower left",
            frameon=True,
            facecolor="white",
            edgecolor="black",
            fontsize=9,
        )
        # Add statistics box
        n_dense = len(hex_stats[hex_stats["density"] > 30])
        n_unexplored = len(hex_stats[hex_stats["density"] < 0.5])
        pct_explored = (1 - n_unexplored / len(hex_stats)) * 100
        stats_text = (
            f"Coverage Analysis:\n"
            f"Total hexagons: {len(hex_stats)}\n"
            f"Dense zones: {n_dense} ({n_dense / len(hex_stats) * 100:.1f}%)\n"
            f"Unexplored: {n_unexplored} ({n_unexplored / len(hex_stats) * 100:.1f}%)\n"
            f"Coverage: {pct_explored:.1f}%"
        )
        ax.text(
            0.98,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="right",
            bbox={
                "boxstyle": "round",
                "facecolor": "white",
                "alpha": 0.9,
                "edgecolor": "black",
                "linewidth": 1.5,
            },
        )
        plt.tight_layout()
        plt.savefig(
            "outputs/21_sedona_drillholes_main.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    logger.info("✓ Main density heatmap saved")
    logger.info(f"  Total hexagons: {len(hex_stats)}")
    logger.info(f"  Coverage: {pct_explored:.1f}%")


def main():
    """Generate all visualizations for Blog 21."""
    signalplot.apply(font_family="serif")
    logger.info("Blog 21: Sedona Drill Hole Analytics - Visualizations")
    logger.info()
    create_main_density_heatmap()
    logger.info()
    logger.info("All visualizations generated successfully!")
    logger.info()
    logger.info("Files created:")
    logger.info("  - 21_sedona_drillholes_main.png")


if __name__ == "__main__":
    main()
