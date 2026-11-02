"""Modelos de domínio do guia de segurança informativo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GuideSection:
    title: str
    paragraphs: tuple[str, ...]


@dataclass(frozen=True)
class SafetyGuideContent:
    sections: tuple[GuideSection, ...]
    in_preparation: bool
    demo: bool = True
