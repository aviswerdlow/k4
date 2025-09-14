#!/usr/bin/env python3
"""
Detect letter centroids from relief bake image
Maps centroids to UV space, then to world coordinates, then to arc length ticks
"""

import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.neighbors import KDTree
import sys

# File paths
RELIEF_PNG = Path("relief_bake.png")
UV_WORLD   = Path("uv_world.csv")
TICKS      = Path("panel_ticks.csv")

print("Letter Centroid Detection")
print("=" * 60)

# Check files exist
for f in [RELIEF_PNG, UV_WORLD, TICKS]:
    if not f.exists():
        print(f"ERROR: {f} not found")
        sys.exit(1)

# 1) Load relief image (UV space)
print(f"Loading {RELIEF_PNG}...")
img = cv2.imread(str(RELIEF_PNG), cv2.IMREAD_UNCHANGED)
if img is None:
    raise RuntimeError(f"Cannot load {RELIEF_PNG}")

# Convert to grayscale if needed
if img.ndim == 3:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Normalize to 0-255
img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
print(f"  Image shape: {img.shape}")
print(f"  Value range: {img.min()} to {img.max()}")

# 2) Denoise & threshold
print("\nApplying preprocessing...")
img_blur = cv2.GaussianBlur(img, (5, 5), 0)

# Adaptive threshold
th = cv2.adaptiveThreshold(
    img_blur, 255, 
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY, 
    31, -10
)

# 3) Morphological cleanup
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)

# Save preprocessed image for debugging
cv2.imwrite("relief_preprocessed.png", th)
print("  Saved preprocessed image: relief_preprocessed.png")

# 4) Connected components
print("\nFinding connected components...")
num, labels, stats, centroids = cv2.connectedComponentsWithStats(th, connectivity=8)
print(f"  Found {num} components")

# Filter by area (adjust threshold as needed)
MIN_AREA = 50  # Minimum pixel area for a valid letter
MAX_AREA = 5000  # Maximum area to exclude large blobs

areas = stats[:, cv2.CC_STAT_AREA]
keep = np.where((areas > MIN_AREA) & (areas < MAX_AREA))[0]

# Skip background (component 0)
keep = keep[keep > 0]

centroids = centroids[keep]
areas_kept = areas[keep]

print(f"  Kept {len(centroids)} components after filtering")
print(f"  Area range: {areas_kept.min():.0f} to {areas_kept.max():.0f} pixels")

# Normalize centroids to UV [0,1]
h, w = img.shape[:2]
u = centroids[:, 0] / w
v = 1.0 - centroids[:, 1] / h  # Flip Y so V increases upward

# 5) Row grouping by V
print("\nGrouping into rows...")
df = pd.DataFrame({"u": u, "v": v, "area": areas_kept})

# Estimate number of rows based on V distribution
v_range = df["v"].max() - df["v"].min()
estimated_row_height = v_range / 10  # Assume ~10 rows
row_tolerance = estimated_row_height * 0.3

# Group into rows
df = df.sort_values("v", ascending=False)  # Top to bottom
rows = []
current_row = []
current_v = df.iloc[0]["v"]

for _, point in df.iterrows():
    if abs(point["v"] - current_v) < row_tolerance:
        current_row.append(point)
    else:
        if current_row:
            rows.append(pd.DataFrame(current_row))
        current_row = [point]
        current_v = point["v"]

if current_row:
    rows.append(pd.DataFrame(current_row))

print(f"  Found {len(rows)} rows")

# 6) Order within rows (serpentine)
print("\nOrdering points...")
ordered = []
idx = 0

for i, row_df in enumerate(rows):
    # Sort by U (left to right)
    row_df = row_df.sort_values("u")
    
    # Reverse even rows for serpentine reading
    if i % 2 == 1:
        row_df = row_df.iloc[::-1]
    
    for _, rec in row_df.iterrows():
        ordered.append({
            "idx": idx,
            "u": float(rec.u),
            "v": float(rec.v),
            "row": i,
            "area": float(rec.area)
        })
        idx += 1

