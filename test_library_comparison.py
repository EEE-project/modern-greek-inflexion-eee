#!/usr/bin/env python3
"""
Test library comparison: Original v2.0.7 vs Modified library.

Reads TSV from stdin with verb data (including Rimata reference columns),
tests both library versions, and outputs comparison TSV to stdout.

Usage:
    cat verbs_with_rimata.tsv | python3 test_library_comparison.py > comparison.tsv
    python3 test_library_comparison.py < verbs_with_rimata.tsv > comparison.tsv
"""

import sys
import pandas as pd
from io import StringIO

def test_verb_form(verb_obj, form_type='aorist'):
    """Extract verb form from modern_greek_inflexion Verb object.

    Args:
        verb_obj: Verb object
        form_type: 'aorist' or 'future'

    Returns:
        str: First form in set or empty string if form not found
    """
    try:
        if form_type == 'aorist':
            result = verb_obj.create_aorist()
            forms = result['active']['ind']['sg']['pri']
        elif form_type == 'future':
            result = verb_obj.all()
            forms = result['conjunctive']['active']['ind']['sg']['pri']
        else:
            return ''

        if isinstance(forms, set) and len(forms) > 0:
            return list(forms)[0]
        elif isinstance(forms, str):
            return forms
        else:
            return ''
    except Exception as e:
        return ''

def test_with_library(df, library_name='modified'):
    """Test verbs with specified library version.

    Args:
        df: DataFrame with verb column 'Ενεστώτας'
        library_name: 'modified' or 'original'

    Returns:
        tuple: (aorist_results, future_results)
    """
    if library_name == 'original':
        # Use original library from venv_original
        sys.path.insert(0, '/home/sadov/work/greek/git/github/modern-greek-inflexion-eee/venv_original/lib/python3.12/site-packages')

    try:
        from modern_greek_inflexion import Verb
    except ImportError:
        print(f"ERROR: Could not import modern_greek_inflexion for {library_name}", file=sys.stderr)
        sys.exit(1)

    aorist_results = []
    future_results = []

    for idx, row in df.iterrows():
        verb = row['Ενεστώτας']

        if pd.isna(verb) or str(verb).strip() == '':
            aorist_results.append('')
            future_results.append('')
            continue

        try:
            v = Verb(str(verb))
            aorist = test_verb_form(v, 'aorist')
            future = test_verb_form(v, 'future')

            aorist_results.append(aorist)
            future_results.append(future)

            status = '✓' if aorist or future else '✗'
            print(f"[{library_name:8}] {status} {verb:20} aor: {aorist:15} fut: {future:20}",
                  file=sys.stderr)
        except Exception as e:
            aorist_results.append('ERROR')
            future_results.append('ERROR')
            print(f"[{library_name:8}] ✗ {verb:20} ERROR: {str(e)[:40]}", file=sys.stderr)

    return aorist_results, future_results

def compare_results(expected, modified, original):
    """Compare test results and determine status.

    Returns: (status, 'PASS'/'FAIL' for modified, 'PASS'/'FAIL' for original, change_description)
    """
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
    """Read verbs with Rimata data, test both libraries, output comparison."""

    try:
        # Read TSV from stdin
        input_tsv = sys.stdin.read()
        df = pd.read_csv(StringIO(input_tsv), sep='\t')

        print(f"Testing {len(df)} verbs...", file=sys.stderr)
        print(f"Testing with MODIFIED library (from venv)...", file=sys.stderr)

        # Test with modified library
        aorist_mod, future_mod = test_with_library(df, 'modified')

        print(f"\nTesting with ORIGINAL library (v2.0.7 from venv_original)...", file=sys.stderr)

        # Test with original library
        aorist_orig, future_orig = test_with_library(df, 'original')

        # Build comparison DataFrame
        result_df = pd.DataFrame({
            'Ρήμα': df['Ενεστώτας'],
            'Translation': df.get('Μετάφραση', ''),
            'Aorist_Expected': df.get('Αόριστος', ''),
            'Future_Expected': df.get('Μέλλοντας', ''),
            'Rimata_Αόριστος': df.get('Rimata_Αόριστος', ''),
            'Rimata_Μέλλοντας': df.get('Rimata_Μέλλοντας', ''),
            'Aorist_Modified': aorist_mod,
            'Future_Modified': future_mod,
            'Aorist_Original': aorist_orig,
            'Future_Original': future_orig,
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

    except pd.errors.ParserError as e:
        print(f"ERROR: Failed to parse TSV: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
