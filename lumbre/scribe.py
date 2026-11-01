"""Turn a model's reply into a card. Offerings never come from the model."""

import re
from collections.abc import Callable

from lumbre.altar import AltarCard, AltarInput
from lumbre.prompts import build_prompt

Generate = Callable[[str, str], tuple[str, str]]

_LABELS = ("INSCRIPTION", "REMEMBRANCE")


class ScribeError(Exception):
    """The model reply could not be read as a card."""


def parse_card(raw: str) -> tuple[str, str]:
    labeled = _parse_labels(raw)
    if labeled and all(labeled):
        return labeled
    text = _plain(raw)
    if not text:
        raise ScribeError("The model returned an empty card.")
    first, dot, rest = text.partition(". ")
    if dot and rest:
        return _clip(first + ".", 400), _clip(rest, 1200)
    return _clip(text, 400), _clip(text, 1200)


def compose(altar: AltarInput, generate: Generate) -> AltarCard:
    system, user = build_prompt(altar)
    raw, model = generate(system, user)
    inscription, remembrance = parse_card(raw)
    return AltarCard(
        name=altar.name,
        years=altar.years,
        relationship=altar.relationship,
        memory=altar.memory,
        inscription=inscription,
        remembrance=remembrance,
        offerings=tuple(altar.offerings()),
        gaps=tuple(altar.gaps()),
        model=model,
    )


def _parse_labels(raw: str) -> tuple[str, str] | None:
    buckets: dict[str, list[str]] = {label: [] for label in _LABELS}
    current: str | None = None
    for line in raw.splitlines():
        label, remainder = _split_label(line)
        if label:
            current = label
            if remainder:
                buckets[label].append(remainder)
            continue
        if current and line.strip():
            buckets[current].append(line.strip())
    if not any(buckets.values()):
        return None
    return (
        _clip(" ".join(buckets["INSCRIPTION"]), 400),
        _clip(" ".join(buckets["REMEMBRANCE"]), 1200),
    )


def _split_label(line: str) -> tuple[str | None, str]:
    cleaned = line.strip().lstrip("#").strip("* ").strip()
    match = re.match(r"^(INSCRIPTION|REMEMBRANCE)\s*[:\-]\s*(.*)$", cleaned, re.I)
    if not match:
        return None, ""
    return match.group(1).upper(), match.group(2).strip()


def _plain(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        text = line.strip().lstrip("#").strip("* ").strip()
        if text:
            lines.append(text)
    return " ".join(lines).strip()


def _clip(text: str, limit: int) -> str:
    return " ".join(text.split())[:limit].strip()
