# Skill: Integração de LLM e engenharia de prompts

## Finalidade

Integrar modelos de linguagem como geradores informativos substituíveis,
controlando latência, custo, privacidade e indisponibilidade.

## Conhecimentos necessários

- APIs de modelos, streaming, contexto, timeouts, retries, cancelamento e
  custos.
- Prompts versionados, contratos estruturados e separação entre instruções e
  conteúdo recuperado.
- Adaptadores de provedor, limites de contexto e fallback.
- Prompt injection em entradas e documentos RAG; não usar prompt como único
  controle de segurança.
- Avaliação de retenção, uso para treinamento, região, suboperadores e
  condições do provedor.

## Contexto específico do Aurora

- O LLM redige informação ancorada no RAG; não decide risco agudo nem escolhe
  sozinho encaminhamento.
- Desempenho documenta metas de primeiro token e resposta completa.
- Indisponibilidade deve manter canais de emergência e conteúdo estático seguro.
- Não enviar PII desnecessária ao provedor.

## Resultado esperado

Integração isolada, observável sem conteúdo sensível, com limites e fallback
testáveis e versionamento de prompts.
