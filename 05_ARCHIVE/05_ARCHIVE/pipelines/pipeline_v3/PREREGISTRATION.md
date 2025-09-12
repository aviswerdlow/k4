# Explore v3: Generation-First Overhaul Pre-Registration

**Date:** 2025-01-06  
**Branch:** pipeline-v3-explore-gen-20250106  
**Commit:** 9cbce0a  
**Seed:** 1337  

## Motivation

The v2.3 diagnostic sprint revealed that while the Explore pipeline functions perfectly as a discriminative filter, all generation methods produce texts with n-gram scores ~5.88σ below random controls. The n-gram feature dominates scoring (r=0.984), meaning any successful approach must generate coherent bigrams/trigrams that survive blinding.

## Hypothesis

By shifting focus from constraint-forcing to native generation quality, we can produce heads with better language statistics that survive the blinding process. Three orthogonal approaches will be tested:

1. **Track A (Letter-space MCMC/Gibbs)**: Sample from English letter distribution directly
2. **Track B (WFSA/PCFG)**: Generate via weighted finite-state transducers  
3. **Track C (Cipher-space search)**: Optimize in cipher space with language objectives

## Success Criteria

- **Primary**: At least one track produces heads with delta_windowed > 0.05 AND delta_shuffled > 0.10
- **Secondary**: Improved n-gram z-scores compared to v2 baseline (target: > -3σ)
- **Tertiary**: Generate interpretable structure in promoted heads

## Tracks

### Track A: Letter-Space MCMC/Gibbs
- **Method**: Markov chain over letter positions with trigram model
- **Innovation**: Direct sampling from English distribution
- **Files**: `tracks/a_mcmc/mcmc_generator.py`

### Track B: WFSA/PCFG Synthesizer  
- **Method**: Weighted automata with corridor constraints
- **Innovation**: Structural generation with language coherence
- **Files**: `tracks/b_wfsa/wfsa_generator.py`

### Track C: Cipher-Space Hill-Climb
- **Method**: Search cipher space optimizing blinded language score
- **Innovation**: End-to-end optimization bypassing generation
- **Files**: `tracks/c_cipher/cipher_search.py`

## Common Infrastructure

- **Scoring**: Unified scoring module inheriting from v2 pipeline
- **Corpus**: Brown corpus trigram model for language statistics
- **Orbits**: Stability checking for promoted candidates
- **Validation**: Delta thresholds remain δ₁=0.05, δ₂=0.10

## Timeline

1. Build trigram model from corpus
2. Implement Track A (MCMC)
3. Implement Track B (WFSA)
4. Implement Track C (Cipher)
5. Run all tracks through pipeline
6. Create dashboard and analysis

## Pre-Registration Hash

This document pre-registered at commit: 9cbce0a