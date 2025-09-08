# Merge Instructions - Clean Repository State

**Date**: 2025-09-05  
**Tagged**: repo_truthful_20250905

## Branches to Merge (in order)

1. **hotfix-0457-sim-quarantine**
   ```bash
   git checkout main
   git merge hotfix-0457-sim-quarantine
   ```
   - Quarantines simulated content
   - Adds disclaimers

2. **audit-truth-sweep** 
   ```bash
   git checkout main
   git merge audit-truth-sweep
   ```
   - Removes final simulated link
   - Adds audit framework
   - Includes CI checks

## Branch to Archive (DO NOT MERGE)

- **experiment-0457** - Contains original mock implementations (historical reference only)
  ```bash
  # Archive locally but don't push
  git branch -m experiment-0457 archive/experiment-0457-simulated
  ```

## Post-Merge Verification

Run these checks after merging:

```bash
# 1. Verify no simulated links in README
grep -c "_simulated" README.md  # Should be 0

# 2. Run CI pre-merge check
./experiments/audit/ci/pre_merge_check.sh

# 3. Verify tag
git tag -l | grep truthful  # Should show repo_truthful_20250905

# 4. Check quarantine exists
ls experiments/_simulated/0457/DISCLAIMER_SIMULATED.md
```

## Ready State Confirmation

After merging, the repository will have:
- ✅ All simulated content quarantined with disclaimers
- ✅ No links to simulated content in README
- ✅ Audit framework in place
- ✅ CI checks active
- ✅ Forum reply draft ready to send

## Send to Elonka/Sparrow

Use the reply at: `experiments/audit/docs/FORUM_REPLY_DRAFT.md`

Key points emphasized:
1. Full transparency about mock implementations
2. Immediate corrective actions taken
3. P[74] = editorial (empirically proven)
4. Repository verified clean