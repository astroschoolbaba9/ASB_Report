from numerology.core import mystical_triangle_values_image
from numerology.reads import build_reads
from numerology.traits import F_TRAIT, NUMBER_MEANINGS, num_traits

def test_reads_contains_key_set():
    vals = mystical_triangle_values_image("28-01-2005")
    reads = build_reads(vals)
    # core keys
    assert "G" in reads
    assert "EF(CORE)" in reads
    # a few concatenations
    for k in ["AB", "CD", "AE", "DF", "NP", "OP", "PR"]:
        assert k in reads

def test_f_trait_present_for_1_to_9():
    for n in range(1, 10):
        assert n in F_TRAIT
        assert isinstance(F_TRAIT[n], str) and len(F_TRAIT[n]) > 0

def test_number_meanings_and_num_traits_safe():
    for n in range(1, 10):
        assert n in NUMBER_MEANINGS
        t = num_traits(n)
        assert "meaning" in t
        # keys are always present even if empty
        for k in ("title", "positive", "negative", "roles", "story"):
            assert k in t
