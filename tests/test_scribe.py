import unittest

from lumbre.altar import AltarInput
from lumbre.sample import EXAMPLE
from lumbre.scribe import compose, parse_card


class ScribeTests(unittest.TestCase):
    def test_labeled_reply_is_split(self) -> None:
        inscription, remembrance = parse_card(
            "INSCRIPTION: For Rosa, the cup waits.\nREMEMBRANCE: She dried marigolds on Sundays."
        )
        self.assertEqual(inscription, "For Rosa, the cup waits.")
        self.assertIn("marigolds", remembrance)

    def test_unlabeled_reply_still_makes_a_card(self) -> None:
        inscription, remembrance = parse_card(
            "Rosa kept the blue cup. She dried marigolds on the kitchen table."
        )
        self.assertTrue(inscription.startswith("Rosa kept the blue cup."))
        self.assertIn("marigolds", remembrance)

    def test_invented_food_does_not_become_an_offering(self) -> None:
        altar = AltarInput.from_form(**EXAMPLE)

        def fake(system: str, user: str) -> tuple[str, str]:
            self.assertIn("not given", system.lower() + user.lower())
            return (
                "INSCRIPTION: For Rosa.\nREMEMBRANCE: She liked mangoes and the blue cup.",
                "test-model",
            )

        card = compose(altar, fake)
        self.assertEqual(card.offerings, tuple(altar.offerings()))
        self.assertNotIn("mangoes", card.offerings)
        self.assertEqual(card.memory, altar.memory)
        self.assertEqual(card.model, "test-model")

    def test_empty_reply_is_refused(self) -> None:
        with self.assertRaises(Exception):
            parse_card("   ")


if __name__ == "__main__":
    unittest.main()
