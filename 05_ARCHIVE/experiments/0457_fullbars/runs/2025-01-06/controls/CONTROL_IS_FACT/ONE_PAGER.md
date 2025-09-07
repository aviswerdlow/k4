# CONTROL: CONTROL_IS_FACT

## Control Head
- **Text**: "IS FACT"
- **Expanded**: ISFACTISFACTISFACTISFACTISFACTISFACTISFACTISFACTIS...
- **Length**: 97
- **Expected**: fail - Too short and simplistic

## Gate Results
- **Near-gate**: FAIL
  - Coverage: 0.436
  - F-words: 1
  - Has verb: False

- **Phrase gates**: FAIL
  - Flint v2: FAIL
  - Generic: FAIL
  - Cadence: FAIL
  - Accepted by: []

## Evidence Spans

### 1. near - Low coverage
- **Evidence**: Coverage 0.436 < 0.85
- **Span**: `ISFACTISFACTISFACTIS...`

### 2. near - Insufficient F-words
- **Evidence**: F-words 1 < 5
- **Span**: `IS FACTI SFA`

### 3. flint_v2 - Failed Flint v2 check
- **Evidence**: No recognized phrase patterns
- **Span**: `ISFACTISFACTISFACTISFACTISFACT...`

### 4. generic - Low POS score
- **Evidence**: POS 0.279 < 0.60
- **Span**: `IS FACTI SFA CTISFAC TIS`

## Conclusion
Control head "IS FACT" failed linguistic gates as expected.
This confirms that the gates are functioning to reject non-linguistic content.