df_ordered = pd.DataFrame(ordered)
print(f"  Ordered {len(df_ordered)} centroids")

# 7) Map UV centroids to world coordinates
print("\nMapping to world coordinates...")
uvw = pd.read_csv(UV_WORLD)
print(f"  Loaded {len(uvw)} UV-world mappings")

# Build KD-tree for nearest neighbor search
tree = KDTree(uvw[["u", "v"]].values)
dist, ind = tree.query(df_ordered[["u", "v"]].values, k=1)

# Get matched world coordinates
matched = uvw.iloc[ind[:, 0]].reset_index(drop=True)
df_ordered["x"] = matched["x"].values
df_ordered["y"] = matched["y"].values
df_ordered["z"] = matched["z"].values
df_ordered["uv_dist"] = dist[:, 0]

# 8) Map to nearest arc length tick
print("\nMapping to arc length ticks...")
ticks = pd.read_csv(TICKS)
print(f"  Loaded {len(ticks)} arc length ticks")

t_xyz = ticks[["x", "y", "z"]].values
tree2 = KDTree(t_xyz)
dist2, ind2 = tree2.query(df_ordered[["x", "y", "z"]].values, k=1)

df_ordered["nearest_tick_idx"] = ticks.iloc[ind2[:, 0]]["idx"].values
df_ordered["s"] = ticks.iloc[ind2[:, 0]]["s"].values
df_ordered["tick_dist"] = dist2[:, 0]

# 9) Save outputs
print("\nSaving results...")
df_ordered.to_csv("letter_centroids_world.csv", index=False)
print(f"  Wrote letter_centroids_world.csv")

df_ordered[["idx", "u", "v", "row"]].to_csv("letter_centroids_uv.csv", index=False)
print(f"  Wrote letter_centroids_uv.csv")

# Save K4 subset (last 97 by arc length)
if len(df_ordered) >= 97:
    df_k4 = df_ordered.nlargest(97, "s").sort_values("s")
    df_k4.to_csv("letter_centroids_k4.csv", index=False)
    print(f"  Wrote letter_centroids_k4.csv (last 97 centroids)")

# Create visualization
print("\nCreating visualization...")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Plot 1: UV space with row colors
ax = axes[0]
scatter = ax.scatter(df_ordered["u"], df_ordered["v"], 
                    c=df_ordered["row"], cmap="tab20", s=10)
ax.set_xlabel("U")
ax.set_ylabel("V")
ax.set_title(f"Centroids in UV Space ({len(df_ordered)} points)")
ax.set_aspect("equal")
plt.colorbar(scatter, ax=ax, label="Row")

# Plot 2: Arc length distribution
ax = axes[1]
ax.scatter(df_ordered["s"], df_ordered["row"], s=5)
ax.set_xlabel("Arc length (m)")
ax.set_ylabel("Row")
ax.set_title("Arc Length Distribution")
ax.grid(True, alpha=0.3)

# Plot 3: Area distribution
ax = axes[2]
ax.hist(df_ordered["area"], bins=30, edgecolor="black")
ax.set_xlabel("Component Area (pixels)")
ax.set_ylabel("Count")
ax.set_title("Area Distribution")

plt.tight_layout()
plt.savefig("letter_centroids_viz.png", dpi=150)
print("  Saved visualization: letter_centroids_viz.png")

# Summary statistics
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total centroids detected: {len(df_ordered)}")
print(f"Number of rows: {df_ordered['row'].nunique()}")
print(f"Arc length range: {df_ordered['s'].min():.3f} to {df_ordered['s'].max():.3f} m")
print(f"Average UV mapping error: {df_ordered['uv_dist'].mean():.6f}")
print(f"Average tick distance: {df_ordered['tick_dist'].mean():.3f} m")

if len(df_ordered) >= 97:
    print(f"\n✓ Success: Found enough centroids for K4 subset (97 needed)")
else:
    print(f"\n⚠ Warning: Only {len(df_ordered)} centroids found (97 needed for K4)")
    print("  Consider adjusting MIN_AREA threshold in the script")

print("\nDone!")
