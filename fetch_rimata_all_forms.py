#!/usr/bin/env python3
"""
Fetch ALL verb forms from Rimata.app and save to TSV.

Reads TSV from file or stdin with verb column,
queries Rimata.app for each verb to extract all available forms,
outputs extended TSV with all forms to stdout.

Usage:
    python3 fetch_rimata_all_forms.py input.tsv > output_with_rimata.tsv
    cat input.tsv | python3 fetch_rimata_all_forms.py > output_with_rimata.tsv
"""

import sys
import urllib.request
import urllib.parse
import urllib.error
import re
import time
import pandas as pd
from io import StringIO

def fetch_all_rimata_forms(verb):
    """Fetch all verb forms from rimata.app for a verb.

    Returns dict with all available forms extracted from HTML.
    """
    clean_verb = verb.split('/')[0].strip()

    if not clean_verb:
        return {}

    encoded = urllib.parse.quote(clean_verb)
    url = f"https://rimata.app/verb/{encoded}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8')

        forms = {}

        # Extract all <strong>Label:</strong> VALUE</li> patterns
        pattern = r'<strong>([^<]+):</strong>\s*([^<]+)</li>'
        for match in re.finditer(pattern, html):
            label = match.group(1).strip()
            value = match.group(2).strip()

            # Map Greek labels to English keys
            label_map = {
                'Aorist': 'aorist',
                'Αόριστος': 'aorist',
                'Future': 'future',
                'Μέλλοντας': 'future',
                'Imperfect': 'imperfect',
                'Παρατατικός': 'imperfect',
                'Perfect': 'perfect',
                'Παρακείμενος': 'perfect',
                'Present': 'present',
                'Ενεστώτας': 'present',
                'Subjunctive': 'subjunctive',
                'Υποτακτική': 'subjunctive',
                'Imperative': 'imperative',
                'Προστακτική': 'imperative',
            }

            key = label_map.get(label, label.lower())
            if key not in forms:
                forms[key] = value

        return forms

    except urllib.error.HTTPError as e:
        return {'error': f'HTTP {e.code}'}
    except urllib.error.URLError as e:
        return {'error': f'URLError: {e.reason}'}
    except Exception as e:
        return {'error': str(e)}

def main():
    """Read verbs, fetch all Rimata forms, output extended TSV."""

    try:
        # Read TSV from stdin or file
        if len(sys.argv) > 1:
            df = pd.read_csv(sys.argv[1], sep='\t')
        else:
            input_tsv = sys.stdin.read()
            df = pd.read_csv(StringIO(input_tsv), sep='\t')

        # Find verb column
        verb_col = None
        for col in ['Ενεστώτας', 'Verb', 'Present']:
            if col in df.columns:
                verb_col = col
                break

        if verb_col is None:
            print("ERROR: No verb column found", file=sys.stderr)
            sys.exit(1)

        # Collect all forms
        rimata_present = []
        rimata_aorist = []
        rimata_imperfect = []
        rimata_future = []
        rimata_perfect = []
        rimata_subjunctive = []
        rimata_imperative = []
        rimata_notes = []

        # Fetch data for each verb
        total = len(df)
        for idx, row in df.iterrows():
            verb = row[verb_col]

            if pd.isna(verb) or str(verb).strip() == '':
                rimata_present.append('')
                rimata_aorist.append('')
                rimata_imperfect.append('')
                rimata_future.append('')
                rimata_perfect.append('')
                rimata_subjunctive.append('')
                rimata_imperative.append('')
                rimata_notes.append('')
                print(f"[{idx+1}/{total}] SKIP (empty)", file=sys.stderr)
                continue

            forms = fetch_all_rimata_forms(str(verb))

            rimata_present.append(forms.get('present', ''))
            rimata_aorist.append(forms.get('aorist', ''))
            rimata_imperfect.append(forms.get('imperfect', ''))
            rimata_future.append(forms.get('future', ''))
            rimata_perfect.append(forms.get('perfect', ''))
            rimata_subjunctive.append(forms.get('subjunctive', ''))
            rimata_imperative.append(forms.get('imperative', ''))
            rimata_notes.append(forms.get('error', ''))

            status = '✓' if not forms.get('error') else '✗'
            print(f"[{idx+1}/{total}] {status} {verb:20} forms: {len([v for v in forms.values() if v])}",
                  file=sys.stderr)

            # Be polite to server
            time.sleep(0.5)

        # Add all form columns to dataframe
        df['Rimata_Present'] = rimata_present
        df['Rimata_Aorist'] = rimata_aorist
        df['Rimata_Imperfect'] = rimata_imperfect
        df['Rimata_Future'] = rimata_future
        df['Rimata_Perfect'] = rimata_perfect
        df['Rimata_Subjunctive'] = rimata_subjunctive
        df['Rimata_Imperative'] = rimata_imperative
        df['Rimata_Note'] = rimata_notes

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
