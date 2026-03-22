#!/bin/bash
# Complete test workflow: fetch Rimata data and compare libraries

set -e

REPO_DIR="/home/sadov/work/greek/git/github/modern-greek-inflexion-eee"
TEST_DATA_DIR="$REPO_DIR/test/data"
INPUT_FILE="$TEST_DATA_DIR/Ρήματα_Input_for_rimata.tsv"
COMBINED_FILE="$TEST_DATA_DIR/Ρήματα_Combined.tsv"
RESULTS_FILE="$TEST_DATA_DIR/Ρήματα_Test_Results_Comparison.tsv"

cd "$REPO_DIR"
source venv/bin/activate

echo "=========================================="
echo "Modern Greek Inflexion - Full Test Suite"
echo "=========================================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."
if [ ! -d "venv" ]; then
    echo "ERROR: venv directory not found"
    exit 1
fi

if [ ! -d "venv_original" ]; then
    echo "ERROR: venv_original directory not found (install with: python3 -m venv venv_original && source venv_original/bin/activate && pip install modern-greek-inflexion==2.0.7)"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

# Step 1: Fetch Rimata data
echo "=========================================="
echo "Step 1: Fetch Rimata.app reference data"
echo "=========================================="
echo "Input: $INPUT_FILE"
echo "Output: $COMBINED_FILE"
echo ""

python3 fetch_rimata.py < "$INPUT_FILE" > "$COMBINED_FILE" 2>test/data/fetch_rimata.log
RIMATA_COUNT=$(grep -c "✓" test/data/fetch_rimata.log || true)
echo "✓ Fetched Rimata data for $RIMATA_COUNT verbs"
echo ""

# Step 2: Compare libraries
echo "=========================================="
echo "Step 2: Compare library versions"
echo "=========================================="
echo "Testing: Modified (venv) vs Original (v2.0.7)"
echo "Input: $COMBINED_FILE"
echo "Output: $RESULTS_FILE"
echo ""

python3 test_library_comparison.py < "$COMBINED_FILE" > "$RESULTS_FILE" 2>test/data/test_comparison.log

# Parse results from log
TOTAL=$(grep -o '\[1/[0-9]*\]' test/data/test_comparison.log | head -1 | grep -o '[0-9]*')
IMPROVEMENTS=$(grep "^Total verbs:" test/data/test_comparison.log)
REGRESSIONS=$(grep "^Improvements:" test/data/test_comparison.log)

echo "✓ Completed library comparison"
echo ""

# Step 3: Show summary
echo "=========================================="
echo "Step 3: Results Summary"
echo "=========================================="
echo ""

if [ -f "$RESULTS_FILE" ]; then
    python3 << 'PYTHON_EOF'
import pandas as pd
import sys

df = pd.read_csv('test/data/Ρήματα_Test_Results_Comparison.tsv', sep='\t')

print(f"Total verbs tested: {len(df)}")
print("")

# Aorist stats
aor_mod_pass = (df['Aorist_Modified'] == 'PASS').sum()
aor_orig_pass = (df['Aorist_Original'] == 'PASS').sum()
print(f"Aorist PASS (Modified): {aor_mod_pass}/{len(df)} ({aor_mod_pass*100//len(df)}%)")
print(f"Aorist PASS (Original): {aor_orig_pass}/{len(df)} ({aor_orig_pass*100//len(df)}%)")
print("")

# Future stats
fut_mod_pass = (df['Future_Modified'] == 'PASS').sum()
fut_orig_pass = (df['Future_Original'] == 'PASS').sum()
print(f"Future PASS (Modified): {fut_mod_pass}/{len(df)} ({fut_mod_pass*100//len(df)}%)")
print(f"Future PASS (Original): {fut_orig_pass}/{len(df)} ({fut_orig_pass*100//len(df)}%)")
print("")

# Changes
improved = (df['Overall_Change'] == 'IMPROVED').sum()
regressed = (df['Overall_Change'] == 'REGRESSED').sum()
print(f"Improvements: {improved}")
print(f"Regressions: {regressed}")
print("")

if regressed > 0:
    print("Regressions found:")
    reg_df = df[df['Overall_Change'] == 'REGRESSED']
    for idx, row in reg_df.iterrows():
        print(f"  • {row['Ρήμα']:20} Aorist: {row['Aorist_Change']:15} Future: {row['Future_Change']:15}")
    print("")

print("✓ Results saved to: test/data/Ρήματα_Test_Results_Comparison.tsv")
PYTHON_EOF
fi

echo ""
echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
echo ""
echo "Results file: $RESULTS_FILE"
echo "Log files:"
echo "  - test/data/fetch_rimata.log"
echo "  - test/data/test_comparison.log"
echo ""
echo "View results:"
echo "  libreoffice $RESULTS_FILE"
echo "  head $RESULTS_FILE"
echo ""
