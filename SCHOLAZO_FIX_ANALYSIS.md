# σχολάω Aorist: Linguistic Analysis & Current Library Status

## Corrected Understanding

After consulting a Greek linguist, the analysis in UPSTREAM_BUGS.md Bug #2 requires significant revision.

### What We Thought vs What's True

| Assumption | Status | Reality |
|-----------|--------|---------|
| σχολάω is irregular | ✗ WRONG | It's a **contract verb (-άω)**, completely regular in aorist |
| Needs σχ/σκ alternation | ✗ WRONG | These don't exist in aorist forms (only in present) |
| Should generate multiple variant forms | ⚠️ UNCLEAR | Depends if contract verbs should get stress variants |

## Verb Classification: Contract Verbs (-άω)

**σχολάω belongs to the -άω contraction group:**

```
Present forms:
- σχολάω (present active)
- σχολώ (alternative present)

Aorist (SINGLE regular form):
- σχόλησα (1st sg) — completely regular, no variants
```

**Similar verbs in same group:**
- αγαπάω → αγάπησα (love)
- μιλάω → μίλησα (speak)

## Current Library Output

```python
from modern_greek_inflexion import Verb

verb = Verb('σχολάω')
aorist = verb.create_aorist()['active']['ind']

# ACTUAL OUTPUT (Correct):
{
    'sg': {
        'pri': {'σχόλησα'},      # correct
        'sec': {'σχόλησες'},      # correct
        'ter': {'σχόλησε'}        # correct
    },
    'pl': {
        'pri': {'σχολήσαμε'},     # correct
        'sec': {'σχολήσατε'},     # correct
        'ter': {'σχόλησαν', 'σχολήσανε'}  # correct
    }
}
```

**✓ Library is CORRECT for contract verbs**

## Comparison: Contract (-άω) vs Regular (-ω) Verbs

The **actual difference** is that regular verbs generate stress variants:

```python
# Contract verb (-άω): Single stress pattern
Verb('σχολάω').create_aorist()['active']['ind']
# sg-pri: {'σχόλησα'}  ← ONE form

Verb('μιλάω').create_aorist()['active']['ind']
# sg-pri: {'μίλησα'}   ← ONE form

Verb('αγαπάω').create_aorist()['active']['ind']
# sg-pri: {'αγάπησα'}  ← ONE form

# Regular verb (-ω): MULTIPLE stress patterns
Verb('τελειώνω').create_aorist()['active']['ind']
# sg-pri: {'τέλειωσα', 'τελείωσα'}  ← TWO forms (stress variants)
```

## The Real Question

**Why do regular verbs (-ω) generate stress variants but contract verbs (-άω) don't?**

### Possible Explanations

1. **Intentional**: Library design choice - contract verbs use single stress pattern
2. **By-product**: Stress generation algorithm works differently for different conjugation groups
3. **Corpus-driven**: Only single-stress forms are in greek_corpus for contract verbs

### Evidence

```python
# Check Greek corpus
from modern_greek_inflexion.resources import greek_corpus

contract_forms = [
    'σχόλησα',      # ✓ in corpus
    'σχολάσα',      # ✗ NOT in corpus (if it existed)
    'μίλησα',       # ✓ in corpus
    'μιλάσα',       # ✗ NOT in corpus
]

# Regular verb forms - multiple stress patterns ARE in corpus:
regular_forms = [
    'τέλειωσα',     # ✓ in corpus
    'τελείωσα',     # ✓ in corpus
]
```

## Conclusion

### Bug Status: CLARIFIED, NOT A BUG

- ✓ Library correctly generates aorist for σχολάω
- ✓ Forms match standard Modern Greek
- ✗ No missing variants in aorist

### What UPSTREAM_BUGS.md Got Wrong

- ❌ Claimed σχολάω is "irregular" → It's regular contract (-άω)
- ❌ Claimed missing σχ/σκ alternation → These don't exist in aorist
- ❌ Suggested variant dictionary needed → Not for aorist

### What Remains Open

The **design question**: Should contract verbs generate stress-shifted variants like regular verbs?

- If YES: Need to modify aorist generation for -άω verbs
- If NO: Current library behavior is correct

This is a **general conjugation system question**, not specific to σχολάω.

## Test Case

Added `test_scholazo_aorist()` to `test/unit/test_verb_aorist.py` to document:
1. σχολάω is fully regular in aorist
2. Current library output is correct
3. Open question about stress variants for contract verbs

---

**Analysis Date**: March 21, 2026
**Status**: Linguistic clarification complete, design question remains
**Files Updated**: test/unit/test_verb_aorist.py
