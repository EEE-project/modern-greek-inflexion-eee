#!/usr/bin/env python3
"""
Test modified library version.

Reads TSV from stdin with verbs, tests with modified library,
outputs results as TSV to stdout.

Usage (from modified venv):
    source venv/bin/activate
    cat verbs.tsv | python3 test_modified_lib.py > results_modified.tsv
"""

import sys
import pandas as pd
from io import StringIO
from modern_greek_inflexion import Verb

def test_verb_form(verb_obj, form_type='aorist'):
    """Extract verb form from Verb object."""
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

def main():
    """Read verbs, test with modified library, output results."""
    try:
        # Read TSV from stdin or file
        if len(sys.argv) > 1:
            # If filename provided as argument, read from file
            df = pd.read_csv(sys.argv[1], sep='\t')
        else:
            # Otherwise read from stdin
            input_tsv = sys.stdin.read()
            df = pd.read_csv(StringIO(input_tsv), sep='\t')

        aorist_results = []
        future_results = []

        for idx, row in df.iterrows():
            verb = row['Ενεστώτας']

            if pd.isna(verb) or str(verb).strip() == '':
                aorist_results.append('')
                future_results.append('')
                print(f"[{idx+1}/{len(df)}] SKIP (empty)", file=sys.stderr)
                continue

            try:
                v = Verb(str(verb))
                aorist = test_verb_form(v, 'aorist')
                future = test_verb_form(v, 'future')

                aorist_results.append(aorist)
                future_results.append(future)

                status = '✓' if aorist or future else '✗'
                print(f"[{idx+1}/{len(df)}] {status} {verb:20} aor: {aorist:15} fut: {future:20}",
                      file=sys.stderr)
            except Exception as e:
                aorist_results.append('ERROR')
                future_results.append('ERROR')
                print(f"[{idx+1}/{len(df)}] ✗ {verb:20} ERROR: {str(e)[:40]}", file=sys.stderr)

        # Add results columns to dataframe
        df['Aorist_Modified'] = aorist_results
        df['Future_Modified'] = future_results

        # Output to stdout
        output = df.to_csv(None, sep='\t', index=False)
        sys.stdout.write(output)
        sys.stdout.flush()

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
