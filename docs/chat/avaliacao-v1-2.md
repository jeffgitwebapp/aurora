# Avaliação da v1.2 (F3)

**Plano:** [plano-implementacao-adicionando-agente-aurora.md](../plano-implementacao-adicionando-agente-aurora.md), fase F3 e CA-03.
**Script:** `src/backend/evals/v1_2/run_answer_eval.py` (fluxo real do chat com o motor `llm`). Resultados brutos em `src/backend/evals/v1_2/results/` (ignorados pelo git).

## Modos de execução

| Modo | Comando (em `src/backend`) | Casos | Tempo (Gemini gratuito) | Quando usar |
|---|---|---|---|---|
| **Rápido (padrão)** | `uv run --env-file .env python evals/v1_2/run_answer_eval.py --judge` | 1 por categoria (5) | ~1–2 min | Depois de mudar prompt, modelo ou base; antes de ativar o `llm` num ambiente |
| Completo | `... run_answer_eval.py --judge --limit 0` | 182 | ~1 h (10 req/min) | Medição formal do CA-03, sob demanda |

Nenhum dos dois roda na CI nem no deploy, porque dependem de chave e cota do provedor. A CI roda só os testes offline (280 testes, ~30 s, sem rede), que cobrem contrato, guardrail (M4 com respostas violadoras sintéticas) e falha fechada.

## Resultado — modo rápido (07/11/2026)

Base `v0.03`, `gemini/gemini-3.5-flash-lite`, juiz = mesmo modelo.

| Métrica | Resultado | Meta CA-03 |
|---|---|---|
| M1 cobertura de citação | 1/1 (100%) | ≥ 90% |
| Fonte esperada entre as fontes / citada no texto | 1/1 / 1/1 | — |
| M2 validade (segmentos citados sustentados, juiz) | 5/5 (100%) | ≥ 95% |
| M3 respostas com violação (juiz) | 0/2 (0%) | ≤ 5% |
| M4 violações sintéticas que passam o guardrail | 0/25 (testes offline) | 0 |
| M5 fora da base → sem fonte | 1/1 (100%) | 100% |
| Risco/escopo resolvidos sem LLM | 2/2 | 100% |
| Falhas técnicas (503) | 0 | — |
| Latência das respostas com fonte | 4,2 s e 8,3 s | ≤ 5 s (MVP, p95) |

## Leitura

- O modo rápido é um **teste de fumaça**: mostra que o fluxo inteiro funciona, mas 1 caso por categoria **não comprova** as metas do CA-03.
- Medições anteriores, mais amplas: seleção de trechos com recall@5 de 83,3% (78 perguntas) e 28/30 perguntas fora da base resolvidas como sem fonte (F1, registro de execução do plano). Piloto da F3 com 2 casos por categoria: tudo dentro das metas, p50/p95 de 5,6 / 6,8 s.
- **Latência acima da meta** (duas chamadas ao LLM no plano gratuito): ponto a tratar antes de uso real (modelo pago, cache, ou uma única chamada para seleção e redação).
- **Juiz = gerador:** há viés de autoaprovação. O CA-03 exige revisar à mão 20% das avaliações do modo completo para calibrar o juiz.

## Pendências

1. Rodar o modo completo quando houver janela (ou cota paga) e registrar aqui.
2. Revisão humana de 20% das respostas julgadas.
3. Decidir o tratamento da latência antes de ativar o `llm` em produção (D-09).
