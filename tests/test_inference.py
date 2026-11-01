import unittest
from unittest.mock import patch

from lumbre.config import Settings
from lumbre.inference import InferenceError, _safe_detail, generate


def _settings() -> Settings:
    return Settings(
        hf_token="secret-token",
        router_model="google/gemma-3-4b-it:cheapest",
        space_model="google/gemma-3-270m-it",
        backend="router",
    )


class InferenceTests(unittest.TestCase):
    def test_error_text_hides_the_token(self) -> None:
        detail = _safe_detail("rejected secret-token now", "secret-token")
        self.assertNotIn("secret-token", detail)
        self.assertIn("[token]", detail)

    def test_missing_credits_do_not_echo_the_token(self) -> None:
        class Response:
            status_code = 402
            text = "no credits for secret-token"

            def json(self) -> dict:
                raise AssertionError("402 responses are not parsed")

        with patch("lumbre.inference.requests.post", return_value=Response()):
            with self.assertRaises(InferenceError) as caught:
                generate("system", "note", _settings())
        message = str(caught.exception)
        self.assertNotIn("secret-token", message)
        self.assertIn("credits", message)

    def test_other_errors_are_redacted(self) -> None:
        class Response:
            status_code = 401
            text = "bad secret-token"

        with patch("lumbre.inference.requests.post", return_value=Response()):
            with self.assertRaises(InferenceError) as caught:
                generate("system", "note", _settings())
        message = str(caught.exception)
        self.assertNotIn("secret-token", message)
        self.assertIn("[token]", message)


if __name__ == "__main__":
    unittest.main()
