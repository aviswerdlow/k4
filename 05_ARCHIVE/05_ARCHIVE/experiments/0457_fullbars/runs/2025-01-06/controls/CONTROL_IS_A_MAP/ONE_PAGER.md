# CONTROL: CONTROL_IS_A_MAP

## Control Head
- **Text**: "IS A MAP"
- **Expanded**: ISAMAPISAMAPISAMAPISAMAPISAMAPISAMAPISAMAPISAMAPIS...
- **Length**: 97
- **Expected**: fail - Too short and simplistic

## Gate Results
- **Near-gate**: FAIL
  - Coverage: 0.382
  - F-words: 1
  - Has verb: False

- **Phrase gates**: FAIL
  - Flint v2: FAIL
  - Generic: FAIL
  - Cadence: FAIL
  - Accepted by: []

## Evidence Spans

### 1. near - Low coverage
- **Evidence**: Coverage 0.382 < 0.85
- **Span**: `ISAMAPISAMAPISAMAPIS...`

### 2. near - Insufficient F-words
- **Evidence**: F-words 1 < 5
- **Span**: `ISAMAPIS AMAPI SAMAPI`

### 3. flint_v2 - Failed Flint v2 check
- **Evidence**: No recognized phrase patterns
- **Span**: `ISAMAPISAMAPISAMAPISAMAPISAMAP...`

### 4. generic - Low POS score
- **Evidence**: POS 0.369 < 0.60
- **Span**: `ISAMAPIS AMAPI SAMAPI SAMAPI SAMAP`

## Conclusion
Control head "IS A MAP" failed linguistic gates as expected.
This confirms that the gates are functioning to reject non-linguistic content.
