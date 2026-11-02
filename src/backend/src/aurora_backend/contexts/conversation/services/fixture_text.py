"""Normalização compartilhada pelas frases-fixture estáticas do protótipo."""

import unicodedata


def normalize_fixture_sentence(sentence: str) -> str:
    """Ignora caixa, acentos, espaços repetidos e pontuação nas bordas."""
    decomposed = unicodedata.normalize("NFKD", sentence)
    without_accents = "".join(
        character for character in decomposed if unicodedata.category(character) != "Mn"
    )
    return " ".join(without_accents.casefold().split()).strip(" \t\r\n.,;:!?")
