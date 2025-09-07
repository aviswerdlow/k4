#!/usr/bin/env python3
"""
Gap Composer v2 for v5.2.2-B
Enhanced with per-gap quotas and micro-repair capability.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Function words set
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE', 'FOR'
}

# Action verbs
VERBS = {
    'SET', 'READ', 'SIGHT', 'NOTE', 'OBSERVE', 'FOLLOW',
    'APPLY', 'BRING', 'REDUCE', 'CORRECT', 'TRACE', 'FIND', 
    'MARK', 'SEE'
}

# Per-gap quotas (v5.2.2-B policy)
GAP_QUOTAS = {
    "G1": {"f_words_min": 4, "verbs_min": 1},
    "G2": {"f_words_min": 4, "verbs_min": 1}
}

# Micro-repair synonyms (length-preserving)
SYNONYMS = {
    "SIGN": "MARK",  # 4 chars
    "MARK": "SIGN",  # 4 chars
    "NOTE": "READ",  # 4 chars
    "READ": "NOTE",  # 4 chars
    "DIAL": "GRID",  # 4 chars
    "GRID": "DIAL",  # 4 chars
}

# 3-letter content words that can be replaced with function words
UPGRADEABLE_3 = ["ARC", "DOT", "TOP", "END", "CUT", "GAP", "TIP"]

# Scoring weights
WEIGHTS = {
    "lambda_fw": 1.2,      # Function words (target ≥8)
    "lambda_verbs": 1.0,   # Verbs (target ≥2)
    "lambda_quota": 2.0,   # Per-gap quota compliance
    "lambda_ng": 0.5,      # N-gram score
    "lambda_true": 0.3     # Bonus for TRUE keyword
}

@dataclass
class MicroRepair:
    """A micro-repair operation."""
    gap: str  # "G1" or "G2"
    op_type: str  # "synonym", "upgrade", "transpose"
    position: int
    old_text: str
    new_text: str
    f_word_delta: int
    verb_delta: int

class GapComposerV2:
    """Enhanced gap composer with per-gap quotas and micro-repair."""
    
    def __init__(self, phrasebank_path: Path):
        """Load phrasebank."""
        with open(phrasebank_path, 'r') as f:
            self.phrasebank = json.load(f)
        
        # Filter to only allowed entries
        self.g1_options = [
            entry for entry in self.phrasebank.get("G1_21", [])
            if entry.get("allow", True) and entry["len"] == 21
        ]
        
        self.g2_options = [
            entry for entry in self.phrasebank.get("G2_29", [])
            if entry.get("allow", True) and entry["len"] == 29
        ]
        
        print(f"Gap Composer v2 loaded: {len(self.g1_options)} G1, {len(self.g2_options)} G2 options")
    
    def count_gap_metrics(self, text: str) -> Tuple[int, int]:
        """Count function words and verbs in gap text."""
        words = text.upper().split()
        f_count = sum(1 for w in words if w in FUNCTION_WORDS)
        v_count = sum(1 for w in words if w in VERBS)
        return f_count, v_count
    
    def check_per_gap_quotas(self, g1: Dict, g2: Dict) -> Dict[str, bool]:
        """Check if per-gap quotas are met."""
        return {
            "G1_f": g1["f_count"] >= GAP_QUOTAS["G1"]["f_words_min"],
            "G1_v": g1["v_count"] >= GAP_QUOTAS["G1"]["verbs_min"],
            "G2_f": g2["f_count"] >= GAP_QUOTAS["G2"]["f_words_min"],
            "G2_v": g2["v_count"] >= GAP_QUOTAS["G2"]["verbs_min"],
            "all": (g1["f_count"] >= GAP_QUOTAS["G1"]["f_words_min"] and
                   g2["f_count"] >= GAP_QUOTAS["G2"]["f_words_min"] and
                   g1["v_count"] + g2["v_count"] >= 2)
        }
    
    def suggest_micro_repairs(self, gap_text: str, gap_name: str) -> List[MicroRepair]:
        """Suggest micro-repair operations for a gap."""
        repairs = []
        words = gap_text.upper().split()
        
        # Current metrics
        f_count, v_count = self.count_gap_metrics(gap_text)
        quota = GAP_QUOTAS[gap_name]
        
        # Only suggest repairs if below quota
        if f_count >= quota["f_words_min"] and v_count >= quota["verbs_min"]:
            return repairs
        
        # 1. Synonym swaps (length-preserving)
        for i, word in enumerate(words):
            if word in SYNONYMS:
                new_word = SYNONYMS[word]
                new_text = ' '.join(words[:i] + [new_word] + words[i+1:])
                new_f, new_v = self.count_gap_metrics(new_text)
                
                if new_f > f_count or new_v > v_count:
                    repairs.append(MicroRepair(
                        gap=gap_name,
                        op_type="synonym",
                        position=i,
                        old_text=word,
                        new_text=new_word,
                        f_word_delta=new_f - f_count,
                        verb_delta=new_v - v_count
                    ))
        
        # 2. Function word upgrades (3-letter → THE/AND/FOR)
        for i, word in enumerate(words):
            if len(word) == 3 and word in UPGRADEABLE_3:
                for fw in ["THE", "AND", "FOR"]:
                    new_text = ' '.join(words[:i] + [fw] + words[i+1:])
                    new_f, new_v = self.count_gap_metrics(new_text)
                    
                    if new_f > f_count:
                        repairs.append(MicroRepair(
                            gap=gap_name,
                            op_type="upgrade",
                            position=i,
                            old_text=word,
                            new_text=fw,
                            f_word_delta=new_f - f_count,
                            verb_delta=new_v - v_count
                        ))
        
        # Sort by effectiveness (f_word_delta + verb_delta)
        repairs.sort(key=lambda r: r.f_word_delta + r.verb_delta, reverse=True)
        
        # Return top 2 options (budget constraint)
        return repairs[:2]
    
    def apply_micro_repairs(self, g1: Dict, g2: Dict, max_ops: int = 4) -> Tuple[Dict, Dict, List[MicroRepair]]:
        """Apply micro-repairs to meet per-gap quotas."""
        applied = []
        g1_text = g1["text"]
        g2_text = g2["text"]
        
        # Check initial quotas
        quotas = self.check_per_gap_quotas(g1, g2)
        
        if quotas["all"]:
            return g1, g2, applied  # Already meets quotas
        
        # Get repair suggestions
        g1_repairs = self.suggest_micro_repairs(g1_text, "G1") if not quotas["G1_f"] else []
        g2_repairs = self.suggest_micro_repairs(g2_text, "G2") if not quotas["G2_f"] else []
        
        # Apply repairs (up to 2 per gap, 4 total)
        ops_count = 0
        
        # G1 repairs
        for repair in g1_repairs[:2]:
            if ops_count >= max_ops:
                break
            
            words = g1_text.split()
            if repair.position < len(words):
                words[repair.position] = repair.new_text
                g1_text = ' '.join(words)
                applied.append(repair)
                ops_count += 1
        
        # G2 repairs
        for repair in g2_repairs[:2]:
            if ops_count >= max_ops:
                break
            
            words = g2_text.split()
            if repair.position < len(words):
                words[repair.position] = repair.new_text
                g2_text = ' '.join(words)
                applied.append(repair)
                ops_count += 1
        
        # Update metrics
        g1_f, g1_v = self.count_gap_metrics(g1_text)
        g2_f, g2_v = self.count_gap_metrics(g2_text)
        
        g1_updated = {**g1, "text": g1_text, "f_count": g1_f, "v_count": g1_v}
        g2_updated = {**g2, "text": g2_text, "f_count": g2_f, "v_count": g2_v}
        
        return g1_updated, g2_updated, applied
    
    def score_combination_v2(self, g1: Dict, g2: Dict) -> float:
        """Score with per-gap quota awareness."""
        
        # Total metrics
        total_f = g1["f_count"] + g2["f_count"]
        total_v = g1["v_count"] + g2["v_count"]
        
        # Per-gap quota compliance
        quotas = self.check_per_gap_quotas(g1, g2)
        quota_score = sum([
            1.0 if quotas["G1_f"] else 0.0,
            1.0 if quotas["G1_v"] else 0.0,
            1.0 if quotas["G2_f"] else 0.0,
            1.0 if quotas["G2_v"] else 0.0
        ])
        
        # Mock n-gram score
        ngram_score = 0.7 + random.random() * 0.3
        
        # Check for TRUE keyword
        has_true = "TRUE" in g1["text"] or "TRUE" in g2["text"]
        
        # Calculate score
        score = (
            WEIGHTS["lambda_fw"] * total_f +
            WEIGHTS["lambda_verbs"] * total_v +
            WEIGHTS["lambda_quota"] * quota_score +
            WEIGHTS["lambda_ng"] * ngram_score +
            WEIGHTS["lambda_true"] * (1.0 if has_true else 0.0)
        )
        
        return score
    
    def select_best_combination_v2(self, seed: int, enable_repair: bool = True) -> Tuple[Dict, Dict, Dict]:
        """
        Select best combination with micro-repair support.
        
        Returns: (g1, g2, metrics)
        """
        random.seed(seed)
        
        # Sample candidates
        beam_size = 10
        g1_candidates = random.sample(self.g1_options, min(beam_size, len(self.g1_options)))
        g2_candidates = random.sample(self.g2_options, min(beam_size, len(self.g2_options)))
        
        # Find best combination
        best_score = -float('inf')
        best_g1 = None
        best_g2 = None
        best_metrics = None
        best_repairs = []
        
        for g1 in g1_candidates:
            for g2 in g2_candidates:
                # Apply micro-repairs if enabled
                if enable_repair:
                    g1_repaired, g2_repaired, repairs = self.apply_micro_repairs(g1, g2)
                else:
                    g1_repaired = g1
                    g2_repaired = g2
                    repairs = []
                
                # Check constraints
                total_f = g1_repaired["f_count"] + g2_repaired["f_count"]
                total_v = g1_repaired["v_count"] + g2_repaired["v_count"]
                quotas = self.check_per_gap_quotas(g1_repaired, g2_repaired)
                
                # Score combination
                score = self.score_combination_v2(g1_repaired, g2_repaired)
                
                if score > best_score:
                    best_score = score
                    best_g1 = g1_repaired
                    best_g2 = g2_repaired
                    best_repairs = repairs
                    best_metrics = {
                        "total_f_words": total_f,
                        "total_verbs": total_v,
                        "g1_f_words": g1_repaired["f_count"],
                        "g1_verbs": g1_repaired["v_count"],
                        "g2_f_words": g2_repaired["f_count"],
                        "g2_verbs": g2_repaired["v_count"],
                        "quotas_met": quotas,
                        "score": score,
                        "has_true": "TRUE" in g1_repaired["text"] or "TRUE" in g2_repaired["text"],
                        "repairs_applied": len(repairs)
                    }
        
        return best_g1, best_g2, best_metrics
    
    def compose_layout_v2(self, label: str, seed: int, enable_repair: bool = True) -> Dict:
        """
        Compose layout with v5.2.2-B enhancements.
        """
        
        # Select best combination with repair
        g1, g2, metrics = self.select_best_combination_v2(seed, enable_repair)
        
        # Create layout
        layout = {
            "label": label,
            "seed": seed,
            "gaps": {
                "G1": {
                    "start": 0, 
                    "end": 20, 
                    "text": g1["text"], 
                    "f_count": g1["f_count"], 
                    "v_count": g1["v_count"]
                },
                "G2": {
                    "start": 34, 
                    "end": 62, 
                    "text": g2["text"], 
                    "f_count": g2["f_count"], 
                    "v_count": g2["v_count"]
                }
            },
            "anchors": {
                "EAST": [21, 24],
                "NORTHEAST": [25, 33],
                "BERLINCLOCK": [63, 73]
            },
            "metrics": metrics,
            "per_gap_quotas_met": metrics["quotas_met"]["all"],
            "meets_neargate": (
                metrics["total_f_words"] >= 8 and 
                metrics["total_verbs"] >= 2 and
                metrics["quotas_met"]["all"]
            )
        }
        
        return layout

def test_composer_v2():
    """Test the enhanced gap composer."""
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    phrasebank_path = base_dir / "policies" / "phrasebank.gaps.json"
    
    if not phrasebank_path.exists():
        print(f"Phrasebank not found at {phrasebank_path}")
        return
    
    composer = GapComposerV2(phrasebank_path)
    
    print("\nGap Composer v2 Test (with per-gap quotas)")
    print("=" * 80)
    
    # Test multiple seeds
    for i in range(5):
        label = f"HEAD_{i+1:03d}_v522B"
        seed = 1337 + i * 1000
        
        layout = composer.compose_layout_v2(label, seed, enable_repair=True)
        
        print(f"\n{label}:")
        print(f"G1: {layout['gaps']['G1']['text'][:30]}...")
        print(f"    f_words={layout['gaps']['G1']['f_count']} (quota≥4), verbs={layout['gaps']['G1']['v_count']}")
        print(f"G2: {layout['gaps']['G2']['text'][:30]}...")
        print(f"    f_words={layout['gaps']['G2']['f_count']} (quota≥4), verbs={layout['gaps']['G2']['v_count']}")
        print(f"Total: f_words={layout['metrics']['total_f_words']}, verbs={layout['metrics']['total_verbs']}")
        print(f"Per-gap quotas met: {layout['per_gap_quotas_met']}")
        print(f"Repairs applied: {layout['metrics']['repairs_applied']}")
        print(f"Meets near-gate: {layout['meets_neargate']}")
    
    print("\n" + "=" * 80)
    print("✓ Composer v2 test complete")

if __name__ == "__main__":
    test_composer_v2()