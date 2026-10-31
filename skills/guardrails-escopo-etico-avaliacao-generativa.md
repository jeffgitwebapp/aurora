# Skill: Guardrails, escopo ético e avaliação generativa

## Finalidade

Impedir que respostas fora do escopo ou sem fundamentação sejam apresentadas
como informação confiável.

## Conhecimentos necessários

- Controles de entrada/saída, validação de escopo, detecção de conteúdo
  proibido, proteção contra injeção e fluxo fail-closed.
- Avaliação de grounding, validade/cobertura das citações, aderência e
  comportamento sob falhas.
- Benchmarks, casos adversariais, LLM-as-judge calibrado por revisão humana e
  versionamento dos controles.
- Comunicação clara de recusa, limitação e alternativas informativas.

## Contexto específico do Aurora

- Bloquear diagnóstico, psicoterapia, parecer jurídico individualizado e
  decisão coerciva pela usuária.
- Evitar dizer que a usuária “deve” denunciar ou sair de casa.
- CA-03 define ≥90% de cobertura de citações, limite para respostas fora do
  escopo e zero violações atravessando o guardrail.
- Falha ou timeout do guardrail bloqueia a geração.

## Limites e validação

Métricas automáticas não substituem revisão humana, especialmente para
conteúdo ligado a risco, saúde mental e direitos.
