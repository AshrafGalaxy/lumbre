"""Facts the visitor brings, kept apart from the model's prose."""

from dataclasses import dataclass

FIELD_LIMITS = {
    "name": 80,
    "relationship": 120,
    "years": 40,
    "memory": 800,
    "food": 80,
    "song": 120,
    "object": 80,
}

OPTIONAL_GAPS = (
    ("relationship", "how you knew them"),
    ("years", "the years"),
    ("food", "a favorite food"),
    ("song", "a song or phrase"),
    ("object", "an object"),
)


def _clean(value: str, limit: int) -> str:
    return " ".join(value.split())[:limit].strip()


def download_name(name: str) -> str:
    stem = "".join(char.lower() if char.isalnum() else "-" for char in name)
    stem = "-".join(part for part in stem.split("-") if part)
    return f"{stem or 'altar'}.json"


@dataclass(frozen=True)
class AltarInput:
    name: str
    relationship: str
    years: str
    memory: str
    food: str
    song: str
    object: str

    @classmethod
    def from_form(cls, **fields: str) -> "AltarInput":
        cleaned = {
            key: _clean(str(fields.get(key, "")), limit)
            for key, limit in FIELD_LIMITS.items()
        }
        altar = cls(**cleaned)
        altar.validate()
        return altar

    def validate(self) -> None:
        if not self.name:
            raise ValueError("Write the name that should stand on the altar.")
        if len(self.memory) < 20:
            raise ValueError("Write a memory of at least one sentence.")

    def gaps(self) -> list[str]:
        return [label for field, label in OPTIONAL_GAPS if not getattr(self, field)]

    def offerings(self) -> list[str]:
        return [item for item in (self.food, self.song, self.object) if item]

    def note(self) -> str:
        return "\n".join(
            [
                f"Name: {self.name}",
                f"Relationship: {self.relationship or 'not given'}",
                f"Years: {self.years or 'not given'}",
                f"Memory: {self.memory}",
                f"Food: {self.food or 'not given'}",
                f"Song or phrase: {self.song or 'not given'}",
                f"Object: {self.object or 'not given'}",
            ]
        )


@dataclass(frozen=True)
class AltarCard:
    name: str
    years: str
    relationship: str
    memory: str
    inscription: str
    remembrance: str
    offerings: tuple[str, ...]
    gaps: tuple[str, ...]
    model: str

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "years": self.years,
            "relationship": self.relationship,
            "memory": self.memory,
            "inscription": self.inscription,
            "remembrance": self.remembrance,
            "offerings": list(self.offerings),
            "gaps": list(self.gaps),
            "model": self.model,
        }
