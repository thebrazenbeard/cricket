from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PersonaTrait(str, Enum):
    ABSOLUTE_CANDOR = "ABSOLUTE_CANDOR"
    SASS = "SASS"
    IRREVERENCE = "IRREVERENCE"
    SELF_SKEPTICISM = "SELF_SKEPTICISM"
    QUIET_WHEN_CLEAN = "QUIET_WHEN_CLEAN"
    NO_CRUELTY = "NO_CRUELTY"
    NO_PERFORMATIVE_CONTRARIANISM = "NO_PERFORMATIVE_CONTRARIANISM"


@dataclass(frozen=True)
class CricketPersona:
    name: str
    version: str
    traits: tuple[PersonaTrait, ...]
    motto: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("persona name must be non-empty text")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("persona version must be non-empty text")
        if not isinstance(self.traits, tuple) or not self.traits:
            raise ValueError("persona traits must be a non-empty tuple")
        if not all(isinstance(item, PersonaTrait) for item in self.traits):
            raise ValueError("persona traits must be PersonaTrait values")
        if not isinstance(self.motto, str) or not self.motto.strip():
            raise ValueError("persona motto must be non-empty text")
