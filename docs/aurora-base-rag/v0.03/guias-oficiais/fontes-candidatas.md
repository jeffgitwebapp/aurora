---
titulo: Fontes candidatas — cartilhas e guias para a base RAG do Aurora
versao: 0.2
verificado_em: 2026-11-04
status: validada em 04/11/2026 — cada item com situação; os que viraram arquivo próprio estão nesta pasta
---

# Fontes candidatas: cartilhas e guias (v0.2, validada)

**Filtros obrigatórios (mantidos):** licença · atualidade (se a fonte é anterior às Leis 14.994/2024, 15.123/2025 e às de 2026 — 15.380, 15.383, 15.384, 15.411, 15.412 e 15.438 —, o que ela diz sobre penas, prazos e número de formas de violência não entra) · escopo (nada de "faça X no seu caso").

**Legenda:** ✅ validada e transformada em arquivo · 🟢 validada, usar com as ressalvas · 🟡 existe, mas tem ressalva importante · ⛔ desatualizada para o uso proposto · ⚪ não verificada nesta rodada

## Prioridade A: órgão público federal ou nacional

| # | Fonte | Situação (04/11/2026) | O que muda |
|---|---|---|---|
| A1 | Cartilha "Lei Maria da Penha: Direitos das mulheres e meninas e como buscar ajuda" — Ministério das Mulheres + UNFPA | ✅ `mmulheres-unfpa-2026-cartilha-lei-maria-da-penha.md` | PDF lido na íntegra (o arquivo real está em `…/CartilhaLeiMariadaPenhaversodigital.pdf/@@display-file/file`). Reedição de **fev/2026**, publicada no portal em 03/07/2026. Licença do portal: CC BY-ND 3.0. É **anterior** às leis de abr–jun/2026: diz "cinco formas" (hoje são seis) e simplifica quem concede medida sem juiz — ressalvas anotadas nos trechos. |
| A2 | "Entenda a Violência" — Senado/OMV | ⛔ para conceitos jurídicos | A página "A Violência contra a Mulher" diz que a LMP tem **cinco** formas e trata o feminicídio como **qualificadora** do homicídio (desatualizado desde a Lei 14.994/2024 e a Lei 15.384/2026). Usar só como referência histórica; para a definição da Convenção de Belém do Pará, citar o Decreto 1.973/1996. A subpágina "Violência em Números" pode ser útil para dados, conferindo a data. |
| A3 | "Caminhos: violência contra a mulher" — Senado + Grupo Mulheres do Brasil, 2022 | 🟡 | Registro confirmado (www2.senado.leg.br/jspui/handle/id/602834). Foco no DF e anterior a 2024: usar só a lógica da rota de atendimento, nunca endereços, penas ou prazos. |
| A4 | Nota Técnica nº 25 (CFP) | ✅ `cfp-2025-nota-tecnica-25-mulheres-violencias.md` | Confirmado: **Nota Técnica CFP nº 25/2025, de 07/07/2025**. Uso interno (prompt, Guardrails, revisão da psicóloga). |
| A5 | Cartilha da Ouvidoria das Mulheres (CNMP) | ⚪ | Não localizada nesta rodada com título e ano; manter pendente. |
| A6 (nova) | Referências Técnicas CFP/CREPOP — 2ª ed., 2024 | ✅ `cfp-2024-referencias-tecnicas-mulheres-violencia.md` | Uso interno. Substitui a 1ª edição (2012/2013). |

## Prioridade B: Defensorias e Ministérios Públicos estaduais

| # | Fonte | Situação (04/11/2026) | O que muda |
|---|---|---|---|
| B1 | "Cartilha da Mulher – Violência Psicológica" — DPE-PA | 🟡 | Confirmada: edição de **agosto/2021** (arquivo nomeado "julho 2021"), cópia em ovm.alesc.sc.gov.br (2025). Anterior às Leis 15.123/2025, 15.384/2026 e 15.410/2026: só conceitos, sinais e consequências emocionais. Link original da DPE-PA ainda não localizado. |
| B2 | "Cartilha Maria da Penha" — DPE-SP/NUDEM, 2019 | ⛔ | Anterior ao art. 147-B (2021) e a todas as mudanças de 2023–2026. Não usar; procurar edição nova do NUDEM. |
| B3 | Cartilha da ANADEP com os núcleos estaduais | ⚪ | É catálogo, não RAG. Conferir contatos um a um antes de usar. |
| B4 | "Alerta Lilás" — MPMG | ⚪ | Não verificada. |
| B5 | "Todas e Todos pelo Fim da Violência contra a Mulher" — MPRS | ⚪ | Não verificada. |

## Prioridade C: sociedade civil

| # | Fonte | Situação (04/11/2026) | O que muda |
|---|---|---|---|
| C1 | "Violência psicológica contra mulheres: reconhecer para prevenir e enfrentar" — Aliança Pelas Mulheres, 2025 | 🟢 | Link válido (institutoaurora.org/wp-content/uploads/2025/12/Cartilha-APM-Violencia-psicologica-contra-mulheres.pdf). Seções úteis: sinais nas relações afetivas e no trabalho. Licença não informada; conflito de nome com o "Instituto Aurora" continua valendo. Anterior às leis de 2026. |
| C2 | Dossiês do Instituto Patrícia Galvão | 🟢 | Referência para linguagem responsável; não é chunk para a usuária. |
| C3 | "Manual de Fuga" (PenhaS/AzMina) | ⚪ | Mantido fora do escopo (conteúdo operacional de saída). |
| C4 (nova) | "Ciclo da violência" — Instituto Maria da Penha | ✅ `instituto-maria-da-penha-ciclo-da-violencia.md` | Fonte citada pela própria cartilha A1. |

## Não usar como fonte de conteúdo (mantido)

- Blogs, portais jurídicos comerciais, TCCs, artigos de opinião.
- Dossiê Mulher (ISP-RJ): dados estaduais.

## Próximos passos

- [x] Baixar A1 e confirmar a licença.
- [x] Confirmar a Nota Técnica do CFP (A4).
- [ ] Colar os trechos da A1 (licença ND: sem alterar) e levar à psicóloga.
- [ ] Decidir se entram textos com licença ND só como citação com link.
- [ ] Localizar o link original da DPE-PA (B1) e a cartilha do CNMP (A5).
