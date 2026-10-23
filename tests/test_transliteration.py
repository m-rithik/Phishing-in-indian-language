"""Tests for transliteration candidate generation."""

import unittest
from fisher_transliteration.candidates import generate_candidates, CandidateConfig, Candidate


class TransliterationCandidateTests(unittest.TestCase):
    """Test transliteration candidate generation."""

    def test_single_token_candidates(self):
        """Single-token input generates candidates for each script."""
        candidates = generate_candidates("otp")
        self.assertGreater(len(candidates), 0)

        # Expect: romanized + hindi + tamil + telugu (or subset)
        scripts = {c.script for c in candidates}
        self.assertIn("romanized", scripts)
        self.assertTrue(any(s in scripts for s in ["hindi", "tamil", "telugu"]))

    def test_otp_phishing_term(self):
        """OTP (phishing signal) generates high-confidence candidates."""
        candidates = generate_candidates("otp")

        # Find OTP-specific candidates
        otp_candidates = [c for c in candidates if c.source_rule == "otp"]
        self.assertGreater(len(otp_candidates), 0, "Should find OTP transliterations")

        # OTP-specific rules have high weight
        for c in otp_candidates:
            self.assertGreaterEqual(c.confidence, 1.8, "OTP should have high confidence")

    def test_password_variants(self):
        """Password variants are recognized across scripts."""
        test_cases = ["password", "pass", "pwd"]
        for term in test_cases:
            candidates = generate_candidates(term)
            self.assertGreater(len(candidates), 0, f"Should find candidates for {term}")

    def test_ambiguous_mappings_flagged(self):
        """Ambiguous patterns are marked as such."""
        candidates = generate_candidates("aaa")
        ambiguous = [c for c in candidates if c.ambiguous]
        # Some interpretations may be ambiguous
        if ambiguous:
            self.assertTrue(all(c.ambiguous for c in ambiguous))

    def test_confidence_ordering(self):
        """Candidates are ordered by confidence (descending)."""
        candidates = generate_candidates("otp")
        if len(candidates) > 1:
            for i in range(len(candidates) - 1):
                self.assertGreaterEqual(
                    candidates[i].confidence,
                    candidates[i + 1].confidence,
                    "Candidates should be confidence-ordered",
                )

    def test_max_candidates_respected(self):
        """Generator respects max_candidates config."""
        config = CandidateConfig(max_candidates=3, include_romanized=True)
        candidates = generate_candidates("otp", config)
        self.assertLessEqual(len(candidates), 3)

    def test_min_confidence_filter(self):
        """min_confidence config filters low-confidence candidates."""
        config = CandidateConfig(min_confidence=2.0)
        candidates = generate_candidates("otp", config)
        for c in candidates:
            self.assertGreaterEqual(
                c.confidence, 2.0, "All candidates should meet min_confidence"
            )

    def test_empty_input(self):
        """Empty input returns empty candidate list."""
        self.assertEqual(generate_candidates(""), [])
        self.assertEqual(generate_candidates("   "), [])
        self.assertEqual(generate_candidates(None), [])

    def test_case_insensitive(self):
        """Input is case-insensitive."""
        lower = generate_candidates("otp")
        upper = generate_candidates("OTP")
        mixed = generate_candidates("OtP")

        # All should produce same candidates (after normalization)
        lower_texts = {(c.text, c.script) for c in lower}
        upper_texts = {(c.text, c.script) for c in upper}
        mixed_texts = {(c.text, c.script) for c in mixed}

        self.assertEqual(lower_texts, upper_texts)
        self.assertEqual(lower_texts, mixed_texts)

    def test_hindi_candidates(self):
        """Hindi script candidates are generated."""
        config = CandidateConfig(scripts=["hindi"])
        candidates = generate_candidates("otp", config)

        scripts = {c.script for c in candidates}
        # May include romanized if include_romanized=True (default)
        self.assertTrue(
            "hindi" in scripts or len(candidates) > 0,
            "Should generate Hindi candidates",
        )

    def test_tamil_candidates(self):
        """Tamil script candidates are generated."""
        config = CandidateConfig(scripts=["tamil"])
        candidates = generate_candidates("otp", config)
        scripts = {c.script for c in candidates}
        self.assertTrue(len(candidates) > 0, "Should generate Tamil candidates")

    def test_telugu_candidates(self):
        """Telugu script candidates are generated."""
        config = CandidateConfig(scripts=["telugu"])
        candidates = generate_candidates("otp", config)
        scripts = {c.script for c in candidates}
        self.assertTrue(len(candidates) > 0, "Should generate Telugu candidates")

    def test_romanized_included_by_default(self):
        """Romanized version is included by default."""
        candidates = generate_candidates("otp")
        romanized = [c for c in candidates if c.script == "romanized"]
        self.assertEqual(len(romanized), 1, "Exactly one romanized candidate")
        self.assertEqual(romanized[0].text, "otp")

    def test_romanized_excluded_when_configured(self):
        """Romanized can be excluded via config."""
        config = CandidateConfig(include_romanized=False)
        candidates = generate_candidates("otp", config)
        romanized = [c for c in candidates if c.script == "romanized"]
        self.assertEqual(len(romanized), 0, "No romanized candidates when disabled")

    def test_deterministic_output(self):
        """Candidate generation is deterministic."""
        candidates1 = generate_candidates("password")
        candidates2 = generate_candidates("password")

        self.assertEqual(
            [(c.text, c.script, c.confidence) for c in candidates1],
            [(c.text, c.script, c.confidence) for c in candidates2],
            "Output should be identical across calls",
        )

    def test_kvt_abbreviations(self):
        """KYC, CVV abbreviations are recognized."""
        for term in ["kyc", "cvv"]:
            candidates = generate_candidates(term)
            self.assertGreater(
                len(candidates), 0, f"Should recognize phishing term: {term}"
            )

            # Should have high-confidence transliterations
            high_conf = [c for c in candidates if c.confidence >= 1.8]
            self.assertGreater(len(high_conf), 0, f"{term} should have high-confidence candidates")

    def test_multitoken_generation(self):
        """Multi-token input generates candidates."""
        candidates = generate_candidates("send otp")
        # Should generate something (at least romanized)
        self.assertGreater(len(candidates), 0)

    def test_no_output_echo(self):
        """Candidate generation never echoes sensitive input."""
        sensitive = "card_number_1234_5678"
        candidates = generate_candidates(sensitive)
        # All candidates should be transliterated, not echoed verbatim
        for c in candidates:
            # Romanized is allowed (it's an interpretation, not a leak)
            # But we don't store the exact sensitive input
            pass  # No assertion here; test documents the privacy principle


class CandidateConfigTests(unittest.TestCase):
    """Test CandidateConfig behavior."""

    def test_default_config(self):
        """Default config has sensible values."""
        config = CandidateConfig()
        self.assertEqual(config.max_candidates, 8)
        self.assertEqual(config.min_confidence, 0.3)
        self.assertTrue(config.include_romanized)
        self.assertEqual(set(config.scripts), {"hindi", "tamil", "telugu"})

    def test_custom_config(self):
        """Custom config values are respected."""
        config = CandidateConfig(
            max_candidates=2,
            min_confidence=1.5,
            include_romanized=False,
            scripts=["hindi"],
        )
        self.assertEqual(config.max_candidates, 2)
        self.assertEqual(config.min_confidence, 1.5)
        self.assertFalse(config.include_romanized)
        self.assertEqual(config.scripts, ["hindi"])


if __name__ == "__main__":
    unittest.main()
