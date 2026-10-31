# Skill: Curadoria de conteúdo e engenharia de conhecimento RAG

## Finalidade

Criar e manter uma base de conhecimento rastreável que sustente respostas
informativas do Aurora.

## Conhecimentos necessários

- Curadoria de fontes primárias/secundárias; ingestão de PDF/HTML, OCR,
  parsing, limpeza, chunking, metadados e versionamento.
- Embeddings, busca vetorial/híbrida, reranking, limiar de similaridade e
  avaliação de recuperação.
- Proveniência: autoria/órgão, ano, URL, versão, validade e revisão humana.
- Reindexação incremental, publicação de índice sem interrupção e remoção de
  fontes obsoletas.

## Contexto específico do Aurora

- Cobrir literatura científica e fontes jurídicas/oficiais, como leis,
  cartilhas institucionais e materiais revisados.
- Respostas devem citar fontes e trechos que sustentem as afirmações.
- Sem fonte relevante acima do limiar, declarar limitação em vez de inventar
  conteúdo.
- Frescor da base RAG é distinto do frescor do catálogo de serviços.

## Limites e validação

Especialistas humanos devem validar fontes e interpretações clínicas e
jurídicas; engenharia não certifica precisão de domínio.
