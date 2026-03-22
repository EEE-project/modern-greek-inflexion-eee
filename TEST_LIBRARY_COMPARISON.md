# Test Library Comparison

Script to compare aorist and future verb form generation between original library (v2.0.7) and modified library.

## Prerequisites

Two virtual environments must be set up:

```bash
# Modified library (current development version)
python3 -m venv venv
source venv/bin/activate
pip install -e .
deactivate

# Original library (v2.0.7)
python3 -m venv venv_original
source venv_original/bin/activate
pip install modern-greek-inflexion==2.0.7
deactivate
```

Both venv directories must be at:
- `/home/sadov/work/greek/git/github/modern-greek-inflexion-eee/venv/` (modified)
- `/home/sadov/work/greek/git/github/modern-greek-inflexion-eee/venv_original/` (original)

## Usage

```bash
# Test with verbs + Rimata reference data
cat verbs_with_rimata.tsv | python3 test_library_comparison.py > comparison.tsv

# Or use input redirection
python3 test_library_comparison.py < verbs_with_rimata.tsv > comparison.tsv
```

## Input Format

TSV file with at minimum a verb column (`Ενεστώτας`). Should include Rimata reference data (add with `fetch_rimata.py`).

Required columns:
- `Ενεστώτας` — Greek verb in present form (required)

Optional columns:
- `Μετάφραση` — Translation
- `Αόριστος` — Expected aorist form
- `Μέλλοντας` — Expected future form
- `Rimata_Αόριστος` — Aorist from Rimata.app reference
- `Rimata_Μέλλοντας` — Future from Rimata.app reference

Example:

```tsv
Ενεστώτας	Μετάφραση	Αόριστος	Μέλλοντας	Rimata_Αόριστος	Rimata_Μέλλοντας
σχολάω	skip school	σχόλασα	θα σχολάσω	σχόλασα	θα σχολάσω
γελάω	laugh	γέλασα	θα γελάσω	γέλασα	θα γελάσω
αγαπάω	love	αγάπησα	θα αγαπήσω	αγάπησα	θα αγαπήσω
```

## Output Format

TSV with comprehensive comparison data:

| Column | Description |
|--------|-------------|
| `Ρήμα` | Greek verb (present form) |
| `Translation` | English translation (if provided) |
| `Aorist_Expected` | Expected aorist form (reference data) |
| `Future_Expected` | Expected future form (reference data) |
| `Rimata_Αόριστος` | Aorist from Rimata.app (if provided) |
| `Rimata_Μέλλοντας` | Future from Rimata.app (if provided) |
| `Aorist_Modified` | Aorist from modified library (PASS/FAIL) |
| `Future_Modified` | Future from modified library (PASS/FAIL) |
| `Aorist_Original` | Aorist from original v2.0.7 (PASS/FAIL) |
| `Future_Original` | Future from original v2.0.7 (PASS/FAIL) |
| `Aorist_Change` | Change status: IMPROVED/REGRESSED/— |
| `Future_Change` | Change status: IMPROVED/REGRESSED/— |
| `Overall_Change` | Overall change: IMPROVED/REGRESSED/— |
| `Comment` | User notes |

### Status Codes

- **PASS** — Library generated expected form
- **FAIL** — Library did NOT generate expected form
- **ERROR** — Exception during test
- **—** (dash) — No change between versions

### Change Codes

- **IMPROVED** — Original was FAIL, Modified is PASS (fix worked)
- **REGRESSED** — Original was PASS, Modified is FAIL (side effect)
- **—** (dash) — No change between versions

## Output Streams

- **stdout** — TSV comparison data (for piping/redirection)
- **stderr** — Progress log and summary

Progress example:

