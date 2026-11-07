---
name: aurora-agente-rag
description: Use when working on the Aurora v1.2 chat engine (Claude API + RAG over docs/aurora-base-rag), its knowledge-base ingestion/snapshot, retrieval (BM25), grounded answer generation with [n] source markers, output guardrail, decision trace, evaluation dataset, or when the user mentions "v1.2", "agente", "RAG", "base de conhecimento", "plano-implementacao-adicionando-agente-aurora" or a phase F0–F5 of that plan.
---

# Aurora v1.2 — motor de chat com agente e RAG

## Antes de qualquer ação

1. Leia `docs/plano-implementacao-adicionando-agente-aurora.md` (fonte da verdade: restrições R-xx, decisões U-xx/D-xx, fases Fx, registro de execução) e `docs/chat/dialogo-processamento.md` (pipeline, prompt, marcação `[n]`, exemplos).
2. Identifique a próxima fase "Não iniciada" (seção 6.2 do plano) e **explique à usuária o que vai fazer, aguardando confirmação** antes de alterar arquivos.
3. Branch de trabalho: `feature/v1.2-agente-rag`. Não faça commit/push sem pedido explícito.

## Regras que não podem ser quebradas (resumo; detalhes na seção 2 do plano)

- **Frontend:** só a exibição de fontes por trecho (U-06: lista Fontes numerada + `[n]` clicável em `src/frontend/src/features/chat/`). Nada mais muda no front; o contrato HTTP `POST /api/chat/messages` mantém os campos.
- **Backend existente:** `TriageService`, `GuardrailService`, `ContentOfferService` e `KnowledgeService` não mudam. Alterações permitidas em código existente estão listadas na seção 5.2 do plano (remover atraso simulado, `[n]` nas fixtures, `ChatResponseUnavailableError` → 503, seleção de motor em `main.py`, testes afetados).
- **Plano da jornada e contratos do protótipo** (`docs/jornada-usuario/`) não são alterados.
- **Triagem e escopo determinísticos antes do LLM.** O LLM nunca decide risco, escopo ou encaminhamento e nunca cria fontes, telefones, prazos ou penas.
- **Sem trecho acima do limiar → `no_source`, sem chamar o LLM.** Falha/recusa/guardrail reprovado → 503 (fail-closed).
- **Logs/trace só com metadados** — nunca mensagem, resposta, trecho citado ou corpo HTTP.
- **Base vigente:** maior pasta `docs/aurora-base-rag/vX.YY` (ordem numérica). Nunca fixe `v0.03`. Nova versão ⇒ regenerar o snapshot (`scripts/build_knowledge_snapshot.py`); a CI deve falhar se o snapshot estiver desatualizado.
- **Busca (D-12):** BM25 gera até 30 candidatos e o `LanguageModelChunkSelector` escolhe até 5 (ou nenhum → `no_source`); falha do seletor → 503. O BM25 usa normalização idêntica no índice e na consulta — sem acentos (NFKD), `casefold`, pontuação como separador, stopwords pt-BR. "violência" = "violencia" = "VIOLÊNCIA".
- Projeto em **modo demonstração**: trechos `pendente` são aceitos com `demo: true`; envio ao provedor liberado. Pontos de atenção futuros: exigir `aprovado` e revisão LGPD antes de uso real.
- **Motor (U-07):** `AURORA_CHAT_ENGINE=fixtures|base|llm` em `contexts/conversation/engine.py`, só por ambiente (sem troca por requisição); valor inválido ou `llm` sem chave impede a subida.
- **LLM (D-13):** só pela porta `services/language_model` (`LanguageModel.generate_json`). Provedor por ambiente: `AURORA_LLM_PROVIDER=gemini` (padrão, `gemini-3.5-flash-lite`, `GEMINI_API_KEY`) ou `claude` (`claude-opus-5-5`, `ANTHROPIC_API_KEY`). Nenhum serviço de domínio importa SDK. Plano gratuito do Gemini → só dados sintéticos. Para código do adaptador Claude, consulte a skill `claude-api`.

## Skills do projeto a consultar

`skills/lista_skills.md` e, por fase, os links indicados no plano (integração LLM, guardrails e avaliação, curadoria RAG, triagem, backend FastAPI, frontend chat, acessibilidade, privacidade, observabilidade, qualidade/testes, DevOps).

## Validação (rodar ao fim de cada fase que mexe em código)

```powershell
Set-Location "C:\Projetos\aurora\src\backend"
uv run python -m pytest
uv run python -m ruff check .
uv run python -m ruff format --check .
uv run python -m compileall src

Set-Location "C:\Projetos\aurora\src\frontend"   # só se a fase tocar o front
npm run check
npm run build
```

Conferir também `git diff --stat develop -- src/frontend` (só arquivos de U-06) e registrar o resultado na seção 12 do plano.

## Avaliação

Dataset em `src/backend/evals/v1_2/dataset.jsonl` (gerado por `src/backend/evals/v1_2/build_dataset.py` a partir da base vigente + casos manuais). Metas CA-03: M1 ≥90%, M2 ≥95%, M3 ≤5%, **M4 = 0**, **M5 = 100%**.

## Concluir uma fase

Só marque "Concluída" com implementação, testes, commit, publicação e teste humano na AWS (R-13). Atualize o quadro 6.2 e o registro de execução (seção 12).
