# L=17 Unknown Position Map

## Summary
- Known positions (anchors+tail): 47
- Unknown positions: 50

## Files
- `UNKNOWN_MAP.json`: Detailed metadata for each unknown position
- `UNKNOWN_MAP.csv`: Same data in CSV format
- `UNKNOWN_MAP_BY_CLASS.csv`: Count of unknowns per class
- `UNKNOWN_MAP_BY_SLOT.csv`: Distribution by slot
- `UNKNOWN_MAP.txt`: Visual grid of known/unknown
- `UNKNOWN_MAP_SUMMARY.json`: Aggregate statistics

## Key Finding
With L=17's 1-to-1 mapping property, each constrained position determines exactly one position. Therefore, 47 constraints (24 anchors + 23 tail) yield exactly 47 known positions, leaving 50 unknown.
