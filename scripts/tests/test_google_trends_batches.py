from extractors.google_trends import build_trends_batches


def test_batches_have_at_most_five_terms():
    terms = ["Lula", "A", "B", "C", "D", "E", "F", "G", "H"]
    batches = build_trends_batches(terms, "Lula", max_terms_per_request=5)

    assert all(len(batch) <= 5 for batch in batches)


def test_anchor_present_in_every_batch_without_duplication():
    terms = ["Lula", "A", "B", "C", "D", "E", "F"]
    batches = build_trends_batches(terms, "Lula", max_terms_per_request=5)

    assert len(batches) > 1
    for batch in batches:
        assert batch[0] == "Lula"
        assert batch.count("Lula") == 1


def test_batches_preserve_candidate_order():
    terms = ["Lula", "A", "B", "C", "D", "E"]
    batches = build_trends_batches(terms, "Lula", max_terms_per_request=5)

    candidates = [term for batch in batches for term in batch if term != "Lula"]
    assert candidates == ["A", "B", "C", "D", "E"]


def test_anchor_is_prepended_even_when_not_in_terms():
    terms = ["A", "B", "C"]
    batches = build_trends_batches(terms, "Lula", max_terms_per_request=5)

    assert batches == [["Lula", "A", "B", "C"]]


def test_empty_terms_returns_no_batches():
    assert build_trends_batches([], "Lula", max_terms_per_request=5) == []


def test_only_anchor_returns_no_batches():
    assert build_trends_batches(["Lula"], "Lula", max_terms_per_request=5) == []
