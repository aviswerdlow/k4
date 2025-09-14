#!/usr/bin/env python3
"""
K5 Gate - Post-plaintext validation and secrecy motif detection
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


class K5Gate:
    """Post-plaintext gate for K5 readiness check"""
    
    # Secrecy motifs to look for
    SECRECY_MOTIFS = [
        'SECRET', 'KEEP', 'HIDDEN', 'POWER', 'KNOWLEDGE',
        'TRUTH', 'REVEAL', 'CONCEAL', 'PROTECT', 'GUARD',
        'CIPHER', 'CODE', 'ENCRYPT', 'DECODE', 'KEY',
        'SHADOW', 'LIGHT', 'DARKNESS', 'ILLUMINATE',
        'WISDOM', 'MYSTERY', 'PUZZLE', 'RIDDLE'
    ]
    
    # Intelligence/agency references
    AGENCY_REFS = [
        'CIA', 'NSA', 'FBI', 'AGENCY', 'INTELLIGENCE',
        'LANGLEY', 'BERLIN', 'MOSCOW', 'STATION', 'AGENT'
    ]
    
    # Coordinate/location words
    LOCATION_REFS = [
        'LATITUDE', 'LONGITUDE', 'COORDINATE', 'LOCATION',
        'NORTH', 'SOUTH', 'EAST', 'WEST', 'DEGREE',
        'MINUTE', 'SECOND', 'BEARING', 'AZIMUTH'
    ]
    
    def __init__(self, plaintext: str = None):
        """Initialize with optional plaintext"""
        self.plaintext = plaintext.upper() if plaintext else None
        self.results = {}
    
    def load_plaintext(self, path: str):
        """Load plaintext from file"""
        with open(path, 'r') as f:
            self.plaintext = f.read().strip().upper()
    
    def check_sentence_structure(self) -> Dict[str, Any]:
        """Check for sentence-like structure"""
        if not self.plaintext:
            return {'error': 'No plaintext loaded'}
        
        # Look for sentence boundaries (periods approximated by certain patterns)
        # In K4, sentences might be run together
        
        # Check for repeated short sequences that might indicate word boundaries
        words_3 = []
        words_4 = []
        words_5 = []
        
        for i in range(len(self.plaintext) - 2):
            words_3.append(self.plaintext[i:i+3])
        for i in range(len(self.plaintext) - 3):
            words_4.append(self.plaintext[i:i+4])
        for i in range(len(self.plaintext) - 4):
            words_5.append(self.plaintext[i:i+5])
        
        # Count common English words
        common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY']
        word_count = 0
        for word in common_words:
            word_count += self.plaintext.count(word)
        
        # Estimate sentence count (rough heuristic)
        estimated_sentences = len(self.plaintext) // 20  # Assume ~20 chars per sentence
        
        return {
            'common_word_count': word_count,
            'estimated_sentences': estimated_sentences,
            'has_structure': word_count > 5
        }
    
    def detect_motifs(self) -> Dict[str, List[str]]:
        """Detect secrecy and other motifs"""
        found_motifs = {
            'secrecy': [],
            'agency': [],
            'location': []
        }
        
        if not self.plaintext:
            return found_motifs
        
        # Check for secrecy motifs
        for motif in self.SECRECY_MOTIFS:
            if motif in self.plaintext:
                found_motifs['secrecy'].append(motif)
        
        # Check for agency references
        for ref in self.AGENCY_REFS:
            if ref in self.plaintext:
                found_motifs['agency'].append(ref)
        
        # Check for location references
        for ref in self.LOCATION_REFS:
            if ref in self.plaintext:
                found_motifs['location'].append(ref)
        
        return found_motifs
    
    def check_reordering_potential(self) -> Dict[str, Any]:
        """Check if text might benefit from reordering"""
        if not self.plaintext:
            return {'error': 'No plaintext loaded'}
        
        # Check for patterns that suggest reordering
        # Look for: repeated patterns, unusual character distributions
        
        # Divide into blocks and check coherence
        block_size = len(self.plaintext) // 3
        blocks = [
            self.plaintext[:block_size],
            self.plaintext[block_size:2*block_size],
            self.plaintext[2*block_size:]
        ]
        
        # Score each block for English-like properties
        block_scores = []
        for block in blocks:
            score = sum(1 for c in block if c in 'ETAOINSHRDLU') / len(block) if block else 0
            block_scores.append(score)
        
        # Check if reordering blocks improves coherence
        reorder_suggestions = []
        
        # Try simple reorderings
        reorderings = [
            [0, 1, 2],  # Original
            [2, 1, 0],  # Reverse
            [1, 0, 2],  # Swap first two
            [0, 2, 1],  # Swap last two
            [1, 2, 0],  # Rotate left
            [2, 0, 1]   # Rotate right
        ]
        
        for order in reorderings:
            reordered = ''.join(blocks[i] for i in order)
            if 'SECRET' in reordered or 'BERLINCLOCK' in reordered:
                reorder_suggestions.append({
                    'order': order,
                    'preview': reordered[:30] + '...'
                })
        
        return {
            'block_scores': block_scores,
            'variance': max(block_scores) - min(block_scores) if block_scores else 0,
            'suggestions': reorder_suggestions[:3]  # Top 3 suggestions
        }
    
    def calculate_k5_readiness(self) -> Dict[str, Any]:
        """Calculate overall K5 readiness score"""
        if not self.plaintext:
            return {'error': 'No plaintext loaded', 'score': 0}
        
        score = 0
        factors = []
        
        # Check sentence structure
        structure = self.check_sentence_structure()
        if structure.get('has_structure'):
            score += 20
            factors.append('sentence_structure')
        
        # Check motifs
        motifs = self.detect_motifs()
        if motifs['secrecy']:
            score += 30
            factors.append(f"secrecy_motifs({len(motifs['secrecy'])})")
        if motifs['agency']:
            score += 20
            factors.append(f"agency_refs({len(motifs['agency'])})")
        if motifs['location']:
            score += 15
            factors.append(f"location_refs({len(motifs['location'])})")
        
        # Check reordering
        reordering = self.check_reordering_potential()
        if reordering.get('suggestions'):
            score += 15
            factors.append('reordering_potential')
        
        # Bonus for BERLINCLOCK
        if 'BERLINCLOCK' in self.plaintext:
            score += 20
            factors.append('berlinclock_found')
        
        return {
            'score': score,
            'max_score': 100,
            'percentage': f"{score}%",
            'factors': factors,
            'k5_ready': score >= 50,
            'recommendation': self._get_recommendation(score)
        }
    
    def _get_recommendation(self, score: int) -> str:
        """Get recommendation based on score"""
        if score >= 80:
            return "Strong K5 candidate. Proceed to K5 analysis."
        elif score >= 50:
            return "Moderate K5 potential. Consider reordering or further analysis."
        elif score >= 30:
            return "Weak K5 signals. May need different decryption approach."
        else:
            return "Unlikely K5 candidate. Verify K4 decryption first."
    
    def full_analysis(self) -> Dict[str, Any]:
        """Run complete K5 gate analysis"""
        if not self.plaintext:
            return {'error': 'No plaintext loaded'}
        
        return {
            'plaintext_length': len(self.plaintext),
            'plaintext_preview': self.plaintext[:50] + '...',
            'sentence_structure': self.check_sentence_structure(),
            'motifs': self.detect_motifs(),
            'reordering': self.check_reordering_potential(),
            'k5_readiness': self.calculate_k5_readiness()
        }


def main():
    parser = argparse.ArgumentParser(description='K5 Gate - Post-plaintext validation')
    parser.add_argument('--plaintext', help='Path to plaintext file')
    parser.add_argument('--text', help='Direct plaintext string')
    parser.add_argument('--manifest', help='Path to manifest (will decrypt first)')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("K5 Gate - Post-Plaintext Analysis")
    print("=" * 60)
    
    # Initialize gate
    gate = K5Gate()
    
    # Load plaintext
    if args.text:
        gate.plaintext = args.text.upper()
    elif args.plaintext:
        gate.load_plaintext(args.plaintext)
    elif args.manifest:
        # Decrypt from manifest
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        
        runner = ZoneRunner(args.manifest)
        ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        runner.load_ciphertext(str(ct_path))
        
        try:
            plaintext = runner.decrypt()
            gate.plaintext = plaintext
            print(f"Decrypted from manifest: {plaintext[:50]}...")
        except Exception as e:
            print(f"Error decrypting: {e}")
            sys.exit(1)
    else:
        print("Error: No plaintext source provided")
        sys.exit(1)
    
    # Run analysis
    results = gate.full_analysis()
    
    # Display results
    if 'error' in results:
        print(f"Error: {results['error']}")
        sys.exit(1)
    
    print(f"\nPlaintext length: {results['plaintext_length']}")
    print(f"Preview: {results['plaintext_preview']}")
    
    # Sentence structure
    print("\nSentence Structure:")
    structure = results['sentence_structure']
    print(f"  Common words found: {structure['common_word_count']}")
    print(f"  Estimated sentences: {structure['estimated_sentences']}")
    print(f"  Has structure: {structure['has_structure']}")
    
    # Motifs
    print("\nMotifs Detected:")
    motifs = results['motifs']
    if motifs['secrecy']:
        print(f"  Secrecy: {', '.join(motifs['secrecy'])}")
    if motifs['agency']:
        print(f"  Agency: {', '.join(motifs['agency'])}")
    if motifs['location']:
        print(f"  Location: {', '.join(motifs['location'])}")
    if not any(motifs.values()):
        print("  None found")
    
    # Reordering
    print("\nReordering Analysis:")
    reordering = results['reordering']
    print(f"  Block score variance: {reordering['variance']:.3f}")
    if reordering['suggestions']:
        print("  Suggestions:")
        for i, sugg in enumerate(reordering['suggestions'], 1):
            print(f"    {i}. Order {sugg['order']}: {sugg['preview']}")
    
    # K5 Readiness
    print("\nK5 Readiness Score:")
    k5 = results['k5_readiness']
    print(f"  Score: {k5['score']}/{k5['max_score']} ({k5['percentage']})")
    print(f"  Factors: {', '.join(k5['factors'])}")
    print(f"  K5 Ready: {'✓' if k5['k5_ready'] else '✗'}")
    print(f"  Recommendation: {k5['recommendation']}")
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Return exit code based on K5 readiness
    sys.exit(0 if k5['k5_ready'] else 1)


if __name__ == '__main__':
    main()