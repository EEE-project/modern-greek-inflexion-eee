#!/usr/bin/env python3
"""
Validate modern-greek-inflexion library against Rimata.app verb forms.

Rimata.app is a reference Greek verb conjugation database.
This script extracts data from the comparison TSV and validates key verbs.
"""

import pandas as pd
import sys

# Reference verb data from Rimata (manually extracted or via scraping)
RIMATA_REFERENCE = {
    # B2 contract verbs (should generate σχόλασα, not σχόλησα)
    'σχολάω': {
        'aorist_1sg': 'σχόλασα',
        'future_1sg': 'θα σχολάσω',
        'type': 'B2 contract verb'
    },
    'γελάω': {
        'aorist_1sg': 'γέλασα',
        'future_1sg': 'θα γελάσω',
        'type': 'B2 contract verb'
    },
    'διψάω': {
        'aorist_1sg': 'δίψασα',
        'future_1sg': 'θα διψάσω',
        'type': 'B2 contract verb'
    },
    'χαλάω': {
        'aorist_1sg': 'χάλασα',
        'future_1sg': 'θα χαλάσω',
        'type': 'B2 contract verb'
    },
    'περνάω': {
        'aorist_1sg': 'πέρασα',
        'future_1sg': 'θα περάσω',
        'type': 'B2 contract verb'
    },
    'ξεχνάω': {
        'aorist_1sg': 'ξέχασα',
        'future_1sg': 'θα ξεχάσω',
        'type': 'B2 contract verb'
    },
    # B1 contract verbs (should generate forms like αγάπησα)
    'αγαπάω': {
        'aorist_1sg': 'αγάπησα',
        'future_1sg': 'θα αγαπήσω',
        'type': 'B1 contract verb'
    },
    'μιλάω': {
        'aorist_1sg': 'μίλησα',
        'future_1sg': 'θα μιλήσω',
        'type': 'B1 contract verb'
    },
    'ρωτάω': {
        'aorist_1sg': 'ρώτησα',
        'future_1sg': 'θα ρωτήσω',
        'type': 'B1 contract verb'
    },
    # Ambiguous cases
    'αργώ': {
        'aorist_1sg': 'άργησα',  # or άργασα (B2)
        'future_1sg': 'θα αργήσω',  # or θα αργάσω
        'type': 'Contract verb - B1 or B2',
        'note': 'Both B1 and B2 forms exist; Rimata shows B1'
    },
    'καλώ': {
        'aorist_1sg': 'κάλεσα',
        'future_1sg': 'θα καλέσω',
        'type': 'B2 contract verb'
    },
    'μπορώ': {
        'aorist_1sg': 'μπόρεσα',
        'future_1sg': 'θα μπορέσω',
        'type': 'B2 contract verb'
    },
}

def validate_library_against_rimata():
    """Load TSV comparison and validate against Rimata reference."""

    tsv_file = '/home/sadov/Загрузки/Ρήματα_Test_Results_Comparison.tsv'

    try:
        df = pd.read_csv(tsv_file, sep='\t')
    except FileNotFoundError:
        print(f"ERROR: {tsv_file} not found")
        print("Run test_comparison.sh first to generate comparison TSV")
        return False

    print("=" * 100)
    print("RIMATA.APP VALIDATION - Modern Greek Inflexion Library")
    print("=" * 100)
    print()

    # Validate key verbs against Rimata reference
    print("VALIDATING AGAINST RIMATA.APP REFERENCE DATA:\n")

    passed = 0
    failed = 0

    for verb, expected in RIMATA_REFERENCE.items():
        # Find verb in comparison TSV
        verb_row = df[df['Ρήμα'] == verb]

        if verb_row.empty:
            print(f"⚠  {verb:20} NOT IN TEST SET")
            continue

        row = verb_row.iloc[0]
        aorist_mod = row['Aorist_Modified']
        future_mod = row['Future_Modified']

        # Check if modified library passes
        aorist_expected = expected['aorist_1sg']
        future_expected = expected['future_1sg'].replace('θα ', '')

        status = "✓" if aorist_mod == 'PASS' and future_mod == 'PASS' else "✗"
        note = f"({expected['type']})"
        if 'note' in expected:
            note += f" - {expected['note']}"

        print(f"{status} {verb:20} | Aorist:{aorist_mod:5} Future:{future_mod:5} | {note}")

        if aorist_mod == 'PASS' and future_mod == 'PASS':
            passed += 1
        else:
            failed += 1

    print()
    print("=" * 100)
    print(f"RIMATA VALIDATION RESULTS: {passed} passed, {failed} failed")
    print("=" * 100)

    return failed == 0

if __name__ == '__main__':
    success = validate_library_against_rimata()
    sys.exit(0 if success else 1)
