#!/bin/bash
# Install required packages if needed
pip install opencv-python numpy pandas scikit-learn matplotlib

# Run the detection
python detect_letter_centroids.py

echo "Detection complete. Check outputs:"
echo "  - letter_centroids_world.csv (main output)"
echo "  - letter_centroids_uv.csv (UV coordinates)"
echo "  - letter_centroids_k4.csv (K4 subset, if >= 97 found)"
echo "  - letter_centroids_viz.png (visualization)"
