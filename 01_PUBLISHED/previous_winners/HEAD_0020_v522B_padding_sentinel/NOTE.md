# Sentinel Padding Bundle (Superseded)

This bundle used boundary-tokenizer sentinels ("XXXX", "YYYYYYY") as visual scaffolding
to mark anchor boundaries. Policy, rails, and null model identical to the current winner.
Superseded by lexicon fillers for human readability. See HEAD_0020_v522B/.

## Original Plaintext
```
WEAREINTHEGRIDSEEXXXXEASTNORTHEASTANDWEAREBYTHELINETOSEEYYYYYYYBERLINCLOCK
```

## Original Metrics
- Function words: 10+ (head-only, excluding sentinels)
- Verbs: 2+ (head-only)
- Coverage adj-p: < 0.01
- F-words adj-p: < 0.01

## Rails (Unchanged)
- Route: GRID_W14_ROWS
- T2 SHA: a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31
- Anchors: EAST [21,24], NORTHEAST [25,33], BERLINCLOCK [63,73]
- Option-A lawfulness at anchors

## Archive Date
{datetime.now().isoformat()}
