# How to Use Test Tools

Guide for using the test tool suite to validate library fixes.

## The Three Tools

### 1. `fetch_rimata.py` — Get Reference Data
Fetches aorist and future forms from Rimata.app to create a reference dataset.

```bash
cat input.tsv | python3 fetch_rimata.py > output.tsv
```

**What it does:**
- Reads verbs from TSV via stdin
- Queries Rimata.app for each verb (~0.5s/verb, be patient!)
- Adds 3 columns: Rimata_Αόριστος, Rimata_Μέλλοντας, Rimata_Note
- Writes TSV to stdout
- Shows progress on stderr

### 2. `test_library_comparison.py` — Compare Library Versions
Tests the same verbs with both old (v2.0.7) and new (modified) library versions.

```bash
cat verbs_with_rimata.tsv | python3 test_library_comparison.py > comparison.tsv
```

**What it does:**
- Reads verbs with Rimata reference data via stdin
- Tests each verb with MODIFIED library (from venv)
- Tests each verb with ORIGINAL library v2.0.7 (from venv_original)
- Compares results to identify IMPROVED/REGRESSED changes
- Writes comparison TSV to stdout
- Shows test progress on stderr

### 3. `run_full_test.sh` — Complete Automated Workflow
Runs both tools in sequence with automatic error checking.

```bash
bash run_full_test.sh
```

**What it does:**
1. Checks prerequisites (venv, venv_original directories exist)
2. Runs fetch_rimata.py on input file
3. Runs test_library_comparison.py on result
4. Shows summary statistics
5. Displays any regressions found

## Quick Start — One Command

```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee
bash run_full_test.sh
```

This runs everything automatically and shows results.

## Step-by-Step Usage

### Step 1: Prepare Input (if needed)

```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee

# Create clean input file with just verbs (no Rimata data):
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Combined.tsv', sep='\t')
df[['Ενεστώτας', 'Μετάφραση', 'Αόριστος', 'Μέλλοντας']].to_csv(
    'test/data/Ρήματα_Input_for_rimata.tsv', sep='\t', index=False
)
EOF
```

### Step 2: Fetch Rimata Reference Data

```bash
# This takes ~50 seconds for 87 verbs
cat test/data/Ρήματα_Input_for_rimata.tsv | \
  python3 fetch_rimata.py > test/data/Ρήματα_Combined.tsv \
  2>test/data/fetch_rimata.log

# View progress
tail test/data/fetch_rimata.log
```

**Output files:**
- `test/data/Ρήματα_Combined.tsv` — Verbs with Rimata reference columns
- `test/data/fetch_rimata.log` — Fetch progress (✓/✗ for each verb)

### Step 3: Compare Libraries

```bash
# This takes ~2-3 minutes for 87 verbs
cat test/data/Ρήματα_Combined.tsv | \
  python3 test_library_comparison.py > test/data/Ρήματα_Test_Results_Comparison.tsv \
  2>test/data/test_comparison.log

# View progress
tail test/data/test_comparison.log
```

**Output files:**
- `test/data/Ρήματα_Test_Results_Comparison.tsv` — Full comparison results
- `test/data/test_comparison.log` — Test progress (✓/✗ for each verb)

### Step 4: Analyze Results

```bash
# View in spreadsheet
libreoffice test/data/Ρήματα_Test_Results_Comparison.tsv

# Or view on command line
head test/data/Ρήματα_Test_Results_Comparison.tsv

# Or analyze with Python
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')
print(f"Total: {len(df)}")
print(f"Improved: {(df['Overall_Change'] == 'IMPROVED').sum()}")
print(f"Regressed: {(df['Overall_Change'] == 'REGRESSED').sum()}")
print(f"Aorist PASS (Modified): {(df['Aorist_Modified'] == 'PASS').sum()}/{len(df)}")
EOF
```

## Common Workflows

### After Making Library Changes

```bash
# 1. Reinstall modified library
source venv/bin/activate
pip install -e .

# 2. Run full test
bash run_full_test.sh

# 3. View results
cat test/data/Ρήματα_Test_Results_Comparison.tsv | grep "IMPROVED\|REGRESSED"
```

### Check Specific Verbs

```bash
# View a specific verb
grep "^σχολάω" test/data/Ρήματα_Test_Results_Comparison.tsv

# View key verbs
for verb in σχολάω γελάω αγαπάω αργώ; do
  echo "=== $verb ==="
  grep "^$verb" test/data/Ρήματα_Test_Results_Comparison.tsv
done
```

