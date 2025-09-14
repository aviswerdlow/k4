#!/usr/bin/env python3
"""
Create PT map with K1-K3 plaintext and K4 masked with '?'
"""

import pandas as pd
from pathlib import Path

# Known plaintexts (canonical with typos preserved)
K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSIONDEPARTMENTOFTHEARMYTHEHALLOFTHREE"
K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOTHEYARETHEONESWHOKEEPTHERECORDSFROMTHEPASTTOETELLOURCHILDRENSFUTURETWOHUNDREDANDFOURTEENHOURSGREENWICHTIMESEVENELEVENRETRIEVEEXITPROTOCOL"
K3_PT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINGBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"

# Load CT map
ROOT = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/06_DOCUMENTATION/KryptosModel")
ct_map = pd.read_csv(ROOT / "04_full_sculpture/letters_map_full_ct.csv")

# Create PT map
pt_map = ct_map.copy()

# Replace K1-K3 with plaintext
k1_mask = pt_map['section'] == 'K1'
k2_mask = pt_map['section'] == 'K2'
k3_mask = pt_map['section'] == 'K3'
k4_mask = pt_map['section'] == 'K4'

# Assign plaintext by section index
for i, row in pt_map[k1_mask].iterrows():
    idx = int(row['index_in_section'])
    if idx < len(K1_PT):
        pt_map.at[i, 'char'] = K1_PT[idx]

for i, row in pt_map[k2_mask].iterrows():
    idx = int(row['index_in_section'])
    if idx < len(K2_PT):
        pt_map.at[i, 'char'] = K2_PT[idx]

for i, row in pt_map[k3_mask].iterrows():
    idx = int(row['index_in_section'])
    if idx < len(K3_PT):
        pt_map.at[i, 'char'] = K3_PT[idx]

# Mask K4 with '?'
pt_map.loc[k4_mask, 'char'] = '?'

# Save
output_path = ROOT / "04_full_sculpture/letters_map_full.csv"
pt_map.to_csv(output_path, index=False)

# Verify
print("PT Map Created:")
print(f"  Output: {output_path}")
print("\nSection verification:")
for section in ['K1', 'K2', 'K3', 'K4']:
    section_data = pt_map[pt_map['section'] == section]
    n = len(section_data)
    sample = ''.join(section_data.head(20)['char'].values)
    print(f"  {section}: {n} chars")
    print(f"    First 20: {sample}")

# Check for proper masking
k4_chars = pt_map[k4_mask]['char'].unique()
print(f"\nK4 masking: {k4_chars} (should be only '?')")

print("\n✓ PT map created successfully!")