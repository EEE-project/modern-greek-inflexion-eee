# Test Tools for Modern Greek Inflexion Library

Complete toolkit for testing and validating Greek verb form generation.

## Overview

Three tools work together to validate library fixes:

1. **`fetch_rimata.py`** — Fetch reference data from Rimata.app
2. **`test_library_comparison.py`** — Compare old vs new library versions
3. **`run_full_test.sh`** — Complete automated workflow

## Quick Start

### One-Command Full Test

```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee
bash run_full_test.sh
```

This runs the complete workflow and shows summary results.

### Manual Step-by-Step

```bash
# 1. Fetch Rimata reference data
cat test/data/Ρήματα_Input_for_rimata.tsv | python3 fetch_rimata.py > test/data/Ρήματα_Combined.tsv 2>test/data/fetch_rimata.log

# 2. Compare libraries
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py > test/data/Ρήματα_Test_Results_Comparison.tsv 2>test/data/test_comparison.log

# 3. View results
head test/data/Ρήματα_Test_Results_Comparison.tsv
```

## Tool Details

### 1. `fetch_rimata.py` — Fetch Reference Data

**Purpose:** Query Rimata.app for aorist and future forms to create reference dataset.

**Usage:**
```bash
cat input.tsv | python3 fetch_rimata.py > output.tsv
```

**Input:** TSV with verb column (`Ενεστώτας`, `Verb`, or `Present`)

**Output:** Same TSV with 3 new columns:
- `Rimata_Αόριστος` — Aorist form(s)
- `Rimata_Μέλλοντας` — Future form(s)
- `Rimata_Note` — Error notes

**Progress:** Shown on stderr (shows ✓/✗ for each verb)

**Performance:** ~87 verbs in 50 seconds

See `FETCH_RIMATA.md` for details.

### 2. `test_library_comparison.py` — Compare Libraries

**Purpose:** Test both library versions and compare results to identify improvements/regressions.

**Usage:**
```bash
cat verbs_with_rimata.tsv | python3 test_library_comparison.py > comparison.tsv
```

**Input:** TSV with:
- `Ενεστώτας` — Verb column (required)
- `Αόριστος` — Expected aorist (optional)
- `Μέλλοντας` — Expected future (optional)
- Rimata reference columns (optional but recommended)

**Output:** Comparison TSV with:
- Original library results (v2.0.7)
- Modified library results
- Change status (IMPROVED/REGRESSED/—)
- PASS/FAIL for each verb/form

**Columns:**
```
Ρήμα | Translation | Aorist_Expected | Future_Expected |
Rimata_Αόριστος | Rimata_Μέλλοντας |
Aorist_Modified | Future_Modified | Aorist_Original | Future_Original |
Aorist_Change | Future_Change | Overall_Change | Comment
```

**Progress:** Shown on stderr (shows test results as they run)

**Performance:** ~87 verbs in 2-3 minutes

See `TEST_LIBRARY_COMPARISON.md` for details.

### 3. `run_full_test.sh` — Complete Workflow

**Purpose:** Automated end-to-end testing: fetch Rimata data → test libraries → show results.

**Usage:**
```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee
bash run_full_test.sh
```

**What it does:**
1. Checks prerequisites (venv, venv_original)
2. Runs `fetch_rimata.py` to get reference data
3. Runs `test_library_comparison.py` to compare libraries
4. Shows summary statistics
5. Displays regressions (if any)

**Output:**
- `test/data/Ρήματα_Combined.tsv` — Input + Rimata reference data
- `test/data/Ρήματα_Test_Results_Comparison.tsv` — Full comparison results
- `test/data/fetch_rimata.log` — Fetch progress log
- `test/data/test_comparison.log` — Comparison progress log

**Total Time:** ~3-4 minutes for 87 verbs

## Prerequisites

### Python Virtual Environments

Both must be set up:

```bash
# Modified library (development version)
python3 -m venv venv
source venv/bin/activate
pip install -e .
deactivate

# Original library (v2.0.7 reference)
python3 -m venv venv_original
source venv_original/bin/activate
pip install modern-greek-inflexion==2.0.7
deactivate
```

### Input Data

Requires `test/data/Ρήματα_Input_for_rimata.tsv`:

```bash
# Create from original combined TSV by removing Rimata columns:
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Combined.tsv', sep='\t')
df[['Ενεστώτας', 'Μετάφραση', 'Αόριστος', 'Μέλλοντας']].to_csv(
    'test/data/Ρήματα_Input_for_rimata.tsv', sep='\t', index=False
)
EOF
```

## Workflow Examples

### Run Complete Test After Making Changes

```bash
# Edit library code
# Then test:
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee

# Reinstall modified library
source venv/bin/activate
pip install -e .
deactivate

# Run full test
bash run_full_test.sh
```

### Fetch Rimata Data Only

```bash
cat test/data/Ρήματα_Input_for_rimata.tsv | python3 fetch_rimata.py > test/data/Ρήματα_Combined.tsv
```

