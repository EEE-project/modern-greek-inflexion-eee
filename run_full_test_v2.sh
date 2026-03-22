#!/bin/bash
# Complete test workflow v2: fetch Rimata → test both libs separately → compare results
#
# Usage:
#   bash run_full_test_v2.sh              # Use existing Rimata data, test libraries
#   bash run_full_test_v2.sh --refresh-rimata  # Refetch Rimata data, then test

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DATA_DIR="$REPO_DIR/test/data"
INPUT_FILE="$TEST_DATA_DIR/Ρήματα_Input_for_rimata.tsv"
COMBINED_FILE="$TEST_DATA_DIR/Ρήματα_Combined.tsv"
COMBINED_ALL_FILE="$TEST_DATA_DIR/Ρήματα_All_Forms.tsv"
RESULTS_MOD_FILE="/tmp/results_modified.tsv"
RESULTS_ORIG_FILE="/tmp/results_original.tsv"
RESULTS_FILE="$TEST_DATA_DIR/Ρήματα_Test_Results_Comparison.tsv"

cd "$REPO_DIR"

echo "=========================================="
echo "Modern Greek Inflexion - Full Test Suite"
echo "=========================================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: venv not found"
    exit 1
fi

if [ ! -f "venv_original/bin/activate" ]; then
    echo "ERROR: venv_original not found"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

# Step 1: Fetch Rimata data (or skip if already exists)
echo "=========================================="
echo "Step 1: Fetch Rimata.app reference data"
echo "=========================================="

if [ -f "$COMBINED_FILE" ] && [ -s "$COMBINED_FILE" ] && [ ! "$1" = "--refresh-rimata" ]; then
    echo "Using existing Rimata data: $COMBINED_FILE"
    echo "(Use --refresh-rimata to refetch)"
    echo ""
else
    echo "Input: $INPUT_FILE"
    echo "Output: $COMBINED_FILE"
    echo ""

    source venv/bin/activate
    python3 fetch_rimata.py "$INPUT_FILE" > "$COMBINED_FILE" 2>test/data/fetch_rimata.log
    RIMATA_COUNT=$(grep -c "✓" test/data/fetch_rimata.log || true)
    echo "✓ Fetched Rimata aorist/future for $RIMATA_COUNT verbs"
    deactivate
    echo ""
fi

# Step 1b: Fetch ALL Rimata forms (or skip if exists)
echo "------------------------------------------"
echo "Step 1b: Fetch ALL Rimata.app forms"
echo "------------------------------------------"

if [ -f "$COMBINED_ALL_FILE" ] && [ -s "$COMBINED_ALL_FILE" ] && [ ! "$1" = "--refresh-rimata" ]; then
    echo "Using existing all-forms data: $COMBINED_ALL_FILE"
    echo ""
else
    source venv/bin/activate
    python3 fetch_rimata_all_forms.py "$INPUT_FILE" > "$COMBINED_ALL_FILE" 2>test/data/fetch_rimata_all.log
    RIMATA_COUNT=$(grep -c "✓" test/data/fetch_rimata_all.log || true)
    echo "✓ Fetched all Rimata forms for $RIMATA_COUNT verbs"
    deactivate
    echo ""
fi
echo ""

# Step 2: Test modified library
echo "=========================================="
echo "Step 2: Test modified library (venv)"
echo "=========================================="
echo ""

source venv/bin/activate
python3 test_modified_lib.py "$COMBINED_FILE" > "$RESULTS_MOD_FILE" 2>test/data/test_modified.log
RESULT=$?
deactivate

if [ $RESULT -eq 0 ] && [ -s "$RESULTS_MOD_FILE" ]; then
    echo "✓ Tested modified library"
else
    echo "✗ Error testing modified library (exit code $RESULT)"
    cat test/data/test_modified.log >&2
fi
echo ""

# Step 3: Test original library
echo "=========================================="
echo "Step 3: Test original library v2.0.7 (venv_original)"
echo "=========================================="
echo ""

source venv_original/bin/activate
python3 test_original_lib.py "$COMBINED_FILE" > "$RESULTS_ORIG_FILE" 2>test/data/test_original.log
RESULT=$?
deactivate

if [ $RESULT -eq 0 ] && [ -s "$RESULTS_ORIG_FILE" ]; then
    echo "✓ Tested original library"
else
    echo "✗ Error testing original library (exit code $RESULT)"
    cat test/data/test_original.log >&2
fi
echo ""

# Step 4: Compare results (actual forms with +/- indicators)
echo "=========================================="
echo "Step 4: Compare results"
echo "=========================================="
echo ""

source venv/bin/activate
python3 compare_forms.py "$RESULTS_MOD_FILE" "$RESULTS_ORIG_FILE" > "$RESULTS_FILE" 2>test/data/test_comparison.log
deactivate

echo "✓ Comparison complete"
cat test/data/test_comparison.log
echo ""

# Step 5: Show summary
echo "=========================================="
echo "Step 5: Results Summary"
echo "=========================================="
echo ""

source venv/bin/activate
python3 << 'PYTHON_EOF'
import pandas as pd

df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')

print(f"Total verbs tested: {len(df)}")
print("")

# Count (+) matches
aor_mod_pass = df['Aorist_Modified'].str.contains(r'\(\+\)', na=False).sum()
aor_orig_pass = df['Aorist_Original'].str.contains(r'\(\+\)', na=False).sum()
fut_mod_pass = df['Future_Modified'].str.contains(r'\(\+\)', na=False).sum()
fut_orig_pass = df['Future_Original'].str.contains(r'\(\+\)', na=False).sum()

print(f"Aorist (+) Modified: {aor_mod_pass}/{len(df)}  Original: {aor_orig_pass}/{len(df)}")
print(f"Future (+) Modified: {fut_mod_pass}/{len(df)}  Original: {fut_orig_pass}/{len(df)}")
print("")

improved = (df['Change'] == 'IMPROVED').sum()
regressed = (df['Change'] == 'REGRESSED').sum()
print(f"Improvements: {improved}")
print(f"Regressions: {regressed}")
print("")

if regressed > 0:
    print("Regressions:")
    reg_df = df[df['Change'] == 'REGRESSED']
    for idx, row in reg_df.iterrows():
        print(f"  {row['Ρήμα']:20} Aor: {str(row['Aorist_Modified']):25} Fut: {row['Future_Modified']}")
    print("")

print(f"Results: test/data/Ρήματα_Test_Results_Comparison.tsv")
print(f"All Rimata forms: test/data/Ρήματα_All_Forms.tsv")
PYTHON_EOF
deactivate

echo ""
echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
echo ""
echo "Results file: $RESULTS_FILE"
echo "Log files:"
echo "  - test/data/fetch_rimata.log"
echo "  - test/data/fetch_rimata_all.log"
echo "  - test/data/test_modified.log"
echo "  - test/data/test_original.log"
echo "  - test/data/test_comparison.log"
echo ""
echo "View results:"
echo "  libreoffice $RESULTS_FILE"
echo "  libreoffice $COMBINED_ALL_FILE"
echo ""
