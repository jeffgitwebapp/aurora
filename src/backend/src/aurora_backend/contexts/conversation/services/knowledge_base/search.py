"""Normalização pt-BR e índice BM25 em memória (D-03).

A mesma função `tokenize` é usada no índice e na consulta: sem acentos, sem
diferença de caixa, pontuação como separador e sem stopwords.
"""

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable, Sequence

_TOKEN = re.compile(r"[a-z0-9]+")

_STOPWORDS_RAW = """
a à ao aos as às até com como contra da das de dela dele deles do dos e é ela elas ele eles
em entre era essa esse esta está estão este eu foi for há isso isto já la lhe lo mas me
mesmo meu minha muito na nas não nem no nos nós num numa o os ou para pela pelas pelo pelos
por pra pro qual quando que quem se sem ser seu sua são só também te tem tenho ter um uma
umas uns você vocês vai vou tá to ta pode posso sobre ainda depois então assim ai aí
"""


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def normalize(text: str) -> str:
    return strip_accents(text).casefold()


STOPWORDS = frozenset(normalize(word) for word in _STOPWORDS_RAW.split())


def stem(token: str) -> str:
    """Redução leve de plural/flexão para o português."""
    if len(token) <= 3 or token.isdigit():
        return token
    for suffix, replacement in (("coes", "cao"), ("oes", "ao"), ("aes", "ao"), ("ais", "al")):
        if token.endswith(suffix):
            return token[: -len(suffix)] + replacement
    if token.endswith("s"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    return [stem(token) for token in _TOKEN.findall(normalize(text)) if token not in STOPWORDS]


class BM25Index:
    def __init__(self, documents: Sequence[Iterable[str]], k1: float = 1.5, b: float = 0.75):
        self._k1 = k1
        self._b = b
        self._frequencies = [Counter(document) for document in documents]
        self._lengths = [sum(counter.values()) for counter in self._frequencies]
        total = len(self._frequencies)
        self._average_length = (sum(self._lengths) / total) if total else 0.0
        document_frequency: Counter[str] = Counter()
        for counter in self._frequencies:
            document_frequency.update(counter.keys())
        self._idf = {
            term: math.log(1 + (total - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def scores(self, query: Sequence[str]) -> list[float]:
        terms = [term for term in dict.fromkeys(query) if term in self._idf]
        results: list[float] = []
        for counter, length in zip(self._frequencies, self._lengths, strict=True):
            score = 0.0
            norm = self._k1 * (1 - self._b + self._b * length / (self._average_length or 1))
            for term in terms:
                frequency = counter.get(term, 0)
                if frequency:
                    score += self._idf[term] * frequency * (self._k1 + 1) / (frequency + norm)
            results.append(score)
        return results