```
Testing 87 verbs...
Testing with MODIFIED library (from venv)...
[modified] ✓ σχολάω               aor: σχόλασα        fut: σχολάσω
[modified] ✓ γελάω                aor: γέλασα         fut: γελάσω
...
[original] ✓ σχολάω               aor: σχόλησα        fut: σχολήσω
[original] ✓ γελάω                aor: γέλασα         fut: γελάσω
...

=== SUMMARY ===
Total verbs: 87
Improvements: 63
Regressions: 1
```

## Complete Workflow

### 1. Prepare Input Data

```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee

# Create input TSV with only verbs (no Rimata data yet)
# File: test/data/Ρήματα_Input_for_rimata.tsv
```

### 2. Fetch Rimata Reference Data

```bash
# Add Rimata.app reference data
cat test/data/Ρήματα_Input_for_rimata.tsv | python3 fetch_rimata.py > test/data/Ρήματα_Combined.tsv 2>test/data/fetch_rimata.log

# Verify output
head test/data/Ρήματα_Combined.tsv
```

### 3. Compare Libraries

```bash
# Test both library versions
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py > test/data/Ρήματα_Test_Results_Comparison.tsv 2>test/data/test_comparison.log

# Check results
head test/data/Ρήματα_Test_Results_Comparison.tsv
```

### 4. Analyze Results

```bash
# View in spreadsheet
libreoffice test/data/Ρήματα_Test_Results_Comparison.tsv

# Or use command-line
python3 << 'EOF'
import pandas as pd

df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')
print(f"Total verbs: {len(df)}")
print(f"Improvements: {(df['Overall_Change'] == 'IMPROVED').sum()}")
print(f"Regressions: {(df['Overall_Change'] == 'REGRESSED').sum()}")

# Show improvements
print("\nImprovements:")
improved = df[df['Overall_Change'] == 'IMPROVED']
print(improved[['Ρήμα', 'Aorist_Change', 'Future_Change']].to_string())

# Show regressions
print("\nRegressions:")
regressed = df[df['Overall_Change'] == 'REGRESSED']
print(regressed[['Ρήμα', 'Aorist_Change', 'Future_Change']].to_string())
EOF
```

## Examples

### Test and View Results

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py > /tmp/results.tsv 2>&1
libreoffice /tmp/results.tsv
```

### Show Only Changed Verbs

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py 2>/dev/null | \
  awk -F'\t' '$12 != "—"' > /tmp/changed.tsv
```

### Check for Regressions

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py 2>/dev/null | \
  awk -F'\t' '$12 == "REGRESSED"'
```

### View Progress Only

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py 2>&1 1>/dev/null | tail -20
```

## Troubleshooting

### ModuleNotFoundError: venv_original

Ensure both venv directories exist and contain installed libraries:

```bash
ls -d venv venv_original
python3 -m venv venv_original
source venv_original/bin/activate
pip install modern-greek-inflexion==2.0.7
```

### No verbs tested

Check input TSV has correct verb column name:

```bash
head test/data/Ρήματα_Combined.tsv | cut -f1
```

Should show Greek verbs in first column.

### Empty output file

Check stderr for errors:

```bash
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py 2>&1 | tail -20
```

### Tests very slow

Expected behavior - the script tests each verb against both library versions. With 87 verbs:
- ~1 second per verb (total ~90 seconds)
- Shows progress in stderr

## Integration with Test Suite

Use this script to validate fixes:

```bash
# After making changes to library:
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee

# Reinstall modified library
source venv/bin/activate
pip install -e .

# Run comparison
cat test/data/Ρήματα_Combined.tsv | python3 test_library_comparison.py > test/data/Ρήματα_Test_Results_Comparison.tsv 2>test/data/test_comparison.log

# View results
grep "IMPROVED\|REGRESSED" test/data/Ρήματα_Test_Results_Comparison.tsv
```

## Performance Notes

- Tests 1-3 verbs per second (depends on library complexity)
- 87 verbs take ~90 seconds total
- Memory usage: ~50-100 MB
- Network: None (tests only use loaded libraries)
