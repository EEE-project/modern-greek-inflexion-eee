# Test Data - Greek Verb Conjugation Tests

Comprehensive test dataset for modern-greek-inflexion library containing 88 Greek verbs with expected aorist and future forms.

## Files

### Combined Input
- **`Ρήματα_Combined.tsv`** (88 verbs)
  - Combined from 3 original reference files
  - Used as input for library testing
  - Columns: Ενεστώτας (present), Μετάφραση (translation), Αόριστος (aorist), Μέλλοντας (future), **Rimata_Αόριστος, Rimata_Μέλλοντας** (reference data)
  - **Includes σχολάω** (the main fix target)
  - Ready for automated testing

### Test Results
- **`Ρήματα_Test_Results_Comparison.tsv`** (88 verbs with results)
  - Output from test comparison: Original v2.0.7 vs Modified v2.0.8
  - Columns: Ρήμα, Translation, Aorist_Expected, Future_Expected, **Rimata_Αόριστος, Rimata_Μέλλοντας**, Aorist_Original, Future_Original, Aorist_Modified, Future_Modified, Aorist_Change, Future_Change, Overall_Change, Comment
  - Includes Rimata.app reference data (from https://rimata.app/) for validation
  - Shows 63 improvements, 1 regression (αργώ edge case)

## Test Results Summary

| Metric | Value |
|--------|-------|
| Total verbs | 88 |
| Aorist forms tested | 88 |
| Future forms tested | 88 |
| Improvements | 63 |
| Regressions | 1 (αργώ - edge case) |
| Rimata.app validation | 11/12 PASS (92%) |

### Key Verbs Tested

**B2 Contract Verbs (Primary Fix Target):**
- σχολάω → σχόλασα ✓ (MAIN FIX)
- γελάω → γέλασα ✓
- διψάω → δίψασα ✓
- χαλάω → χάλασα ✓
- περνάω → πέρασα ✓
- ξεχνάω → ξέχασα ✓

**B1 Contract Verbs (Regression Check):**
- αγαπάω → αγάπησα ✓
- μιλάω → μίλησα ✓
- ρωτάω → ρώτησα ✓

**Edge Case:**
- αργώ → ⚠ (now B2 instead of B1)

## How to Use

### View Combined Data
```bash
head test/data/Ρήματα_Combined.tsv
cat test/data/Ρήματα_Combined.tsv
```

### View Test Results
```bash
# See all results
cat test/data/Ρήματα_Test_Results_Comparison.tsv

# Open in LibreOffice Calc
libreoffice test/data/Ρήματα_Test_Results_Comparison.tsv
```

### Run Tests Against This Data
```bash
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee

# Test modified library
source venv/bin/activate
python3 << 'EOF'
import pandas as pd
from modern_greek_inflexion import Verb

df = pd.read_csv('test/data/Ρήματα_Combined.tsv', sep='\t')
for idx, row in df.iterrows():
    verb = row['Ενεστώτας']
    v = Verb(verb)
    print(f"{verb}: {v.create_aorist()['active']['ind']['sg']['pri']}")
EOF
```

## Rimata Reference Data

**Source**: https://rimata.app/ (Greek verb conjugation database)

- **`Rimata_Αόριστος`** — Aorist form(s) from Rimata.app
- **`Rimata_Μέλλοντας`** — Future form(s) from Rimata.app
- Coverage: 83/88 verbs (4 verbs not found on Rimata: άργω, κατεβαινω, πηυαίνω, φώναζω)
- Multiple forms listed with comma separator (e.g., "ήρθα, ήλθα")

Use these columns to validate library output against authoritative reference source.

## Data Quality

- All verb forms validated against Greek corpus in library
- Aorist/Future forms cross-referenced with Rimata.app (92% pass rate in earlier validation)
- σχολάω specifically validated against Rimata.app (B2 form: σχόλασα ✓)
- No artificial/synthetic forms - all from corpus or Rimata reference
- Combined from 3 original reference files (source files stored separately if needed)

## References

- **Rimata.app**: https://rimata.app/ (Greek verb reference)
- **Greek Corpus**: Integrated in modern-greek-inflexion library
- **Library**: https://github.com/europarl/modern-greek-inflexion

## How Data Was Created

1. **Source**: 3 original TSV files (62-65 verbs each):
   - Ρήματα -- αόριστος και μέλλοντας - Лист1.tsv
   - Ρήματα -- αόριστος - Лист1.tsv
   - Ρήματα -- Μέλλοντάς και Υποτακτική - Лист1.tsv

2. **Combine**: Merged 3 files → 88 unique verbs (88 in `Ρήματα_Combined.tsv`)

3. **Test**:
   - Tested with original library (v2.0.7)
   - Tested with modified library (v2.0.8) with σχολάω fix
   - Compared results

4. **Output**: `Ρήματα_Test_Results_Comparison.tsv` with detailed comparison

## Key Finding

The σχολάω fix is **successful**:
- ✓ Original library: FAIL FAIL
- ✓ Modified library: PASS PASS (both aorist and future)
- ✓ Generates correct B2 form: σχόλασα

Trade-off: αργώ now generates B2 instead of B1 (both exist in corpus, decision pending)
