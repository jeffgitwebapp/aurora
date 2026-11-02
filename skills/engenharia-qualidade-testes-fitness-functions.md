# Skill: Engenharia de qualidade, testes e fitness functions

## Finalidade

Transformar as metas de qualidade do Aurora em verificações reproduzíveis,
evidências e gates de merge/deploy/publicação.

## Conhecimentos necessários

- Testes unitários, integração, contrato, E2E, acessibilidade, segurança,
  performance e mutation testing.
- pytest, Playwright, k6, Lighthouse CI e avaliação de precisão/recall, p95/p99.
- Dados sintéticos e prevenção de exposição de dados reais em testes.
- CI gates diferenciados conforme severidade e tipo de mudança.

## Contexto específico do Aurora

- Operacionalizar CA-01 a CA-05.
- Plantar PII sintética e verificar armazenamento, logs, telemetria e payloads.
- Triagem usa casos-âncora, controles sem risco e mutações de regras.
- Testar contra aplicação real quando o atributo exige isso, não apenas mocks.
- Gates: zero falsos negativos de risco agudo nos casos-âncora, zero violações
  no guardrail e limites de latência/frescor conforme os documentos.

## Resultado esperado

Suítes rastreáveis a requisitos, relatórios com evidências e bloqueios
automatizados para falhas críticas.
