import unittest

from lumbre.altar import AltarInput, download_name
from lumbre.sample import EXAMPLE


class AltarTests(unittest.TestCase):
    def test_offerings_come_only_from_named_fields(self) -> None:
        altar = AltarInput.from_form(**EXAMPLE)
        self.assertEqual(
            altar.offerings(),
            ["pan dulce", "a lullaby she hummed without a name", "a blue cup"],
        )

    def test_blank_optional_fields_are_gaps(self) -> None:
        altar = AltarInput.from_form(
            name="Rosa",
            memory="She dried marigolds on the kitchen table each Sunday.",
        )
        self.assertIn("a favorite food", altar.gaps())
        self.assertIn("a song or phrase", altar.gaps())
        self.assertEqual(altar.offerings(), [])

    def test_a_short_memory_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            AltarInput.from_form(name="Rosa", memory="Too short")

    def test_download_name_is_a_safe_file_name(self) -> None:
        self.assertEqual(download_name("Rosa Mendoza"), "rosa-mendoza.json")
        self.assertEqual(download_name("   "), "altar.json")


if __name__ == "__main__":
    unittest.main()
