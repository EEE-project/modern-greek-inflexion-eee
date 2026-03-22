#!/usr/bin/env python3
"""
Compare test results from both library versions.

Reads results from two TSV files (modified and original library results)
and generates comparison output with PASS/FAIL and change indicators.

Usage:
    python3 compare_test_results.py <results_modified.tsv> <results_original.tsv> > comparison.tsv
"""

import sys
import pandas as pd

def compare_results(expected, modified, original):
    """Compare test results and determine status."""
    mod_pass = (modified == expected and modified != '' and modified != 'ERROR')
    orig_pass = (original == expected and original != '' and original != 'ERROR')

    mod_status = 'PASS' if mod_pass else 'FAIL'
    orig_status = 'PASS' if orig_pass else 'FAIL'

    # Determine change
    if orig_pass and not mod_pass:
        change = 'REGRESSED'
    elif not orig_pass and mod_pass:
        change = 'IMPROVED'
    elif orig_pass and mod_pass:
        change = '—'
    else:
        change = '—'

    return mod_status, orig_status, change

def main():
    """Combine and compare test results from both libraries."""

    if len(sys.argv) < 3:
        print("Usage: python3 compare_test_results.py <modified.tsv> <original.tsv> > comparison.tsv",
              file=sys.stderr)
        sys.exit(1)

    modified_file = sys.argv[1]
    original_file = sys.argv[2]

    try:
        # Read both result files
        df_mod = pd.read_csv(modified_file, sep='\t')
        df_orig = pd.read_csv(original_file, sep='\t')

        # Merge on verb column
        result_df = df_mod[['Ενεστώτας', 'Μετάφραση', 'Αόριστος', 'Μέλλοντας',
                            'Rimata_Αόριστος', 'Rimata_Μέλλοντας']].copy()

        # Add modified results
        result_df['Aorist_Modified'] = df_mod['Aorist_Modified']
        result_df['Future_Modified'] = df_mod['Future_Modified']

        # Add original results
        result_df['Aorist_Original'] = df_orig['Aorist_Original']
        result_df['Future_Original'] = df_orig['Future_Original']

        # Rename expected columns
        result_df = result_df.rename(columns={
            'Ενεστώτας': 'Ρήμα',
            'Αόριστος': 'Aorist_Expected',
            'Μέλλοντας': 'Future_Expected',
            'Μετάφραση': 'Translation'
        })

        # Add comparison columns
        aorist_change = []
        future_change = []
        overall_change = []

        for idx, row in result_df.iterrows():
            aor_mod, aor_orig, aor_chg = compare_results(
                row['Aorist_Expected'],
                row['Aorist_Modified'],
                row['Aorist_Original']
            )
            result_df.loc[idx, 'Aorist_Modified'] = aor_mod
            result_df.loc[idx, 'Aorist_Original'] = aor_orig
            aorist_change.append(aor_chg)

            fut_mod, fut_orig, fut_chg = compare_results(
                row['Future_Expected'],
                row['Future_Modified'],
                row['Future_Original']
            )
            result_df.loc[idx, 'Future_Modified'] = fut_mod
            result_df.loc[idx, 'Future_Original'] = fut_orig
            future_change.append(fut_chg)

            # Overall change
            if aor_chg == 'IMPROVED' or fut_chg == 'IMPROVED':
                overall_change.append('IMPROVED')
            elif aor_chg == 'REGRESSED' or fut_chg == 'REGRESSED':
                overall_change.append('REGRESSED')
            else:
                overall_change.append('—')

        result_df['Aorist_Change'] = aorist_change
        result_df['Future_Change'] = future_change
        result_df['Overall_Change'] = overall_change
        result_df['Comment'] = ''

        # Reorder columns
        col_order = [
            'Ρήμα', 'Translation', 'Aorist_Expected', 'Future_Expected',
            'Rimata_Αόριστος', 'Rimata_Μέλλοντας',
            'Aorist_Modified', 'Future_Modified', 'Aorist_Original', 'Future_Original',
            'Aorist_Change', 'Future_Change', 'Overall_Change', 'Comment'
        ]
        result_df = result_df[col_order]

        # Rename Ρήμα column back if needed
        if 'Ενεστώτας' in result_df.columns:
            result_df = result_df.rename(columns={'Ενεστώτας': 'Ρήμα'})

        # Output to stdout
        output = result_df.to_csv(None, sep='\t', index=False)
        sys.stdout.write(output)
        sys.stdout.flush()

        # Print summary to stderr
        print(f"\n=== SUMMARY ===", file=sys.stderr)
        print(f"Total verbs: {len(result_df)}", file=sys.stderr)
        improved = (pd.Series(overall_change) == 'IMPROVED').sum()
        regressed = (pd.Series(overall_change) == 'REGRESSED').sum()
        print(f"Improvements: {improved}", file=sys.stderr)
        print(f"Regressions: {regressed}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
