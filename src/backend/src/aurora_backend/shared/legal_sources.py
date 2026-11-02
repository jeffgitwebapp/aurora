"""Trechos legais literais aprovados como fixture de demonstração.

Citações conferidas no Planalto em 02/11/2026 e aprovadas pela usuária para o
protótipo; revisão jurídica e curadoria formal continuam pendentes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LegalExcerpt:
    id: str
    text: str
    title: str
    locator: str
    publisher: str
    url: str
    version: str | None = None


MARIA_DA_PENHA_ART_7_II = LegalExcerpt(
    id="lei-11340-2006-art-7-ii",
    text=(
        "a violência psicológica, entendida como qualquer conduta que lhe cause "
        "dano emocional e diminuição da autoestima ou que lhe prejudique e "
        "perturbe o pleno desenvolvimento ou que vise degradar ou controlar suas "
        "ações, comportamentos, crenças e decisões, mediante ameaça, "
        "constrangimento, humilhação, manipulação, isolamento, vigilância "
        "constante, perseguição contumaz, insulto, chantagem, violação de sua "
        "intimidade, ridicularização, exploração e limitação do direito de ir e "
        "vir ou qualquer outro meio que lhe cause prejuízo à saúde psicológica e "
        "à autodeterminação"
    ),
    title="Lei nº 11.340, de 7 de agosto de 2006 (Lei Maria da Penha)",
    locator="art. 7º, II",
    publisher="Presidência da República — Planalto",
    url="https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11340.htm",
    version="Redação dada pela Lei nº 13.772, de 2018",
)

CODIGO_PENAL_ART_147_B = LegalExcerpt(
    id="codigo-penal-art-147-b",
    text=(
        "Causar dano emocional à mulher que a prejudique e perturbe seu pleno "
        "desenvolvimento ou que vise a degradar ou a controlar suas ações, "
        "comportamentos, crenças e decisões, mediante ameaça, constrangimento, "
        "humilhação, manipulação, isolamento, chantagem, ridicularização, "
        "limitação do direito de ir e vir ou qualquer outro meio que cause "
        "prejuízo à sua saúde psicológica e autodeterminação: Pena - reclusão, "
        "de 6 (seis) meses a 2 (dois) anos, e multa, se a conduta não constitui "
        "crime mais grave."
    ),
    title="Decreto-Lei nº 2.848, de 7 de dezembro de 1940 (Código Penal)",
    locator="art. 147-B",
    publisher="Presidência da República — Planalto",
    url="https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
    version="Incluído pela Lei nº 14.188, de 28 de julho de 2021",
)