### Test Libraries Only (Skip Rimata Fetch)

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py > test/data/Ρήματα_Test_Results_Comparison.tsv 2>test/data/test_comparison.log
```

### View Only Improvements

```bash
cat test/data/Ρήματα_Test_Results_Comparison.tsv | awk -F'\t' '$12 == "IMPROVED"'
```

### Check for Regressions

```bash
cat test/data/Ρήματα_Test_Results_Comparison.tsv | awk -F'\t' '$12 == "REGRESSED"'
```

### Analyze Results with Python

```bash
python3 << 'EOF'
import pandas as pd

df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')

print("=== STATISTICS ===")
print(f"Total verbs: {len(df)}")
print(f"Improvements: {(df['Overall_Change'] == 'IMPROVED').sum()}")
print(f"Regressions: {(df['Overall_Change'] == 'REGRESSED').sum()}")
print(f"Aorist PASS (Modified): {(df['Aorist_Modified'] == 'PASS').sum()}/{len(df)}")
print(f"Future PASS (Modified): {(df['Future_Modified'] == 'PASS').sum()}/{len(df)}")

# Show key verbs
print("\n=== KEY VERBS ===")
key = ['σχολάω', 'γελάω', 'αγαπάω', 'αργώ']
for verb in key:
    row = df[df['Ρήμα'] == verb]
    if not row.empty:
        r = row.iloc[0]
        print(f"{verb:15} | Aor: {r['Aorist_Change']:15} Fut: {r['Future_Change']:15}")
EOF
```

## Output Analysis

### Read Results File

```bash
# View entire results
cat test/data/Ρήματα_Test_Results_Comparison.tsv

# View in spreadsheet
libreoffice test/data/Ρήματα_Test_Results_Comparison.tsv

# View with column numbers
head test/data/Ρήματα_Test_Results_Comparison.tsv | cut -f1-7
```

### Understanding Columns

| # | Column | Meaning |
|---|--------|---------|
| 1 | Ρήμα | Greek verb (present) |
| 2 | Translation | English translation |
| 3 | Aorist_Expected | Reference aorist form |
| 4 | Future_Expected | Reference future form |
| 5 | Rimata_Αόριστος | Rimata.app aorist |
| 6 | Rimata_Μέλλοντας | Rimata.app future |
| 7 | Aorist_Modified | Modified lib result (PASS/FAIL) |
| 8 | Future_Modified | Modified lib result (PASS/FAIL) |
| 9 | Aorist_Original | Original lib result (PASS/FAIL) |
| 10 | Future_Original | Original lib result (PASS/FAIL) |
| 11 | Aorist_Change | Change (IMPROVED/REGRESSED/—) |
| 12 | Future_Change | Change (IMPROVED/REGRESSED/—) |
| 13 | Overall_Change | Overall (IMPROVED/REGRESSED/—) |
| 14 | Comment | Notes |

### Interpret Results

- **PASS** — Library generated expected form
- **FAIL** — Library did not generate expected form
- **IMPROVED** — Original was FAIL, Modified is PASS (fix worked!)
- **REGRESSED** — Original was PASS, Modified is FAIL (side effect)
- **—** — No change between versions

## Troubleshooting

### ModuleNotFoundError

```
ERROR: Could not import modern_greek_inflexion
```

Solution: Ensure venv_original is set up with v2.0.7:

```bash
python3 -m venv venv_original
source venv_original/bin/activate
pip install modern-greek-inflexion==2.0.7
```

### No input file

```
ERROR: Input file not found
```

Solution: Create input file:

```bash
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Combined.tsv', sep='\t')
df[['Ενεστώτας', 'Μετάφραση', 'Αόριστος', 'Μέλλοντας']].to_csv(
    'test/data/Ρήματα_Input_for_rimata.tsv', sep='\t', index=False
)
EOF
```

### Script hangs

- fetch_rimata.py: Network timeout (Rimata.app slow) - wait or Ctrl+C
- test_library_comparison.py: Expected (87 verbs takes 2-3 min)

### Empty output

Check stderr for errors:

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py 2>&1 | tail -20
```

## Files Summary

| File | Purpose |
|------|---------|
| `fetch_rimata.py` | Fetch Rimata.app reference data |
| `test_library_comparison.py` | Test and compare library versions |
| `run_full_test.sh` | Automated complete workflow |
| `FETCH_RIMATA.md` | Detailed fetch_rimata.py documentation |
| `TEST_LIBRARY_COMPARISON.md` | Detailed test script documentation |
| `TEST_TOOLS.md` | This file - overview and examples |
| `test/data/Ρήματα_Input_for_rimata.tsv` | Input (verbs only, no Rimata data) |
| `test/data/Ρήματα_Combined.tsv` | Output after fetch_rimata.py |
| `test/data/Ρήματα_Test_Results_Comparison.tsv` | Final comparison results |

## Integration with CI/CD

Use in automated testing:

```bash
#!/bin/bash
set -e

cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee
bash run_full_test.sh 2>&1 | tee test-results.log

# Check for regressions
if grep "REGRESSED" test/data/Ρήματα_Test_Results_Comparison.tsv; then
    echo "ERROR: Regressions found"
    exit 1
fi

echo "✓ All tests passed"
```
