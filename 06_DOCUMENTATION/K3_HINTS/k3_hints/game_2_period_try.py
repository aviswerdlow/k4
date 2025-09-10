#!/usr/bin/env python3
"""
Game 2: Period collision testing.
Tests which periods allow K4 crib indices to land on distinct slots.
Pure Python stdlib only. No AI.
"""

def test_period_collisions(period, phase, crib_indices):
    """
    Test if a given period/phase causes slot collisions for crib indices.
    Returns (has_collision, slot_map)
    """
    slots = {}
    for idx in crib_indices:
        slot = (idx - phase) % period
        if slot in slots:
            # Collision detected
            return True, slots
        slots[slot] = idx
    return False, slots


def main():
    print("K4 Period Collision Testing")
    print("=" * 50)
    print("Testing which periods allow K4 cribs to land on distinct slots")
    print()
    
    # K4 crib positions
    cribs = {
        "EAST": list(range(21, 25)),       # 21-24
        "NORTHEAST": list(range(25, 34)),   # 25-33
        "BERLIN": list(range(63, 69)),      # 63-68
        "CLOCK": list(range(69, 74))        # 69-73
    }
    
    # Flatten all crib indices
    all_crib_indices = []
    for indices in cribs.values():
        all_crib_indices.extend(indices)
    
    print("K4 Crib positions:")
    for name, indices in cribs.items():
        print(f"  {name:10} indices {indices[0]}-{indices[-1]}")
    print()
    
    # Test candidate periods
    test_periods = [11, 13, 17, 19]
    
    # For each class, we need to test separately
    # Using the class function from game 1
    classes = {c: [] for c in range(6)}
    for idx in all_crib_indices:
        cls = ((idx % 2) * 3) + (idx % 3)
        classes[cls].append(idx)
    
    print("Crib indices by class:")
    for c in range(6):
        if classes[c]:
            print(f"  Class {c}: {classes[c]}")
    print()
    
    print("Collision Table (testing phase=0 for simplicity):")
    print("-" * 50)
    print("Period | Class 0 | Class 1 | Class 2 | Class 3 | Class 4 | Class 5")
    print("-" * 70)
    
    results = {}
    for period in test_periods:
        row = f"{period:6} |"
        all_good = True
        
        for c in range(6):
            if not classes[c]:
                row += "   N/A   |"
                continue
                
            has_collision, _ = test_period_collisions(period, 0, classes[c])
            if has_collision:
                row += "  CLASH  |"
                all_good = False
            else:
                row += "   OK    |"
        
        results[period] = all_good
        print(row)
    
    print()
    
    # Find smallest working period
    working_periods = [p for p in test_periods if results[p]]
    if working_periods:
        best = min(working_periods)
        print(f"Smallest period with no collisions: {best}")
        print("We pick this for all classes under Option-A.")
    else:
        print("No single period works for all classes.")
        print("May need different L per class.")
    
    # Show detailed slots for L=17
    if 17 in working_periods:
        print("\nDetailed slot assignment for L=17, phase=0:")
        print("-" * 50)
        for c in range(6):
            if classes[c]:
                _, slots = test_period_collisions(17, 0, classes[c])
                print(f"Class {c}:")
                for slot, idx in sorted(slots.items()):
                    crib_name = ""
                    for name, indices in cribs.items():
                        if idx in indices:
                            crib_name = f" ({name})"
                            break
                    print(f"  Slot {slot:2}: index {idx:2}{crib_name}")


if __name__ == "__main__":
    main()