#!/bin/bash
# Script to run Blender export and analyze spatial patterns

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BLEND_FILE="$SCRIPT_DIR/KryptosSculpture3DPrintable.Public.blend"
EXPORT_SCRIPT="$SCRIPT_DIR/export_kryptos_letters.py"
ANALYZE_SCRIPT="$SCRIPT_DIR/analyze_spatial_patterns.py"

echo "=========================================="
echo "Kryptos 3D Spatial Analysis Pipeline"
echo "=========================================="

# Check if Blender is installed
if command -v blender &> /dev/null; then
    echo "✓ Blender found"
    
    echo ""
    echo "Step 1: Running Blender export..."
    echo "-----------------------------------------"
    
    # Run Blender in background mode
    blender "$BLEND_FILE" --background --python "$EXPORT_SCRIPT"
    
    echo ""
    echo "Step 2: Analyzing spatial patterns..."
    echo "-----------------------------------------"
    
    # Run spatial analysis
    python3 "$ANALYZE_SCRIPT"
    
else
    echo "⚠️  Blender not found in PATH"
    echo ""
    echo "Option 1: Install Blender from https://www.blender.org"
    echo "Option 2: Open Blender manually and run the export script"
    echo ""
    echo "For now, creating sample data for demonstration..."
    echo "-----------------------------------------"
    
    # Run analysis with sample data
    python3 "$ANALYZE_SCRIPT"
fi

echo ""
echo "=========================================="
echo "Analysis complete!"
echo "Check spatial_analysis_report.txt for results"
echo "=========================================="