### Show Only Improvements

```bash
# Command line
awk -F'\t' '$13 == "IMPROVED"' test/data/Ρήματα_Test_Results_Comparison.tsv | head

# Or Python
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')
improvements = df[df['Overall_Change'] == 'IMPROVED']
for idx, row in improvements.iterrows():
    print(f"{row['Ρήμα']:15} → Aorist: {row['Aorist_Change']:15} Future: {row['Future_Change']}")
EOF
```

### Show Regressions (Alert!)

```bash
# Command line
awk -F'\t' '$13 == "REGRESSED"' test/data/Ρήματα_Test_Results_Comparison.tsv

# Or Python
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')
regressions = df[df['Overall_Change'] == 'REGRESSED']
print(f"⚠️  Found {len(regressions)} regressions:")
for idx, row in regressions.iterrows():
    print(f"  {row['Ρήμα']:15} Aorist: {row['Aorist_Change']:15} Future: {row['Future_Change']}")
EOF
```

## Understanding Results

### Column Meanings

```
Ρήμα                    = Greek verb (present form)
Translation             = English translation
Aorist_Expected         = Reference aorist (from input)
Future_Expected         = Reference future (from input)
Rimata_Αόριστος        = Aorist from Rimata.app (reference)
Rimata_Μέλλοντας       = Future from Rimata.app (reference)
Aorist_Modified         = Modified lib result (PASS/FAIL)
Future_Modified         = Modified lib result (PASS/FAIL)
Aorist_Original         = Original lib result (PASS/FAIL)
Future_Original         = Original lib result (PASS/FAIL)
Aorist_Change           = Change status (IMPROVED/REGRESSED/—)
Future_Change           = Change status (IMPROVED/REGRESSED/—)
Overall_Change          = Overall (IMPROVED/REGRESSED/—)
Comment                 = Notes
```

### Status Codes

```
PASS    = Library generated the expected form ✓
FAIL    = Library did NOT generate expected form ✗
ERROR   = Exception during test (data issue)
—       = No change (dash character)
```

### Change Codes

```
IMPROVED    = Original FAIL → Modified PASS (the fix worked! 🎉)
REGRESSED   = Original PASS → Modified FAIL (we broke something ⚠️)
—           = No change (dash character)
```

## Example: Testing σχολάω Fix

The main fix target was σχολάω verb (should generate B2 aorist: σχόλασα).

### Before Fix (Original v2.0.7)
```
σχολάω: Aorist_Original = FAIL (was generating σχόλησα instead of σχόλασα)
```

### After Fix (Modified)
```
σχολάω: Aorist_Modified = PASS (now correctly generates σχόλασα)
        Aorist_Change = IMPROVED
```

### View in Results
```bash
grep "^σχολάω" test/data/Ρήματα_Test_Results_Comparison.tsv | cut -f1,11,12,13
# Output: σχολάω   IMPROVED   IMPROVED   IMPROVED
```

## Troubleshooting

### "No module named modern_greek_inflexion"

Ensure both venvs are set up:

```bash
# Check venv exists
ls -d venv venv_original

# Reinstall if needed
python3 -m venv venv_original
source venv_original/bin/activate
pip install modern-greek-inflexion==2.0.7
```

### Script hangs

- `fetch_rimata.py`: Normal (0.5s/verb, ~50s total). Ctrl+C to stop.
- `test_library_comparison.py`: Normal (1-3s/verb, 2-3min total). Ctrl+C to stop.

### Empty output

Check stderr for errors:

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py 2>&1 | tail -20
```

### Input file not found

Create it:

```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('test/data/Ρήματα_Combined.tsv', sep='\t')
df[['Ενεστώτας', 'Μετάφραση', 'Αόριστος', 'Μέλλοντας']].to_csv(
    'test/data/Ρήματα_Input_for_rimata.tsv', sep='\t', index=False
)
EOF
```

## Documentation References

- **FETCH_RIMATA.md** — Detailed fetch_rimata.py documentation
- **TEST_LIBRARY_COMPARISON.md** — Detailed test script documentation
- **TEST_TOOLS.md** — Overview of all tools and workflows

## Summary

```
Input (87 verbs)
    ↓
fetch_rimata.py (adds reference data from Rimata.app)
    ↓
test_library_comparison.py (tests old vs new library)
    ↓
Output (comparison TSV with PASS/FAIL and changes)
```

Use `bash run_full_test.sh` for automatic end-to-end testing.
