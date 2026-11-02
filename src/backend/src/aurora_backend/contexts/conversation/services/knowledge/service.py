"""Serviço de conhecimento com trechos estáticos de fontes oficiais no protótipo."""

from aurora_backend.contexts.conversation.services.fixture_text import (
    normalize_fixture_sentence,
)
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    KnowledgeResult,
    KnowledgeStatus,
    SourceReference,
)

# Citações literais conferidas no Planalto em 02/11/2026. Fixtures de
# demonstração aprovadas pela usuária; revisão jurídica e curadoria pendentes.
_MARIA_DA_PENHA_ART_7_II = KnowledgePassage(
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
    source=SourceReference(
        id="lei-11340-2006-art-7-ii",
        title="Lei nº 11.340, de 7 de agosto de 2006 (Lei Maria da Penha)",
        locator="art. 7º, II",
        publisher="Presidência da República — Planalto",
        url="https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11340.htm",
        version="Redação dada pela Lei nº 13.772, de 2018",
    ),
)

_CODIGO_PENAL_ART_147_B = KnowledgePassage(
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
    source=SourceReference(
        id="codigo-penal-art-147-b",
        title="Decreto-Lei nº 2.848, de 7 de dezembro de 1940 (Código Penal)",
        locator="art. 147-B",
        publisher="Presidência da República — Planalto",
        url="https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
        version="Incluído pela Lei nº 14.188, de 28 de julho de 2021",
    ),
)

_KNOWLEDGE_FIXTURES: dict[str, tuple[KnowledgePassage, ...]] = {
    "O que é violência psicológica?": (_MARIA_DA_PENHA_ART_7_II,),
    "Violência psicológica é crime?": (_CODIGO_PENAL_ART_147_B,),
}

_NORMALIZED_KNOWLEDGE_FIXTURES = {
    normalize_fixture_sentence(question): passages
    for question, passages in _KNOWLEDGE_FIXTURES.items()
}


class KnowledgeService:
    """Recupera trechos das fixtures estáticas atuais; não é busca RAG real."""

    async def retrieve(self, message: str) -> KnowledgeResult:
        passages = _NORMALIZED_KNOWLEDGE_FIXTURES.get(normalize_fixture_sentence(message))
        if passages is None:
            return KnowledgeResult(status=KnowledgeStatus.NO_SOURCE)
        return KnowledgeResult(status=KnowledgeStatus.FOUND, passages=passages)
