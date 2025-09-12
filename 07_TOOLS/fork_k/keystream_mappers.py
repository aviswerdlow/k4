#!/usr/bin/env python3
"""
Fork K - Clock to Keystream Mappers
Combines Berlin Clock and Urania Clock states into 97-character keystreams
"""

from typing import List, Dict, Tuple
import numpy as np

class KeystreamMapper:
    def __init__(self):
        """Initialize keystream mapper"""
        self.methods = [
            'direct_concat',
            'alt_streams',
            'pointwise',
            'matrix_gen'
        ]
    
    def generate_keystream(self, berlin: List[int], urania: List[int], 
                          method: str, params: Dict = None) -> List[int]:
        """
        Generate 97-length keystream from two 24-element clock vectors
        
        Args:
            berlin: 24-element Berlin Clock vector
            urania: 24-element Urania Clock vector
            method: Generation method name
            params: Method-specific parameters
        
        Returns:
            97-element keystream (values 0-25)
        """
        if params is None:
            params = {}
        
        if method == 'direct_concat':
            return self.direct_concatenation(berlin, urania, params)
        elif method == 'alt_streams':
            return self.alternating_streams(berlin, urania, params)
        elif method == 'pointwise':
            return self.pointwise_arithmetic(berlin, urania, params)
        elif method == 'matrix_gen':
            return self.matrix_generation(berlin, urania, params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def direct_concatenation(self, berlin: List[int], urania: List[int], 
                            params: Dict) -> List[int]:
        """
        K.4.1 - Direct concatenation with looping
        Concatenate B[0..23] + U[0..23] → 48 values, repeat to 97
        """
        # Normalize inputs to 0-25 range
        berlin_norm = [b % 26 for b in berlin]
        urania_norm = [u % 26 for u in urania]
        
        # Concatenate
        combined = berlin_norm + urania_norm  # 48 elements
        
        # Extend to 97 with optional jitter
        jitter = params.get('jitter', 0)
        keystream = []
        
        for loop_idx in range(3):  # Need 3 loops to cover 97
            for i, val in enumerate(combined):
                if len(keystream) >= 97:
                    break
                # Add jitter per loop
                jittered_val = (val + loop_idx * jitter) % 26
                keystream.append(jittered_val)
        
        return keystream[:97]
    
    def alternating_streams(self, berlin: List[int], urania: List[int], 
                           params: Dict) -> List[int]:
        """
        K.4.2 - Alternating streams
        Even positions from Berlin, odd from Urania (or vice versa)
        """
        # Normalize inputs
        berlin_norm = [b % 26 for b in berlin]
        urania_norm = [u % 26 for u in urania]
        
        # Determine starting stream
        start_with = params.get('start_with', 'berlin')
        drift = params.get('drift', 0)
        
        keystream = []
        berlin_idx = 0
        urania_idx = 0
        
        for pos in range(97):
            # Apply drift every 48 positions
            drift_offset = (pos // 48) * drift
            
            if start_with == 'berlin':
                if pos % 2 == 0:
                    # Even: Berlin
                    val = (berlin_norm[berlin_idx % 24] + drift_offset) % 26
                    berlin_idx += 1
                else:
                    # Odd: Urania
                    val = (urania_norm[urania_idx % 24] + drift_offset) % 26
                    urania_idx += 1
            else:
                if pos % 2 == 0:
                    # Even: Urania
                    val = (urania_norm[urania_idx % 24] + drift_offset) % 26
                    urania_idx += 1
                else:
                    # Odd: Berlin
                    val = (berlin_norm[berlin_idx % 24] + drift_offset) % 26
                    berlin_idx += 1
            
            keystream.append(val)
        
        return keystream
    
    def pointwise_arithmetic(self, berlin: List[int], urania: List[int], 
                            params: Dict) -> List[int]:
        """
        K.4.3 - Pointwise arithmetic operations
        K[i] = f(B[i%24], U[i%24]) where f ∈ {sum, product, XOR}
        """
        # Get operation
        operation = params.get('operation', 'sum')
        
        # Quantize to 5-bit values if needed
        if params.get('quantize', False):
            berlin_q = [self._quantize_5bit(b) for b in berlin]
            urania_q = [self._quantize_5bit(u) for u in urania]
        else:
            berlin_q = [b % 26 for b in berlin]
            urania_q = [u % 26 for u in urania]
        
        keystream = []
        
        for i in range(97):
            b_val = berlin_q[i % 24]
            u_val = urania_q[i % 24]
            
            if operation == 'sum':
                val = (b_val + u_val) % 26
            elif operation == 'product':
                val = (b_val * u_val) % 26
            elif operation == 'xor':
                # XOR in 5-bit space, then mod 26
                val = (b_val ^ u_val) % 26
            elif operation == 'diff':
                val = (b_val - u_val) % 26
            else:
                val = (b_val + u_val) % 26
            
            keystream.append(val)
        
        return keystream
    
    def matrix_generation(self, berlin: List[int], urania: List[int], 
                         params: Dict) -> List[int]:
        """
        K.4.4 - Matrix generation method
        Build transform matrix T from clock states, iterate vector
        """
        # Get parameters
        alpha = params.get('alpha', 1)
        beta = params.get('beta', 1)
        seed_type = params.get('seed', 'unit')
        
        # Normalize inputs
        berlin_norm = [b % 26 for b in berlin]
        urania_norm = [u % 26 for u in urania]
        
        # Build 26x26 transform matrix
        T = np.zeros((26, 26), dtype=int)
        
        # Fill matrix using clock values
        for r in range(26):
            for c in range(26):
                # Use clock values cyclically
                b_val = berlin_norm[r % 24]
                u_val = urania_norm[c % 24]
                T[r][c] = (alpha * b_val + beta * u_val) % 26
        
        # Initialize seed vector
        if seed_type == 'unit':
            v = np.zeros(26, dtype=int)
            v[0] = 1
        elif seed_type == 'kryptos':
            # K=10, R=17, Y=24, P=15, T=19, O=14, S=18
            kryptos_vals = [10, 17, 24, 15, 19, 14, 18]
            v = np.zeros(26, dtype=int)
            for i, val in enumerate(kryptos_vals):
                if i < 26:
                    v[i] = val
        else:
            v = np.ones(26, dtype=int)
        
        # Generate keystream by iterating vector
        keystream = []
        
        for i in range(97):
            # Extract key value (sum of vector mod 26)
            key_val = int(np.sum(v) % 26)
            keystream.append(key_val)
            
            # Update vector: v = T @ v (mod 26)
            v = (T @ v) % 26
        
        return keystream
    
    def _quantize_5bit(self, val: int) -> int:
        """Quantize value to 5-bit range (0-31) then mod 26"""
        return (val & 0x1F) % 26
    
    def get_all_variants(self, berlin: List[int], urania: List[int]) -> Dict[str, List[int]]:
        """Generate all keystream variants for testing"""
        variants = {}
        
        # Direct concatenation variants
        variants['direct_concat_j0'] = self.direct_concatenation(berlin, urania, {'jitter': 0})
        variants['direct_concat_j1'] = self.direct_concatenation(berlin, urania, {'jitter': 1})
        
        # Alternating stream variants
        variants['alt_berlin_d0'] = self.alternating_streams(berlin, urania, 
                                                            {'start_with': 'berlin', 'drift': 0})
        variants['alt_berlin_d1'] = self.alternating_streams(berlin, urania, 
                                                            {'start_with': 'berlin', 'drift': 1})
        variants['alt_urania_d0'] = self.alternating_streams(berlin, urania, 
                                                            {'start_with': 'urania', 'drift': 0})
        
        # Pointwise variants
        variants['point_sum'] = self.pointwise_arithmetic(berlin, urania, {'operation': 'sum'})
        variants['point_prod'] = self.pointwise_arithmetic(berlin, urania, {'operation': 'product'})
        variants['point_xor'] = self.pointwise_arithmetic(berlin, urania, {'operation': 'xor'})
        variants['point_diff'] = self.pointwise_arithmetic(berlin, urania, {'operation': 'diff'})
        
        # Matrix variants
        variants['matrix_11_unit'] = self.matrix_generation(berlin, urania, 
                                                           {'alpha': 1, 'beta': 1, 'seed': 'unit'})
        variants['matrix_15_unit'] = self.matrix_generation(berlin, urania, 
                                                           {'alpha': 1, 'beta': 5, 'seed': 'unit'})
        variants['matrix_51_unit'] = self.matrix_generation(berlin, urania, 
                                                           {'alpha': 5, 'beta': 1, 'seed': 'unit'})
        variants['matrix_11_kryptos'] = self.matrix_generation(berlin, urania, 
                                                              {'alpha': 1, 'beta': 1, 'seed': 'kryptos'})
        
        return variants


def main():
    """Test keystream mapper"""
    mapper = KeystreamMapper()
    
    # Create sample clock states
    berlin = list(range(24))  # Sample Berlin state
    urania = [(i * 3) % 24 for i in range(24)]  # Sample Urania state
    
    print("=== Keystream Mapper Test ===")
    print(f"Berlin sample: {berlin[:6]}...")
    print(f"Urania sample: {urania[:6]}...")
    
    # Test each method
    variants = mapper.get_all_variants(berlin, urania)
    
    for name, keystream in variants.items():
        print(f"\n{name}:")
        print(f"  First 20: {keystream[:20]}")
        print(f"  Length: {len(keystream)}")
        print(f"  Range: {min(keystream)}-{max(keystream)}")


if __name__ == "__main__":
    main()