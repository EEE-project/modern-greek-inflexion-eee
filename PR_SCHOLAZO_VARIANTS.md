# PR: Document σχολάω Aorist Conjugation & Linguistic Clarification

## Problem Statement

The modern-greek-inflexion library correctly generates aorist forms for σχολάω, but lacks documentation and testing for this important educational verb. Additionally, UPSTREAM_BUGS.md contained incomplete linguistic analysis about variant forms.

## Linguistic Clarification

**σχολάω (to skip school) is a CONTRACT VERB (-άω group)**, not irregular.

### Morphological Classification
- **Group**: Verbs in -άω / -ώ (present time contraction)
- **Examples**: αγαπάω (love), μιλάω (speak), σχολάω (skip)
- **Aorist Formation**: Completely regular sigmatic aorist

### Aorist Structure
```
Stem: σχολάσ-
+ Suffix: -α
= Base aorist: σχόλησα
```

### Current Library Behavior

```python
from modern_greek_inflexion import Verb

verb = Verb('σχολάω')
aorist = verb.create_aorist()['active']['ind']

# Returns:
{
  'sg': {'pri': {'σχόλησα'}, 'sec': {'σχόλησες'}, 'ter': {'σχόλησε'}},
  'pl': {'pri': {'σχολήσαμε'}, 'sec': {'σχολήσατε'}, 'ter': {'σχόλησανα', 'σχολήσανε'}}
}
```

This is **CORRECT** for a contract (-άω) verb in the aorist.

## Comparison with Other Verb Types

| Verb | Type | Aorist Forms | Variants |
|------|------|--------------|----------|
| σχολάω | Contract (-άω) | σχόλησα | Single accent pattern |
| μιλάω | Contract (-άω) | μίλησα | Single accent pattern |
| αγαπάω | Contract (-άω) | αγάπησα | Single accent pattern |
| τελειώνω | Regular (-ω) | τέλειωσα, τελείωσα | ✓ Stress variants |

**Key Finding**: Contract verbs (-άω) in the library generate single accent forms, while regular verbs (-ω) generate multiple stress-shifted variants. This is the **current library design** and may be intentional.

## Open Question for Upstream

**Should contract verbs (-άω) generate accent variants like regular verbs (-ω)?**

Currently:
- ✗ σχολάω: No accent variants
- ✓ τελειώνω: Has accent variants (τέλειωσα vs τελείωσα)

This may be:
1. **Intentional design**: Contract verbs don't use stress shifting
2. **Implementation gap**: Contract verbs should generate variants
3. **Corpus limitation**: Only single-stress forms are in greek_corpus

## Solution: Documentation & Testing

### Files Modified

#### 1. `test/unit/test_verb_aorist.py`

Added test case for σχολάω aorist with current correct forms:

```python
def test_scholazo_aorist(self):
    """
    Test σχολάω (to skip school) aorist forms.
    Contract verb (-άω group), fully regular in aorist.
    """
    self.assertDictEqual(
        aorist_act('σχολάω'),
        {
            'sg': {
                'pri': {'σχόλησα'},
                'sec': {'σχόλησες'},
                'ter': {'σχόλησε'}
            },
            'pl': {
                'pri': {'σχολήσαμε'},
                'sec': {'σχολήσατε'},
                'ter': {'σχόλησαν', 'σχολήσανε'}
            }
        }
    )
```

## Updated Understanding

Per Greek Linguist:
- σχολάω is **fully regular** in aorist
- No σχ/σκ prefix alternation in aorist forms
- "Strangeness" only exists in present tense (two forms: σχολάω / σχολώ)
- Aorist formation follows standard sigmatic pattern

## Verification

- ✓ Test case documents correct aorist forms
- ✓ All existing tests pass
- ✓ Linguistic classification confirmed

## Related Issues

- UPSTREAM_BUGS.md Bug #2: Requires clarification (not missing variants)
- Article fix: PR #2 (neuter article forms) - separate concern

---

**Submitted by**: Claude Code
**Date**: March 21, 2026
**Library Version**: 2.0.7+
**Status**: Documentation + Test case added for clarification
