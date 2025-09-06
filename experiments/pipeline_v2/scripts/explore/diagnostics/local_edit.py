#!/usr/bin/env python3
"""
Perform local edits on near-miss candidates.
Try legal point edits to see if any can cross delta thresholds.
"""

import json
import csv
import random
import string
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# Add pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.explore.run_family import ExplorePipeline


class LocalEditor:
    """Perform legal edits on heads."""
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        self.pipeline = ExplorePipeline(seed)
        
        # Corridor positions to preserve
        self.corridor_masks = [
            (21, 25),    # EAST
            (25, 34),    # NORTHEAST
            (63, 74)     # BERLINCLOCK
        ]
        
        # Character classes for swaps
        self.vowels = set("AEIOU")
        self.consonants = set("BCDFGHJKLMNPQRSTVWXYZ")
        
        # Function words for substitution
        self.function_words = ["THE", "AND", "OF", "TO", "IN", "IS", "IT", "BE", "AS", "AT"]
    
    def is_editable(self, pos: int) -> bool:
        """Check if position is editable (not in corridor)."""
        for start, end in self.corridor_masks:
            if start <= pos < end:
                return False
        return True
    
    def generate_edits(self, text: str, max_edits: int = 250) -> List[Dict]:
        """
        Generate legal edits of the text.
        
        Args:
            text: Original head text
            max_edits: Maximum number of edits to generate
        
        Returns:
            List of edited texts with descriptions
        """
        edits = []
        text_list = list(text)
        
        # Type 1: Single character swaps within same class
        for _ in range(max_edits // 3):
            pos = random.randint(0, len(text) - 1)
            
            if self.is_editable(pos):
                char = text_list[pos]
                
                if char in self.vowels:
                    # Swap with another vowel
                    new_char = random.choice(list(self.vowels - {char}))
                elif char in self.consonants:
                    # Swap with another consonant
                    new_char = random.choice(list(self.consonants - {char}))
                else:
                    continue
                
                edited = text_list.copy()
                edited[pos] = new_char
                
                edits.append({
                    "text": ''.join(edited),
                    "edit_type": "char_swap",
                    "position": pos,
                    "change": f"{char}->{new_char}"
                })
        
        # Type 2: Function word substitutions
        for _ in range(max_edits // 3):
            # Find potential function word positions
            word_len = random.choice([2, 3])
            pos = random.randint(0, len(text) - word_len)
            
            if all(self.is_editable(pos + i) for i in range(word_len)):
                # Replace with function word
                word = random.choice([w for w in self.function_words if len(w) == word_len])
                
                edited = text_list.copy()
                for i, char in enumerate(word):
                    edited[pos + i] = char
                
                edits.append({
                    "text": ''.join(edited),
                    "edit_type": "function_word",
                    "position": pos,
                    "change": f"insert_{word}"
                })
        
        # Type 3: Tail boundary edits (positions 73-74)
        for _ in range(max_edits // 3):
            if random.random() < 0.5 and self.is_editable(73):
                # Edit position 73
                char_73 = text_list[73]
                new_char = random.choice(list(string.ascii_uppercase) - {char_73})
                
                edited = text_list.copy()
                edited[73] = new_char
                
                edits.append({
                    "text": ''.join(edited),
                    "edit_type": "tail_boundary",
                    "position": 73,
                    "change": f"{char_73}->{new_char}"
                })
            
            if random.random() < 0.5 and self.is_editable(74):
                # Edit position 74
                char_74 = text_list[74]
                new_char = random.choice(list(string.ascii_uppercase) - {char_74})
                
                edited = text_list.copy()
                edited[74] = new_char
                
                edits.append({
                    "text": ''.join(edited),
                    "edit_type": "tail_boundary",
                    "position": 74,
                    "change": f"{char_74}->{new_char}"
                })
        
        # Remove duplicates
        seen = set()
        unique_edits = []
        for edit in edits:
            if edit["text"] not in seen:
                seen.add(edit["text"])
                unique_edits.append(edit)
        
        return unique_edits[:max_edits]
    
    def evaluate_edit(self, original_text: str, edited_text: str) -> Dict:
        """
        Evaluate an edited text against original.
        
        Returns:
            Scoring results and delta improvements
        """
        # Score both
        policies = [
            {"name": "fixed", "window_radius": 0, "typo_budget": 0},
            {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
            {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
        ]
        
        orig_results = self.pipeline.run_anchor_modes(original_text, policies)
        edit_results = self.pipeline.run_anchor_modes(edited_text, policies)
        
        return {
            "original_deltas": {
                "windowed": orig_results["delta_vs_windowed"],
                "shuffled": orig_results["delta_vs_shuffled"]
            },
            "edited_deltas": {
                "windowed": edit_results["delta_vs_windowed"],
                "shuffled": edit_results["delta_vs_shuffled"]
            },
            "improvements": {
                "windowed": edit_results["delta_vs_windowed"] - orig_results["delta_vs_windowed"],
                "shuffled": edit_results["delta_vs_shuffled"] - orig_results["delta_vs_shuffled"]
            },
            "pass_deltas": edit_results["pass_deltas"]
        }


def main():
    """Run local edit search on frontier candidates."""
    print("="*60)
    print("LOCAL EDIT SEARCH")
    print("="*60)
    
    # Load frontier candidates
    frontier_file = Path("experiments/pipeline_v2/runs/2025-01-06-explore-diagnostics/FRONTIER_eps0.10.csv")
    
    if not frontier_file.exists():
        print("No frontier file found. Run mine_frontier.py first.")
        return
    
    # Load top candidates
    candidates = []
    with open(frontier_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)
    
    if not candidates:
        print("No frontier candidates to edit.")
        return
    
    # Process top 50 or all available
    num_to_process = min(50, len(candidates))
    print(f"Processing top {num_to_process} frontier candidates...")
    
    editor = LocalEditor(seed=1337)
    survivors = []
    
    for i, candidate in enumerate(candidates[:num_to_process]):
        if i % 10 == 0:
            print(f"  Processing candidate {i+1}/{num_to_process}...")
        
        # Get original text (need to reload from heads file)
        campaign_id = candidate["campaign"]
        label = candidate["label"]
        
        # Load original head
        heads_dir = Path(f"experiments/pipeline_v2/runs/2025-01-06-explore-ideas-{campaign_id}")
        heads_files = list(heads_dir.glob("heads_*.json"))
        
        if not heads_files:
            continue
        
        with open(heads_files[0]) as f:
            heads_data = json.load(f)
        
        # Find specific head
        original_text = None
        for head in heads_data["heads"]:
            if head["label"] == label:
                original_text = head["text"]
                break
        
        if not original_text:
            continue
        
        # Generate edits
        edits = editor.generate_edits(original_text, max_edits=250)
        
        # Evaluate each edit
        for edit in edits:
            result = editor.evaluate_edit(original_text, edit["text"])
            
            if result["pass_deltas"]:
                # Found a survivor!
                survivors.append({
                    "original_label": f"{campaign_id}/{label}",
                    "edited_text": edit["text"],
                    "edit_type": edit["edit_type"],
                    "edit_description": edit["change"],
                    "original_deltas": result["original_deltas"],
                    "edited_deltas": result["edited_deltas"],
                    "improvements": result["improvements"]
                })
                
                print(f"    ✅ SURVIVOR: {edit['edit_type']} edit improved deltas!")
                print(f"       Windowed: {result['original_deltas']['windowed']:.4f} -> {result['edited_deltas']['windowed']:.4f}")
                print(f"       Shuffled: {result['original_deltas']['shuffled']:.4f} -> {result['edited_deltas']['shuffled']:.4f}")
    
    # Save results
    output_dir = Path("experiments/pipeline_v2/runs/2025-01-06-explore-diagnostics")
    
    if survivors:
        # Save promotion queue
        queue_file = output_dir / "promotion_queue.json"
        with open(queue_file, 'w') as f:
            json.dump({
                "status": "explore_survivor_pending_confirm",
                "survivors": survivors
            }, f, indent=2)
        
        print(f"\n✅ Found {len(survivors)} EXPLORE SURVIVORS!")
        print(f"Saved to {queue_file}")
    else:
        print(f"\n❌ No edits crossed both delta thresholds.")
    
    # Create report
    report_file = output_dir / "LOCAL_EDIT_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# Local Edit Report\n\n")
        f.write(f"**Candidates processed:** {num_to_process}\n")
        f.write(f"**Edits per candidate:** 250\n")
        f.write(f"**Total edits evaluated:** ~{num_to_process * 250}\n\n")
        
        if survivors:
            f.write(f"## ✅ SURVIVORS: {len(survivors)}\n\n")
            
            for i, surv in enumerate(survivors[:10]):  # Show top 10
                f.write(f"### Survivor {i+1}\n\n")
                f.write(f"**Original:** {surv['original_label']}\n")
                f.write(f"**Edit type:** {surv['edit_type']}\n")
                f.write(f"**Change:** {surv['edit_description']}\n\n")
                f.write("**Delta improvements:**\n")
                f.write(f"- Windowed: {surv['original_deltas']['windowed']:.4f} → {surv['edited_deltas']['windowed']:.4f} ")
                f.write(f"(+{surv['improvements']['windowed']:.4f})\n")
                f.write(f"- Shuffled: {surv['original_deltas']['shuffled']:.4f} → {surv['edited_deltas']['shuffled']:.4f} ")
                f.write(f"(+{surv['improvements']['shuffled']:.4f})\n\n")
        else:
            f.write("## Result: NO SURVIVORS\n\n")
            f.write("None of the local edits were able to push candidates over both delta thresholds.\n")
            f.write("This suggests the hypothesis space is fundamentally far from the requirements.\n")
    
    print(f"Report saved to {report_file}")
    
    return survivors


if __name__ == "__main__":
    survivors = main()