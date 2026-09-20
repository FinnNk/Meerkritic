"""Challenge fixed lexical semantics rather than deriving expectations from the code."""

import unittest

from semantic_reviewer.domain.grouping import cluster_texts, interpretation_text
from semantic_reviewer.domain.normalisation import IssueInterpretation


class StudyGroupingTest(unittest.TestCase):
    def test_inclusive_threshold_transitivity_and_representative(self):
        rows = cluster_texts(("a", "b", "c"), ("a b c d", "a", "a e f g"))
        self.assertEqual([r["cluster"] for r in rows], [0, 0, 0])
        self.assertEqual([r["representative"] for r in rows], [False, True, False])

    def test_sets_casefold_ascii_empty_and_stable_tie(self):
        rows = cluster_texts(("a", "b", "c", "d"), ("WORD word!", "word", "東京", ""))
        self.assertEqual([r["cluster"] for r in rows], [0, 0, -1, -1])
        self.assertEqual([r["representative"] for r in rows], [True, False, False, False])

    def test_below_threshold_and_no_stop_words(self):
        rows = cluster_texts(("a", "b", "c"), ("a b c d e", "a", "the a"))
        self.assertEqual([r["cluster"] for r in rows], [-1, 0, 0])

    def test_invalid_inputs(self):
        for ids, texts in (
            ((), ()),
            (("a", "a"), ("x", "x")),
            (("a",), ()),
            (("a",), ("x" * 12001,)),
            (("",), ("x",)),
        ):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                cluster_texts(ids, texts)

    def test_shared_text_preserves_empty_line_and_category_order(self):
        # Construct only the fields read here; full source grounding belongs to normalisation.
        value = IssueInterpretation.model_construct(
            issue_statement="Keep the input",
            proposed_invariant=None,
            coarse_categories=("correctness", "security"),
        )
        self.assertEqual(interpretation_text(value), "Keep the input\n\ncorrectness, security")
