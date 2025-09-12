#!/usr/bin/env python3
"""
Validate Fork D Result Cards
Ensures all result cards comply with the strict schema
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Tuple, List

MASTER_SEED = 1337

def validate_result_card(card_path: str) -> Tuple[bool, str]:
    """
    Validate a single result card against schema
    
    Returns:
        (valid, message)
    """
    try:
        with open(card_path, 'r') as f:
            card = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Could not read file: {e}"
    
    # Required fields
    required_fields = [
        'mechanism', 'unknowns_before', 'unknowns_after',
        'anchors_preserved', 'new_positions_determined',
        'indices_before', 'indices_after', 'parameters',
        'seed', 'notes'
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in card:
            return False, f"Missing required field: {field}"
    
    # Validate seed
    if card['seed'] != MASTER_SEED:
        return False, f"Invalid seed: {card['seed']} (expected {MASTER_SEED})"
    
    # Validate types
    if not isinstance(card['unknowns_before'], int):
        return False, "unknowns_before must be integer"
    
    if not isinstance(card['unknowns_after'], int):
        return False, "unknowns_after must be integer"
    
    if not isinstance(card['anchors_preserved'], bool):
        return False, "anchors_preserved must be boolean"
    
    if not isinstance(card['new_positions_determined'], list):
        return False, "new_positions_determined must be list"
    
    if not isinstance(card['indices_before'], list):
        return False, "indices_before must be list"
    
    if not isinstance(card['indices_after'], list):
        return False, "indices_after must be list"
    
    # Validate logic
    if card['unknowns_after'] > card['unknowns_before']:
        return False, "unknowns_after cannot exceed unknowns_before"
    
    # If claiming reduction, must list positions
    reduction = card['unknowns_before'] - card['unknowns_after']
    if reduction > 0:
        if len(card['new_positions_determined']) != reduction:
            return False, f"Claims {reduction} reduction but lists {len(card['new_positions_determined'])} positions"
        
        # Check positions are valid indices
        for pos in card['new_positions_determined']:
            if not isinstance(pos, int) or pos < 0 or pos > 96:
                return False, f"Invalid position index: {pos}"
        
        # Check positions were actually unknown before
        for pos in card['new_positions_determined']:
            if pos not in card['indices_before']:
                return False, f"Position {pos} was not in indices_before"
        
        # Check indices_after is correct
        expected_after = [i for i in card['indices_before'] if i not in card['new_positions_determined']]
        if set(card['indices_after']) != set(expected_after):
            return False, "indices_after doesn't match expected remaining unknowns"
    
    # If no reduction, lists should be same
    elif reduction == 0:
        if card['new_positions_determined']:
            return False, "No reduction claimed but new_positions_determined is not empty"
        
        if set(card['indices_before']) != set(card['indices_after']):
            return False, "No reduction but indices_before != indices_after"
    
    # Check parameters
    if not isinstance(card['parameters'], dict):
        return False, "parameters must be dictionary"
    
    # Check mechanism format
    if not isinstance(card['mechanism'], str) or not card['mechanism']:
        return False, "mechanism must be non-empty string"
    
    return True, "Valid"


def validate_directory(directory: str) -> Tuple[int, int, List[str]]:
    """
    Validate all result cards in directory
    
    Returns:
        (valid_count, invalid_count, errors)
    """
    valid_count = 0
    invalid_count = 0
    errors = []
    
    # Find all result JSON files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('result_') and file.endswith('.json'):
                path = os.path.join(root, file)
                valid, msg = validate_result_card(path)
                
                if valid:
                    valid_count += 1
                    print(f"✓ {path}")
                else:
                    invalid_count += 1
                    error_msg = f"✗ {path}: {msg}"
                    errors.append(error_msg)
                    print(error_msg)
    
    return valid_count, invalid_count, errors


def main():
    """Main validation"""
    if len(sys.argv) < 2:
        print("Usage: python validate_result_cards.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        sys.exit(1)
    
    print(f"=== Validating Fork D Result Cards ===")
    print(f"Directory: {directory}")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    valid, invalid, errors = validate_directory(directory)
    
    print(f"\n=== Validation Summary ===")
    print(f"Valid cards: {valid}")
    print(f"Invalid cards: {invalid}")
    
    if invalid > 0:
        print("\nValidation FAILED!")
        print("\nErrors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("\n✓ All result cards validated successfully!")
        
        # Additional checks
        print("\n=== Additional Checks ===")
        
        # Check for any successes
        success_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith('result_') and file.endswith('.json'):
                    path = os.path.join(root, file)
                    with open(path) as f:
                        card = json.load(f)
                    if card['unknowns_after'] < card['unknowns_before'] and card['anchors_preserved']:
                        success_count += 1
                        print(f"🎯 SUCCESS: {card['mechanism']} reduced {card['unknowns_before']} → {card['unknowns_after']}")
        
        if success_count > 0:
            print(f"\n🎉 Found {success_count} successful reductions!")
        else:
            print("\n📊 No reductions found (clean negative results)")


if __name__ == "__main__":
    main()