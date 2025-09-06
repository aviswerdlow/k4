# CONTROL: CONTROL_IS_TRUE

## Control Head
- **Text**: "IS TRUE"
- **Expanded**: ISTRUEISTRUEISTRUEISTRUEISTRUEISTRUEISTRUEISTRUEIS...
- **Length**: 97
- **Expected**: fail - Too short and simplistic

## Gate Results
- **Near-gate**: FAIL
  - Coverage: 0.215
  - F-words: 0
  - Has verb: False

- **Phrase gates**: FAIL
  - Flint v2: FAIL
  - Generic: FAIL
  - Cadence: FAIL
  - Accepted by: []

## Evidence Spans

### 1. near - Low coverage
- **Evidence**: Coverage 0.215 < 0.85
- **Span**: `ISTRUEISTRUEISTRUEIS...`

### 2. near - Insufficient F-words
- **Evidence**: F-words 0 < 5
- **Span**: `IST RUEIST RUEISTRU`

### 3. flint_v2 - Failed Flint v2 check
- **Evidence**: No recognized phrase patterns
- **Span**: `ISTRUEISTRUEISTRUEISTRUEISTRUE...`

### 4. generic - Low POS score
- **Evidence**: POS 0.220 < 0.60
- **Span**: `IST RUEIST RUEISTRU EISTRU EISTRUE`

## Conclusion
Control head "IS TRUE" failed linguistic gates as expected.
This confirms that the gates are functioning to reject non-linguistic content.
