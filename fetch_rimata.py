#!/usr/bin/env python3
"""
Fetch verb forms from Rimata.app and add to TSV.

Reads TSV from stdin with verb data, queries Rimata.app for each verb,
and outputs extended TSV to stdout with Rimata reference columns.

Usage:
    cat input.tsv | python3 fetch_rimata.py > output.tsv
    python3 fetch_rimata.py < input.tsv > output.tsv
"""

import sys
import urllib.request
import urllib.parse
import urllib.error
import re
import time
import pandas as pd
from io import StringIO

def fetch_rimata(verb):
    """Fetch aorist and future from rimata.app for a verb.

    Args:
        verb: Greek verb in present form

    Returns:
        tuple: (aorist, future, error_note)
    """
    # Clean verb (remove alternatives like πάω/πηγαίνω)
    clean_verb = verb.split('/')[0].strip()

    if not clean_verb:
        return '', '', ''

    encoded = urllib.parse.quote(clean_verb)
    url = f"https://rimata.app/verb/{encoded}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8')

        # Extract aorist: <strong>Aorist:</strong> VALUE</li>
        aorist = ''
        m = re.search(r'<strong>Aorist:</strong>\s*([^<]+)</li>', html)
        if m:
            aorist = m.group(1).strip()

        # Extract future: <strong>Future:</strong> VALUE</li>
        future = ''
        m = re.search(r'<strong>Future:</strong>\s*([^<]+)</li>', html)
        if m:
            future = m.group(1).strip()

        return aorist, future, ''
    except urllib.error.HTTPError as e:
        return '', '', f'HTTP {e.code}'
    except urllib.error.URLError as e:
        return '', '', f'URLError: {e.reason}'
    except Exception as e:
        return '', '', str(e)

def main():
    """Read TSV from stdin or file, fetch Rimata data, output to stdout."""

    try:
        # Read TSV from stdin or file
        if len(sys.argv) > 1:
            # If filename provided as argument, read from file
            df = pd.read_csv(sys.argv[1], sep='\t')
        else:
            # Otherwise read from stdin
            input_tsv = sys.stdin.read()
            df = pd.read_csv(StringIO(input_tsv), sep='\t')

        # Check if input has verb column
        verb_col = None
        for col in ['Ενεστώτας', 'Verb', 'Present']:
            if col in df.columns:
                verb_col = col
                break

        if verb_col is None:
            print("ERROR: No verb column found (expected: Ενεστώτας, Verb, or Present)",
                  file=sys.stderr)
            sys.exit(1)

        # Initialize output columns
        rimata_aorist = []
        rimata_future = []
        rimata_notes = []

        # Fetch data for each verb
        total = len(df)
        for idx, row in df.iterrows():
            verb = row[verb_col]

            if pd.isna(verb) or str(verb).strip() == '':
                rimata_aorist.append('')
                rimata_future.append('')
                rimata_notes.append('')
                print(f"[{idx+1}/{total}] SKIP (empty)", file=sys.stderr)
                continue

            aor, fut, note = fetch_rimata(str(verb))
            rimata_aorist.append(aor)
            rimata_future.append(fut)
            rimata_notes.append(note)

            status = '✓' if aor or fut else '✗'
            print(f"[{idx+1}/{total}] {status} {verb}", file=sys.stderr)

            # Be polite to the server
            time.sleep(0.5)

        # Add columns to dataframe
        df['Rimata_Αόριστος'] = rimata_aorist
        df['Rimata_Μέλλοντας'] = rimata_future
        df['Rimata_Note'] = rimata_notes

        # Output to stdout (use buffer to avoid encoding issues)
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
        sys.exit(1)

if __name__ == '__main__':
    main()
