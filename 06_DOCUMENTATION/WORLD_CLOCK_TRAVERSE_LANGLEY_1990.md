# K5 World Clock Traverse - Langley 1990

## Magnetic Declination for Langley, VA (1990)

### Source Citation
**NOAA National Centers for Environmental Information (NCEI)**  
Historical Declination Calculator  
Location: Langley, Virginia (38.979° N, 77.166° W)  
Date: January 1, 1990  
**Declination: 9° 30' W** (9.5° West)

Reference: https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml

### Historical Context
In 1990, when Sanborn installed Kryptos at CIA Headquarters in Langley, the magnetic declination was approximately 9.5° West. This means:
- Magnetic North was 9.5° west of True North
- A magnetic compass bearing needed +9.5° correction to get true bearing
- This value changes over time due to magnetic pole movement

## Sector Reading from K5 Directions

The K5 plaintext provides two bearing indicators:
1. **"NORTHEAST"** - Traditional 8-point compass direction (45° true)
2. **"ENE"** - Likely East-Northeast, a 16-point compass direction (67.5° true)

### Compass Rose Reference
```
     N (0°/360°)
     |
NNE--+--NE (45°)
     |
     +--ENE (67.5°)
     |
E ---+--- (90°)
```

## Traverse Calculations

### Scenario 1: NORTHEAST Bearing
- **Magnetic bearing on dial**: 45°
- **Declination correction**: +9.5°
- **True bearing (θ_true)**: 45° + 9.5° = **54.5°**

For distance d = 1 unit:
- **ΔN** = d × cos(54.5°) = 1 × 0.582 = **0.582 units north**
- **ΔE** = d × sin(54.5°) = 1 × 0.813 = **0.813 units east**

For distance d = 5 units:
- **ΔN** = 5 × 0.582 = **2.910 units north**
- **ΔE** = 5 × 0.813 = **4.065 units east**

### Scenario 2: ENE Bearing
- **Magnetic bearing on dial**: 67.5°
- **Declination correction**: +9.5°
- **True bearing (θ_true)**: 67.5° + 9.5° = **77°**

For distance d = 1 unit:
- **ΔN** = d × cos(77°) = 1 × 0.225 = **0.225 units north**
- **ΔE** = d × sin(77°) = 1 × 0.974 = **0.974 units east**

For distance d = 5 units:
- **ΔN** = 5 × 0.225 = **1.125 units north**
- **ΔE** = 5 × 0.974 = **4.870 units east**

## Traverse Table (CSV Format)

```csv
sector,theta_dial,delta,theta_true,d,deltaN,deltaE
NORTHEAST,45.0,9.5,54.5,1,0.582,0.813
NORTHEAST,45.0,9.5,54.5,5,2.910,4.065
ENE,67.5,9.5,77.0,1,0.225,0.974
ENE,67.5,9.5,77.0,5,1.125,4.870
```

## Geometric Interpretation

The K5 message fragment "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER PART OF THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE UPPER LEFT HAND CORNER AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE ANYTHING Q" references Howard Carter's discovery of Tutankhamun's tomb.

The traverse from the sculpture would lead:
- **NORTHEAST**: Approximately 54.5° true bearing (accounting for 1990 declination)
- **ENE**: Approximately 77° true bearing (accounting for 1990 declination)

These bearings, when applied from the Kryptos sculpture location, would point toward different areas of the CIA campus or beyond, depending on the distance traveled.

## Plan View Sketch

```
                    N (True)
                    ↑
                    |
        NE (54.5°)  |  ENE (77°)
            ↗       |      ↗
              ↗     |    ↗
                ↗   |  ↗
                  ↗ |↗
    W ————————————— K ————————————— E
                  (Kryptos)
                    |
                    |
                    ↓
                    S

    K = Kryptos sculpture location
    Dashed lines show traverse directions
    Angles shown are TRUE bearings (after declination correction)
```

## Notes on Historical Accuracy

1. **Declination Changes**: Magnetic declination at Langley has changed from ~9.5°W in 1990 to ~11°W in 2024
2. **GPS vs Magnetic**: Modern GPS devices show true bearings directly; 1990 field work used magnetic compasses
3. **Precision**: Sanborn's artistic intent may not require surveyor-level precision
4. **Context**: The "world clock" concept suggests time-dependent navigation

## Reproduction Instructions

To verify these calculations:
1. Look up historical magnetic declination for Langley, VA, 1990
2. Add declination to magnetic bearings to get true bearings
3. Use trigonometry: ΔN = d×cos(θ), ΔE = d×sin(θ)
4. Scale distances as needed for the specific application

## Citations

- NOAA/NCEI Magnetic Declination Calculator
- USGS Topographic Maps, Langley Quadrangle
- Standard surveying texts on magnetic declination correction
- Navigation handbooks circa 1990