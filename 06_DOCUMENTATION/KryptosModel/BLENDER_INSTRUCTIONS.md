# Instructions for Running Kryptos Letter Export in Blender

## Prerequisites
- Blender 2.79 or newer (including 3.x)
- A Blender file (.blend) containing the Kryptos model with letter objects

## Setup Instructions

### Method 1: Run from Blender's Text Editor (Recommended)

1. **Open Blender** with your Kryptos model file

2. **Open the Text Editor**:
   - Switch to the "Scripting" workspace tab at the top
   - Or split a window and change it to "Text Editor"

3. **Load the Script**:
   - In the Text Editor, click "Open" (folder icon)
   - Navigate to: `/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/06_DOCUMENTATION/KryptosModel/`
   - Select `export_kryptos_letters.py`

4. **Run the Script**:
   - Click "Run Script" button in the Text Editor
   - Check the console for output messages

### Method 2: Run from Blender's Python Console

1. **Open Blender** with your Kryptos model

2. **Open Python Console**:
   - Switch to "Scripting" workspace
   - Find the Python Console panel

3. **Execute the Script**:
   ```python
   import sys
   sys.path.append('/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/06_DOCUMENTATION/KryptosModel/')
   import export_kryptos_letters
   export_kryptos_letters.main()
   ```

### Method 3: Run from Command Line

```bash
# Navigate to the KryptosModel directory
cd "/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/06_DOCUMENTATION/KryptosModel/"

# Run Blender in background mode with your .blend file
blender your_kryptos_model.blend --background --python export_kryptos_letters.py
```

## Configuration

Before running, you may need to adjust these settings in the script:

### Object Name Patterns
The script looks for objects with names containing:
- "Kryptos"
- "Screen"
- "Panel"
- "Letter"
- "K4"

Adjust `INCLUDE_NAME_SUBSTRINGS` if your objects use different naming.

### Letter Detection
The script identifies letters by:
1. Object name patterns (e.g., "K4_C_063", "Letter_E_21")
2. Custom property named "char"
3. Child text objects

### Reading Order
- `READING_MODE = "serpentine"`: Alternates left-to-right and right-to-left by row
- `READING_MODE = "left_to_right"`: Always left-to-right

## Output Files

The script will create three files in the same directory as your .blend file:

1. **kryptos_letters.csv**: All letters with full data
   - Columns: idx, char, obj_name, collection, x, y, z, nx, ny, nz, sx, sy, sz

2. **kryptos_letters.json**: Same data in JSON format

3. **k4_line.csv**: Last 97 letters (presumed K4)
   - Columns: k4_idx, char, obj_name, x, y, z

## Troubleshooting

### No Letters Found
If the script reports "No letters found", check:
- Object names contain one of the required substrings
- Objects are of type MESH or FONT
- Letter characters are identifiable (A-Z or ?)

### Incorrect Letter Order
- Adjust `ROW_TOL` if letters aren't grouping into rows correctly
- Try switching between "serpentine" and "left_to_right" modes

### Missing Blender Module Error
If running outside Blender:
```python
# This script MUST run inside Blender's Python environment
# The 'bpy' module is only available within Blender
```

## Verifying Results

After export, check:
1. Total letter count matches expectations
2. K4 section has exactly 97 letters
3. Letter order matches the physical sculpture

## Example Usage for K4 Analysis

Once exported, use the CSV files to:
- Map 3D positions to cipher positions
- Analyze spatial patterns in the sculpture
- Correlate physical layout with cryptographic structure

The exported data provides exact coordinates and orientations that may reveal:
- Hidden geometric patterns
- Alignment with architectural features
- Spatial encoding schemes