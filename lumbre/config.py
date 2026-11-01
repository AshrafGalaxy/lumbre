"""Runtime settings. Tokens are read from the environment, never from source."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTER_MODEL = "google/gemma-3-4b-it:cheapest"
DEFAULT_SPACE_MODEL = "google/gemma-3-270m-it"
FALLBACK_SPACE_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
SPACE_URL = "https://ashraf01k-lumbre.static.hf.space"

_SECRET_KEYS = ("HF_TOKEN", "HF_MODEL", "LUMBRE_MODEL", "LUMBRE_BACKEND")


@dataclass(frozen=True)
class Settings:
    hf_token: str
    router_model: str
    space_model: str
    backend: str

    @property
    def active_model(self) -> str:
        if self.backend == "weights":
            return self.space_model
        return self.router_model


def load_settings() -> Settings:
    load_dotenv(ROOT / ".env")
    _copy_streamlit_secrets()
    return Settings(
        hf_token=os.getenv("HF_TOKEN", "").strip(),
        router_model=os.getenv("HF_MODEL", DEFAULT_ROUTER_MODEL).strip(),
        space_model=os.getenv("LUMBRE_MODEL", DEFAULT_SPACE_MODEL).strip(),
        backend=_backend(),
    )


def _backend() -> str:
    chosen = os.getenv("LUMBRE_BACKEND", "").strip().lower()
    if chosen in {"weights", "router"}:
        return chosen
    if os.getenv("SPACE_ID"):
        return "weights"
    return "router"


def _copy_streamlit_secrets() -> None:
    try:
        import streamlit as st

        secrets = st.secrets
        items = secrets.to_dict() if hasattr(secrets, "to_dict") else dict(secrets)
    except Exception:
        return
    for key in _SECRET_KEYS:
        if not os.getenv(key) and items.get(key):
            os.environ[key] = str(items[key])
