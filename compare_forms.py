#!/usr/bin/env python3
"""
Compare verb forms from both library versions, showing actual forms with +/- indicators.

Reads results from modified and original library test TSVs.
For each verb shows: actual form generated (+) if matches expected, (-) if not.

Usage:
    python3 compare_forms.py <results_modified.tsv> <results_original.tsv> > comparison.tsv
"""

import sys
import pandas as pd


def normalize_form(form):
    """Normalize a verb form for comparison.

    Strips θα/να prefixes so library output can be compared with Rimata reference.
    """
    if pd.isna(form):
        return ''
    s = str(form).strip()
    # Strip θα / να prefixes (Rimata includes them, library doesn't)
    for prefix in ['θα ', 'να ']:
        if s.startswith(prefix):
            s = s[len(prefix):]
    # Take first alternative if comma-separated (e.g. "σχολάω, σχολώ")
    if ',' in s:
        s = s.split(',')[0].strip()
    return s


def match_indicator(generated, expected):
    """Return (+) if generated matches expected, (-) if not, or empty if no data."""
    gen = normalize_form(generated)
    exp = normalize_form(expected)

    if not gen and not exp:
        return ''
    if not gen:
        return '(-)'
    if not exp:
        return '(?)'  # no expected value to compare against
    if gen == exp:
        return '(+)'
    return '(-)'


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 compare_forms.py <modified.tsv> <original.tsv> > comparison.tsv",
              file=sys.stderr)
        sys.exit(1)

    modified_file = sys.argv[1]
    original_file = sys.argv[2]

    try:
        df_mod = pd.read_csv(modified_file, sep='\t')
        df_orig = pd.read_csv(original_file, sep='\t')

        rows = []
        for idx in range(len(df_mod)):
            mod = df_mod.iloc[idx]
            orig = df_orig.iloc[idx]

            verb = mod['Ενεστώτας']
            translation = mod.get('Μετάφραση', '')

            # Expected forms from input TSV
            aor_expected = str(mod.get('Αόριστος', '')) if pd.notna(mod.get('Αόριστος', '')) else ''
            fut_expected = str(mod.get('Μέλλοντας', '')) if pd.notna(mod.get('Μέλλοντας', '')) else ''

            # Rimata reference (if available)
            rimata_aor = str(mod.get('Rimata_Αόριστος', '')) if pd.notna(mod.get('Rimata_Αόριστος', '')) else ''
            rimata_fut = str(mod.get('Rimata_Μέλλοντας', '')) if pd.notna(mod.get('Rimata_Μέλλοντας', '')) else ''

            # Library results
            aor_mod = str(mod.get('Aorist_Modified', '')) if pd.notna(mod.get('Aorist_Modified', '')) else ''
            fut_mod = str(mod.get('Future_Modified', '')) if pd.notna(mod.get('Future_Modified', '')) else ''
            aor_orig = str(orig.get('Aorist_Original', '')) if pd.notna(orig.get('Aorist_Original', '')) else ''
            fut_orig = str(orig.get('Future_Original', '')) if pd.notna(orig.get('Future_Original', '')) else ''

            # Compare against expected (from input TSV), normalized
            aor_mod_ind = match_indicator(aor_mod, aor_expected)
            fut_mod_ind = match_indicator(fut_mod, normalize_form(fut_expected))
            aor_orig_ind = match_indicator(aor_orig, aor_expected)
            fut_orig_ind = match_indicator(fut_orig, normalize_form(fut_expected))

            # Also compare against Rimata
            aor_mod_rimata = match_indicator(aor_mod, rimata_aor)
            fut_mod_rimata = match_indicator(fut_mod, normalize_form(rimata_fut))

            # Overall change: improved if mod matches where orig didn't, regressed if opposite
            aor_mod_ok = normalize_form(aor_mod) == normalize_form(aor_expected) and aor_mod != ''
            aor_orig_ok = normalize_form(aor_orig) == normalize_form(aor_expected) and aor_orig != ''
            fut_mod_ok = normalize_form(fut_mod) == normalize_form(fut_expected) and fut_mod != ''
            fut_orig_ok = normalize_form(fut_orig) == normalize_form(fut_expected) and fut_orig != ''

            if (aor_mod_ok and not aor_orig_ok) or (fut_mod_ok and not fut_orig_ok):
                change = 'IMPROVED'
            elif (not aor_mod_ok and aor_orig_ok) or (not fut_mod_ok and fut_orig_ok):
                change = 'REGRESSED'
            else:
                change = ''

            rows.append({
                'Ρήμα': verb,
                'Translation': translation,
                'Aorist_Expected': aor_expected,
                'Aorist_Rimata': rimata_aor,
                'Aorist_Modified': f"{aor_mod} {aor_mod_ind}".strip() if aor_mod or aor_mod_ind else '',
                'Aorist_Original': f"{aor_orig} {aor_orig_ind}".strip() if aor_orig or aor_orig_ind else '',
                'Aorist_vs_Rimata': aor_mod_rimata,
                'Future_Expected': normalize_form(fut_expected),
                'Future_Rimata': normalize_form(rimata_fut),
                'Future_Modified': f"{fut_mod} {fut_mod_ind}".strip() if fut_mod or fut_mod_ind else '',
                'Future_Original': f"{fut_orig} {fut_orig_ind}".strip() if fut_orig or fut_orig_ind else '',
                'Future_vs_Rimata': fut_mod_rimata,
                'Change': change,
            })

        result_df = pd.DataFrame(rows)

        # Output
        output = result_df.to_csv(None, sep='\t', index=False)
        sys.stdout.write(output)
        sys.stdout.flush()

        # Summary to stderr
        total = len(result_df)
        aor_mod_pass = sum(1 for r in rows if '(+)' in r.get('Aorist_Modified', ''))
        aor_orig_pass = sum(1 for r in rows if '(+)' in r.get('Aorist_Original', ''))
        fut_mod_pass = sum(1 for r in rows if '(+)' in r.get('Future_Modified', ''))
        fut_orig_pass = sum(1 for r in rows if '(+)' in r.get('Future_Original', ''))
        improved = sum(1 for r in rows if r['Change'] == 'IMPROVED')
        regressed = sum(1 for r in rows if r['Change'] == 'REGRESSED')

        print(f"\n=== SUMMARY ===", file=sys.stderr)
        print(f"Total verbs: {total}", file=sys.stderr)
        print(f"Aorist (+) Modified: {aor_mod_pass}/{total}  Original: {aor_orig_pass}/{total}", file=sys.stderr)
        print(f"Future (+) Modified: {fut_mod_pass}/{total}  Original: {fut_orig_pass}/{total}", file=sys.stderr)
        print(f"Improvements: {improved}  Regressions: {regressed}", file=sys.stderr)

        if regressed > 0:
            print(f"\nRegressions:", file=sys.stderr)
            for r in rows:
                if r['Change'] == 'REGRESSED':
                    print(f"  {r['Ρήμα']:20} Aor: {r['Aorist_Modified']:25} Fut: {r['Future_Modified']}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
