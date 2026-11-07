# Plano de Implementação — Adicionando um Agente à Aurora (v1.2)

**Status:** plano escrito em 07/11/2026, revisão 2 (incorpora os ajustes da usuária de 07/11/2026). **Nenhuma fase iniciada.** A implementação começa após a revisão deste plano e a resolução das decisões abertas bloqueantes (seção 7).
**Branch:** `feature/v1.2-agente-rag` (criada a partir de `develop` em 07/11/2026)
**Documento complementar:** [docs/chat/dialogo-processamento.md](./chat/dialogo-processamento.md) — onde e como cada conceito aplicado entra no processamento de uma mensagem.
**Independência:** este plano é **apartado** de qualquer plano existente. O [plano da jornada do usuário](./jornada-usuario/plano-implementacao-jornada-usuario.md) e os [contratos do protótipo](./jornada-usuario/contratos-integracao-mocks.md) **não são alterados**; servem apenas como referência de arquitetura, convenções e contrato.

---

## 0. Como retomar este trabalho em um novo contexto

Leia nesta ordem:

1. Este arquivo, principalmente as seções 1 (pedido), 2 (restrições), 4 (matriz de aplicabilidade), 6 (fases) e 7 (decisões).
2. [docs/chat/dialogo-processamento.md](./chat/dialogo-processamento.md): pipeline, prompt, marcação de fontes e exemplos.
3. O estado das fases (seção 6.2) e o registro de execução (seção 12).

Prompt sugerido para o Claude Code:

> Leia `docs/plano-implementacao-adicionando-agente-aurora.md` e `docs/chat/dialogo-processamento.md`. Estamos na branch `feature/v1.2-agente-rag`. Continue a partir da próxima fase "Não iniciada" da seção 6.2, respeitando as restrições da seção 2 e as decisões da seção 7. O frontend só pode mudar para exibir as fontes por trecho (U-06); o plano da jornada não pode ser alterado. Antes de implementar, explique o que vai fazer e aguarde minha confirmação.

---

## 1. Pedido original (resumo fiel, 07/11/2026)

- O Aurora vai usar conceitos do plano de estudos da dissertação da usuária ([plano-estudo-8-semanas.md](#9-referências)). **Interessa apenas o conhecimento de como consultar documentos e responder em um chat com agente** (LLM, prompting, tool use, busca em documentos, loop de agente, memória, orquestração, observabilidade). **O livro base da dissertação (H-ACD) e os demais materiais de leitura da pesquisa não fazem parte desta iteração.**
- Objetivo: **analisar a aplicabilidade** desses conceitos para um chat mais inteligente, capaz de responder à vítima **dentro das regras e da base de conhecimento**, sem aplicar tudo de forma indiscriminada.
- O agente usa a **API do Claude**.
- Considerar as **skills do projeto**, a **arquitetura** e os **contratos** definidos no plano existente.
- **O frontend não é alterado**, com uma única exceção autorizada depois (U-06): exibir a fonte de cada trecho da resposta. O **backend é alterado** para continuar respondendo ao mesmo front, agora **sem textos fixos** na resposta informativa.
- As features existentes não mudam de comportamento para a usuária. A integração nova é a **v1.2**: um módulo novo no backend, com contratos internos próprios, ligado ao chat atual pelas portas que já existem.
- Base de conhecimento: `docs/aurora-base-rag/<versão>/`, hoje [v0.03](./aurora-base-rag/v0.03/). **Usar sempre a versão mais recente**: se surgir `v0.04`, a `v0.03` passa a ser ignorada e a base nova precisa ser relida.
- Requisitos em [docs/](./). README com estrutura e CI/CD em [README.md](../README.md).
- Artefatos: este plano e [docs/chat/dialogo-processamento.md](./chat/dialogo-processamento.md).
- Recursos do Claude Code podem ser configurados quando necessário (seção 8).

### 1.1 Decisões da usuária já tomadas (07/11/2026)

| # | Decisão |
|---|---|
| U-01 | **Triagem de risco e limite de escopo continuam determinísticos** (como exigem os requisitos). A v1.2 troca **só a recuperação e a redação** da resposta. |
| U-02 | **Remover o atraso simulado de 5 s** do router do chat. |
| U-03 | **Marcar a fonte de cada trecho da resposta.** A marcação vai **dentro do texto do `reply`** (`[1]`, `[2]`… na ordem da lista `sources`), mantendo o contrato HTTP. O **mesmo comportamento é replicado na versão com fixtures** (`ChatResponseService`). |
| U-04 | Pastas da base no padrão **`vX.YY`** (ex.: `v0.03`, `v0.04`), ordenadas **numericamente**; a maior é a vigente. |
| U-05 | Fora do item U-06, o front não é alterado. Consequência: **sem histórico de conversa no backend** nesta versão (o front envia só a mensagem atual). |
| U-07 | **Roteamento do backend entre mocks e modelo** por `AURORA_CHAT_ENGINE` (`fixtures` / `base` / `llm`), só por variável de ambiente, sem troca por requisição. O `docker compose` local lê `src/backend/.env` (opcional). Na EC2, `/opt/aurora/backend.env` com `env_file` opcional (F5) |
| U-09 | **Correção do layout da conversa** (`styles.css`), pedida pela usuária em 07/11/2026 após teste na AWS: em janelas baixas, a coluna lateral era mais alta que a tela, a grade crescia e o contêiner com `overflow: hidden` era rolado por foco ou âncora, o que tirava o cabeçalho e a caixa de texto da tela. Correção: linha da grade limitada à altura (`minmax(0, 1fr)`), coluna lateral com rolagem própria (no celular, até 30% da altura) e `overflow: clip` no contêiner. Defeito anterior à v1.2, exposto pelas respostas longas |
| U-08 | **Ajuste dos avisos de demonstração do chat** (`MessageList.tsx`), autorizado em 07/11/2026: os textos de "found" e "no_source" deixam de falar em "trecho escolhido para teste" e "só responde a perguntas de teste", porque os motores `base`/`llm` respondem a perguntas livres. Os textos valem para qualquer motor (o front não sabe qual está ativo) |
| U-06 | **O front pode ser ajustado somente para U-03:** numerar a lista **Fontes** (`[1]`, `[2]`…) e renderizar os marcadores `[n]` do texto como referência clicável/acessível para a fonte correspondente. Sem mudança de contrato, de fluxo, de telas ou de outras features. Vale para os dois motores. |

---

## 2. Restrições inegociáveis

| # | Restrição | Origem |
|---|---|---|
| R-01 | **Em `src/frontend/`, só a exibição das fontes por trecho (U-06), os avisos de demonstração (U-08) e a correção do layout da conversa (U-09)**: arquivos de apresentação da mensagem em `features/chat/` (ex.: `components/MessageList.tsx` e, se necessário, um componente novo de marcador e `styles.css`). `api/chatApi.ts`, outras features, `shared/` e `app/` não mudam. O contrato HTTP `POST /api/chat/messages` mantém campos, tipos e combinações válidas. | Pedido; U-05; U-06 |
| R-02 | Alterações em código existente do backend limitadas a: (a) remoção do atraso simulado no `send_message/router.py` (U-02); (b) marcação `[n]` no `ChatResponseService` (U-03); (c) mapeamento de uma nova falha de geração para `503` (seção 5.4); (d) composição em `main.py` (seleção do motor); (e) atualização dos testes afetados por (a)–(c); (f) dependências. `TriageService`, `GuardrailService`, `ContentOfferService` e `KnowledgeService` **não mudam**. | Pedido; U-01..U-03 |
| R-03 | O plano da jornada e os contratos do protótipo não são alterados. | Pedido |
| R-04 | **Triagem antes de conteúdo**, determinística, com precedência. Risco agudo ou indeterminado nunca chega ao LLM. O LLM **não decide risco, escopo nem encaminhamento e não cria fontes**. | RF03, RNF03, U-01, [skill triagem](../skills/triagem-risco-agudo-avaliacao-seguranca.md), [skill LLM](../skills/integracao-llm-engenharia-prompts.md) |
| R-05 | Resposta informativa só a partir de trechos da base, **com fonte citada**. Sem trecho acima do limiar → `no_source` (sem chamar o LLM). | RF02, RNF04, CA-03 M1/M5 |
| R-06 | **Guardrail de saída** entre a geração e a resposta HTTP, *fail-closed*. | RNF06, CA-03 M4 |
| R-07 | Sem PII nem conteúdo em logs, traces ou telemetria; nenhuma persistência do relato; nenhum `session_id`. | RNF01, CA-01, [contratos §2](./jornada-usuario/contratos-integracao-mocks.md) |
| R-08 | Escopo ético: não diagnosticar, não prescrever, não dar parecer individual, nunca "você deve denunciar/sair de casa". O Aurora **indica**, não "encaminha" nem "aciona". | Requisitos §1, RNF06, [README da legislação](./aurora-base-rag/v0.03/legislacao/README.md) |
| R-09 | O que se cita é o **texto oficial**; o "Resumo em linguagem simples" é apoio de redação, não citação. Telefones de emergência e catálogo de serviços **não** vêm da base RAG (CA-05). | [README da legislação](./aurora-base-rag/v0.03/legislacao/README.md) |
| R-10 | A regra da base exige `status: aprovado` para uso real. Hoje **todos** estão `pendente` e o projeto inteiro está em demonstração → `pendente` é aceito com `demo: true` (D-02, resolvida). Voltar a exigir `aprovado` antes de uso real. | idem; D-02 |
| R-11 | **Sempre a versão mais recente da base** (U-04). Nenhum código pode fixar `v0.03`. | Pedido |
| R-12 | Serviços com nomes de produção, sem `Mock*`; domínio não importa FastAPI nem SDK; portas assíncronas; testes injetam falhas pelas portas. | [contratos §2](./jornada-usuario/contratos-integracao-mocks.md) |
| R-13 | Fase concluída = implementação + testes + commit + publicação + **teste humano na AWS**. O assistente não declara conclusão sem essa evidência. | [plano jornada §3](./jornada-usuario/plano-implementacao-jornada-usuario.md) |
| R-14 | Skills técnicas não substituem a revisão de psicóloga, advogada, privacidade e segurança antes de uso real. | [lista de skills](../skills/lista_skills.md) |

---

## 3. Estado atual relevante (levantado em 07/11/2026)

### 3.1 Backend (`src/backend`, FastAPI + uv, Python 3.12)

- Slice `contexts/conversation/features/send_message/`. O [handler](../src/backend/src/aurora_backend/contexts/conversation/features/send_message/handler.py) orquestra: triagem → guardrail de escopo → oferta → `KnowledgeRetriever.retrieve(message)` → (se `found`) `ChatResponseGenerator.generate_reply(message, passages)`.
- As portas já são assíncronas e substituíveis ([services/](../src/backend/src/aurora_backend/contexts/conversation/services/)). Hoje todas as implementações usam **frases-fixture exatas**: o conhecimento só responde a "O que é violência psicológica?" e "Violência psicológica é crime?".
- `ChatResponseService` monta texto fixo: a introdução "Este é o texto da lei sobre isso…" + citações literais.
- O [router](../src/backend/src/aurora_backend/contexts/conversation/features/send_message/router.py) aplica `SIMULATED_PROCESSING_DELAY_SECONDS = 5` quando há conhecimento e mapeia `GuardrailUnavailableError`/`KnowledgeUnavailableError` → `503`.
- `main.py::create_app(...)` aceita a injeção de cada serviço → a v1.2 entra pela composição.
- `pyproject.toml` não tem SDK `anthropic`.

### 3.2 Frontend (só a exibição das fontes muda — U-06)

- [chatApi.ts](../src/frontend/src/features/chat/api/chatApi.ts) valida em runtime: `found` ⇒ `reply` string + `sources` não vazio, cada fonte com `id`, `title`, `locator`, `publisher` não vazios, `url` começando com `https://` e `version` string|null; `no_source` ⇒ `reply: null` e `sources: []`. Campos extras são ignorados.
- O texto da mensagem é renderizado com `white-space: pre-wrap` → os marcadores `[n]` e as quebras de parágrafo aparecem corretamente.
- O bloco **Fontes** lista as fontes na ordem recebida; com `demo: true`, exibe o aviso de demonstração.
- Qualquer resposta HTTP sem sucesso vira mensagem de erro técnico segura.

### 3.3 Base de conhecimento (`docs/aurora-base-rag/v0.03`)

- 31 arquivos Markdown, ~29 mil palavras (ordem de 50–60 mil tokens), **81 chunks reais** marcados com `<!-- chunk: id#localizador -->`. Um 82º marcador, `id#localizador`, é só o exemplo do README e deve ser ignorado. São **57 blocos de "Perguntas de teste"**.
- Cada arquivo tem cabeçalho YAML (`id`, `titulo`, `tipo`, `orgao`, `versao`, `url_oficial`, `temas`, `status`…). Cada chunk tem Localizador, Redação, Temas, Texto oficial, Resumo em linguagem simples (rascunho), Perguntas de teste e Atenção (escopo).
- Pastas:
  - `legislacao/`: 17 normas + README com as regras da base;
  - `guias-oficiais/`: cartilha MMulheres/UNFPA, notas CFP de "uso interno", Instituto Maria da Penha, fontes candidatas;
  - `literatura/`: 4 artigos, só resumo + DOI ("citar, não reproduzir");
  - `dados/`: 4 pesquisas com ressalvas;
  - `catalogo/`: catálogo de serviços, **não é RAG**.
- **Todos os itens estão `pendente`.**
- ⚠️ `docs/aurora-base-rag/` **não está versionada no git** e fica **fora do contexto Docker** do backend (`./src/backend`). Tratado em F0/F1.

### 3.4 Requisitos e métricas aplicáveis

| Fonte | O que importa |
|---|---|
| [RF02](./requisitos-aurora.md) | top-k + limiar + resposta ancorada + fontes exibidas |
| [RF03 / RNF03](./requisitos-aurora.md) | triagem determinística com precedência |
| [RF10 / RNF06](./requisitos-aurora.md) | guardrails *fail-closed*; prompts versionados e auditáveis |
| [RNF04](./requisitos-aurora.md) | ≥90% com fonte; ≤5% fora do escopo; metadados completos de fonte |
| [RNF05](./requisitos-aurora.md) | provedor de LLM isolado por porta/adaptador |
| [RNF07 / CA-04](./arquitetura_operacionalizada_aurora.md) | resposta completa ≤3 s alvo / ≤5 s MVP (p95), p99 8 s |
| [CA-03](./arquitetura_operacionalizada_aurora.md) | M1 ≥90% · M2 ≥95% · M3 ≤5% · **M4 = 0** · **M5 = 100%** (M4 e M5 bloqueiam deploy) |
| [Backlog E3/E13](./backlog-aurora.md) | chatbot LLM+RAG; base citável com guardrails |
| Restrição R1 (orçamento) | R$ 5.865 no total → custo por pergunta importa (D-01) |

---

## 4. Análise de aplicabilidade do plano de estudos

**Recorte:** apenas o conteúdo técnico sobre **consultar documentos e responder com um agente**. Ficam **fora** da análise: leitura e fichamento do livro H-ACD, o paper ADEPTS, a releitura teórica da semana 5, a metodologia de pesquisa (DSR) e a SLR (semanas 7–8). São material da dissertação, não da Aurora.

**Critério:** um conceito entra se **(a)** melhora a resposta à vítima ou a verificabilidade, **(b)** não viola a seção 2 e **(c)** o custo (latência, dependência, complexidade) se justifica para 81 chunks, um front fixo e um orçamento acadêmico.

Legenda: ✅ aplica · 🟡 aplica parcialmente ou reinterpretado · ⏸️ condicional (só com evidência) · ❌ não aplica.

### 4.1 Semana 1 — API do LLM e prompting

| Conceito | Decisão | Como / por quê |
|---|---|---|
| Chamada à API (SDK Python `anthropic`) | ✅ | É o núcleo do novo gerador, isolado atrás da porta `ChatResponseGenerator` (RNF05). |
| *System prompt* com papel e escopo | ✅ | Define o papel, os limites éticos, a linguagem simples e a regra de citação. Fica versionado em arquivo, com hash registrado no trace. Não é o único controle: há regras determinísticas antes e depois. |
| *Few-shot* | 🟡 | Até 2 exemplos de **forma** (tom, linguagem simples, limite), aprovados pela psicóloga. Nenhum exemplo traz fato jurídico próprio. |
| Saída estruturada (JSON) | 🟡 | Só em chamadas internas (juiz da avaliação; classificador opcional do guardrail, D-10). Na resposta, as **citações nativas** da API são incompatíveis com `output_config.format` e valem mais para RNF04. |
| Tokens, contexto, custo | ✅ | `max_tokens` curto, *prompt caching* do system prompt, medição de `usage` e estimativa de custo por pergunta. |
| Chain-of-Thought explícito | ❌ técnica · 🟡 capacidade | O modelo já usa *adaptive thinking* interno; pedir CoT no prompt é obsoleto. O raciocínio **nunca** é exibido. |
| Conversa multi-turno | ❌ nesta versão | O front envia só a mensagem atual e não pode mudar (U-05). Cada turno é independente. |

### 4.2 Semana 2 — Tool use e consulta a documento

| Conceito | Decisão | Como / por quê |
|---|---|---|
| "Carregar trechos do documento como contexto e extrair conceitos" | ✅ | É o coração da v1.2: os trechos recuperados vão como blocos `search_result` com citações habilitadas. |
| Tool de busca no documento | ⏸️ | Só na fase condicional F4: `buscar_base_conhecimento(consulta)`, somente leitura. Na fase base, quem busca é o código. |
| Assistente que escolhe entre várias tools | ❌ | Não há o que escolher com segurança: encaminhamento e contatos são determinísticos e acionados pela usuária. O Aurora **indica, não aciona**. |
| Loop completo de tool use e tratamento de erros | 🟡 | O tratamento de erros vale desde a F2: cada falha vira um estado explícito, nunca uma resposta de sucesso. O loop só entra na F4. |
| *Designing effective tools* | ✅ (F4) | Uma tool, descrição precisa, `strict: true`, limite de chamadas. |

### 4.3 Semana 3 — Agente e loop ReAct

| Conceito | Decisão | Como / por quê |
|---|---|---|
| Definição de agente (percepção, ação, ambiente) | ✅ documental | Percepção = mensagem + trechos; ações = redigir e citar, ou declarar limite (e buscar, na F4); ambiente = base curada + regras. |
| ReAct livre | ❌ | A sequência de segurança precisa ser fixa e testável (R-04..R-06). Um *workflow* atende RF02 com menos latência e risco. |
| ReAct **limitado** (até 2–3 buscas, só leitura) | ⏸️ F4 | Motivo: a vítima escreve de forma coloquial ("ele controla tudo") e a base usa termos técnicos ("controle coercitivo", "art. 7º, II"). Reformular a busca pode aumentar o recall. **Só adotar se a avaliação (F3) mostrar ganho** sem perder latência nem segurança. |
| Memória em arquivo JSON | ❌ | Persistir relato viola RNF01. |

### 4.4 Semana 4 — LangGraph, estado, memória, human-in-the-loop, LangSmith

| Conceito | Decisão | Como / por quê |
|---|---|---|
| LangGraph / LangChain | ❌ | O fluxo é um pipeline fixo, já orquestrado pelo handler e pelas portas. O framework traria dependência pesada e opacidade sem ganho. |
| **Grafo de estados explícito** (conceito) | ✅ sem framework | O fluxo é documentado como máquina de estados com desfechos explícitos (`dialogo-processamento.md` §2). |
| Memória in-thread / cross-thread | ❌ | Front fixo (U-05) e RNF01. |
| Human-in-the-loop | 🟡 reinterpretado | Não há operador em tempo real. O humano participa **antes** (especialistas aprovam conteúdo, prompt e exemplos: `status: aprovado`), **depois** (revisão humana de 20% da avaliação) e **na tela**: a usuária recebe informação e opções, nunca ordens. |
| LangSmith | ❌ | Enviaria a conversa a terceiros (RNF01). É substituído por trace local **só com metadados**. |
| "Agente que lê o documento: resposta com fonte e raciocínio explícito" | 🟡 | Fonte explícita: sim, com os marcadores `[n]` + bloco Fontes (U-03). Raciocínio explícito: não. |

### 4.5 Semana 5 — Multi-agente (parte técnica)

| Conceito | Decisão | Como / por quê |
|---|---|---|
| Pipeline pesquisador + escritor, supervisor, swarm | ❌ | Soma latência (≤5 s MVP) e dilui a responsabilidade por cada saída. Um gerador único + verificador determinístico basta. |
| Verificação separada da geração | 🟡 | O **guardrail de saída** é um verificador por regras (seção 5.5). Um classificador LLM é opcional (D-10). |
| Converter checklist em testes / pytest | ✅ | Testes de contrato para cada desfecho e cada regra do guardrail, além de um checklist de PR (`dialogo-processamento.md` §6). |

### 4.6 Semana 6 — Observabilidade e trilha de auditoria (parte técnica)

| Conceito | Decisão | Como / por quê |
|---|---|---|
| Logging estruturado (timestamp, step, input, output, duração) | ✅ com restrição | Registra etapa, duração, desfecho, ids de chunks, versões, modelo e tokens. **Nunca input/output textual** (R-07). |
| Audit trail imutável | 🟡 | Sem "quem pediu" (anonimato). Registra a decisão do sistema + as versões de prompt, base e guardrail. |
| `explicar_ultima_decisao()` | 🟡 | Para a usuária, a explicação são as fontes marcadas por trecho. Internamente, o trace. |
| Escalonamento por baixa confiança | ✅ reinterpretado | Abaixo do limiar de recuperação → `no_source`; falha ou dúvida no guardrail → bloqueio (`503`). Nunca pausa à espera de um humano. |

### 4.7 Fora do escopo desta iteração

Livro H-ACD e seus conceitos teóricos, paper ADEPTS, fichamentos, DSR, SLR, outline da dissertação, cursos e vídeos de fundamentos (Karpathy, Illustrated Transformer). Servem para formar quem implementa, mas não viram componente.

### 4.8 Síntese da arquitetura

> A v1.2 é um **workflow com uma chamada ao Claude**: o código faz a triagem e o escopo (já existentes), recupera os trechos da versão vigente da base e só então pede ao modelo uma resposta **ancorada e citada**, que passa por um **guardrail de saída fail-closed** antes de chegar ao front. A autonomia do modelo fica restrita à **redação** (e à reformulação da busca, se a F4 provar valor).

---

## 5. Arquitetura proposta da v1.2

### 5.1 Encaixe no fluxo existente (o handler não muda)

```text
Front (só exibição de fontes muda, U-06) ── POST /api/chat/messages ──▶ send_message (router + handler existentes)
  1. TriageEvaluator   → TriageService (existente, determinístico)
  2. ScopeGuardrail    → GuardrailService (existente, determinístico)
  3. ContentOffer      → ContentOfferService (existente)
  4. KnowledgeRetriever       → [v1.2] KnowledgeBaseService   (BM25 na versão vigente da base)
  5. ChatResponseGenerator    → [v1.2] GroundedAnswerService  (Claude + citações + marcadores [n]
                                                               + AnswerGuardrail + DecisionTrace)
Seleção do motor em main.py (contexts/conversation/engine.py):
  AURORA_CHAT_ENGINE = "fixtures" (padrão) | "base" (BM25, sem LLM) | "llm" (BM25 + seleção pelo LLM)
```

- Com `fixtures`, tudo funciona como hoje, mais os marcadores `[n]` (U-03) e sem o atraso (U-02).
- Com `base` ou `llm`, as etapas 4 e 5 usam o novo motor; o contrato HTTP é o mesmo. Até a F2, a resposta nos dois modos é montada por `SourceReplyService` (abertura neutra + citações com `[n]`); na F2 a redação passa ao LLM.
- `llm` sem credencial válida, ou valor desconhecido → o app **não sobe** e diz o motivo (*fail-fast*); nunca cai silenciosamente para outro motor.
- Sem troca por requisição (decisão da usuária, U-07): o motor é só por variável de ambiente.

### 5.2 Estrutura de código nova

```text
src/backend/src/aurora_backend/contexts/conversation/services/
├── knowledge_base/                 # NOVO
│   ├── models.py                   # KnowledgeChunk, ReviewStatus, KnowledgeBaseSnapshot
│   ├── versioning.py               # localizar a versão vigente vX.YY (seção 5.3)
│   ├── ingestion.py                # parser Markdown → chunks (usado pelo script e pelos testes)
│   ├── repository.py               # KnowledgeBaseRepository: chunks por id, resumo, "Atenção"
│   ├── search.py                   # normalização pt-BR (D-03) + índice BM25
│   ├── selector.py                 # ChunkSelector / LanguageModelChunkSelector (D-12)
│   ├── service.py                  # KnowledgeBaseService implementa KnowledgeRetriever (BM25 → seleção)
│   └── data/knowledge_base.json    # snapshot gerado (versão, hash, chunks)
├── grounded_answer/                # NOVO
│   ├── models.py                   # GroundedAnswer, AnswerSegment
│   ├── service.py                  # GroundedAnswerService implementa ChatResponseGenerator (SDK anthropic)
│   └── prompts/system_v1_2.md      # system prompt versionado
├── answer_guardrail/               # NOVO
│   ├── port.py / models.py
│   └── service.py                  # AnswerGuardrailService (regras determinísticas, §5.5)
└── decision_trace/                 # NOVO
    └── service.py                  # DecisionTraceService (log JSON só com metadados, §5.7)

src/backend/src/aurora_backend/contexts/conversation/services/language_model/   # NOVO (D-13)
├── port.py      # LanguageModel.generate_json, LanguageModelUnavailableError
├── gemini.py    # GeminiLanguageModel (google-genai)
├── claude.py    # ClaudeLanguageModel (anthropic)
└── factory.py   # AURORA_LLM_PROVIDER / AURORA_LLM_MODEL -> adaptador

src/backend/scripts/build_knowledge_snapshot.py   # NOVO — gera o snapshot a partir da versão vigente
src/backend/evals/v1_2/                           # NOVO — dataset + runner da avaliação (F3)
src/backend/tests/test_knowledge_base*.py, test_grounded_answer*.py, test_answer_guardrail*.py  # NOVOS
```

**Alterações em código existente (R-02):**

| Arquivo | Alteração | Motivo |
|---|---|---|
| `features/send_message/router.py` | Remover `SIMULATED_PROCESSING_DELAY_SECONDS` e o `asyncio.sleep`; mapear `ChatResponseUnavailableError` → `503` | U-02; §5.4 |
| `services/chat_response/port.py` | Adicionar `ChatResponseUnavailableError` (como já existe `KnowledgeUnavailableError`) | §5.4 |
| `services/chat_response/service.py` | Acrescentar `[n]` a cada citação, na ordem de `KnowledgeResult.sources` | U-03 |
| `main.py` | Selecionar o motor por `AURORA_CHAT_ENGINE` via `contexts/conversation/engine.py` (serviços injetados nos testes têm precedência) | §5.1, U-07 |
| `docker-compose.yml` (local) | `env_file: ./src/backend/.env` com `required: false` | U-07 |
| `tests/test_send_message.py` | Ajustar asserções de atraso e de texto da fixture | consequência de U-02/U-03 |
| `frontend/src/features/chat/components/MessageList.tsx` (+ componente de marcador e estilos, se necessário) | Numerar a lista **Fontes**; transformar `[n]` do texto em referência acessível (link para âncora da fonte `n`, com `aria-label` "Fonte n: título"); `[n]` sem fonte correspondente é exibido como texto, sem link | U-06 |
| `pyproject.toml` / `uv.lock` | `anthropic` (produção) e `pyyaml` (só dev, para a ingestão). BM25 implementado sem dependência | F1 |

### 5.3 Versão vigente da base (U-04, R-11)

1. **Regra:** dentro de `docs/aurora-base-rag/`, considerar só subpastas que casam com `^v(\d+)\.(\d+)$`. A vigente é a de maior `(major, minor)` numérico (`v0.10` > `v0.04` > `v0.03`). As demais são **ignoradas**.
2. **Releitura:** `scripts/build_knowledge_snapshot.py` aplica a regra, faz a ingestão completa da pasta vigente e grava `data/knowledge_base.json` com `kb_version` (ex.: `v0.03`), `source_hash` (SHA-256 dos arquivos), data e os chunks.
3. **Garantia de que a releitura aconteceu:** um teste (`test_snapshot_matches_latest_base`) recalcula a versão vigente e o hash e **falha** se o snapshot estiver desatualizado. Adicionar `v0.04` sem regenerar o snapshot quebra a CI.
4. **Mudança de formato:** se a ingestão encontrar um chunk sem `id`, sem texto citável ou um YAML inválido, ela **falha com erro claro**. Uma base nova nunca é ingerida pela metade.
5. **Por que snapshot e não leitura direta da pasta:** o contexto Docker do backend é `./src/backend` (a pasta `docs/` não entra na imagem), e o snapshot dá rastreabilidade (RNF06). Em desenvolvimento, o script pode ser rodado a qualquer momento.

### 5.4 Contrato HTTP (sem mudança de campos) e comportamento por desfecho

O contrato continua sendo o da seção 4 dos [contratos do protótipo](./jornada-usuario/contratos-integracao-mocks.md). O que muda é **o conteúdo**:

| Situação | Resposta |
|---|---|
| Risco agudo / indeterminado | Igual a hoje (triagem determinística) |
| Fora do escopo | Igual a hoje (guardrail determinístico) |
| Oferta do guia de segurança | Igual a hoje |
| Nenhum chunk acima do limiar | `knowledge_status: "no_source"`, `reply: null`, `sources: []` — **sem chamar o LLM** |
| Resposta gerada e aprovada | `knowledge_status: "found"`, `reply` com texto gerado + marcadores `[n]`, `sources` (≥1) na ordem dos marcadores, `demo: true` enquanto houver fonte `pendente` |
| Geração recusada pelo modelo, reprovada pelo guardrail de saída, timeout ou indisponibilidade do provedor | **`503`** com `detail` genérico ("O serviço de informações está indisponível no momento."). O front mostra o erro técnico seguro; nenhum texto não validado chega à usuária (*fail-closed*) |

**Marcação de fontes (U-03), regra única para os dois motores:**
- `sources` é numerada a partir de 1, na ordem enviada; `[n]` no `reply` refere-se a `sources[n-1]`.
- Todo `[n]` precisa existir em `sources` (o guardrail verifica os ids citados). **Ajuste da F2:** `sources` vem do handler com **todos** os trechos recuperados (o handler não muda), então pode haver fonte listada sem marcador no texto.
- Mapeamento dos campos de fonte a partir do chunk: `id` = id do chunk (`cp-art147b#caput`); `title` = `titulo` do documento; `locator` = Localizador do chunk; `publisher` = `orgao` (ou autoria/periódico para literatura); `url` = `url_oficial` (deve ser `https://`, exigência do front); `version` = `versao`.
- Fixtures: o texto passa a ser, por exemplo, `Este é o texto da lei… \n\nLei nº 11.340…, art. 7º, II: “…” [1]`.
- Front (U-06): o bloco **Fontes** mostra `[1]`, `[2]`… antes de cada fonte; cada `[n]` no texto vira um link para a âncora da fonte `n`, legível por leitor de tela. Não há mudança no cliente HTTP nem na validação.

### 5.5 Guardrail de saída (determinístico)

Funções puras, cada uma testada com respostas violadoras sintéticas (CA-03 M4):

1. **Grounding:** ≥1 segmento citado e todo `source_id` citado ∈ trechos enviados (implementado em `answer_guardrail@1`).
2. **Proporção sem citação:** frases factuais sem marcador acima de um limite → reprovação. Frases de limite e acolhimento são permitidas.
3. **Padrões proibidos:** diagnóstico ("você tem/sofre de…"), prescrição, imperativos coercivos ("você deve denunciar/sair/se separar"), parecer individual ("no seu caso é crime"), "encaminhei" ou "acionei".
4. **Contatos e links:** telefones só da lista permitida (180/190/192/188); URLs só as das fontes enviadas.
5. **Fail-closed:** exceção ou timeout no guardrail → `ChatResponseUnavailableError` → `503`.
6. **(Opcional, D-10)** Classificador LLM com saída estruturada, depois das regras determinísticas.

### 5.6 Integração com o LLM: porta independente de provedor (D-13)

> **Revisão 07/11/2026:** sem créditos na Anthropic, a demonstração usa o **plano gratuito do Gemini**. O código fica preparado para trocar para o Claude **só por variável de ambiente**.

**Desenho:** porta `LanguageModel` em `services/language_model/port.py` com uma única capacidade, `generate_json(system, prompt, schema, max_output_tokens)`, que devolve um objeto JSON validado contra o schema.
- **Adaptadores:** `GeminiLanguageModel` (`google-genai`) e `ClaudeLanguageModel` (`anthropic`). São os únicos que importam SDK.
- **Fábrica:** `create_language_model` escolhe o adaptador pelo ambiente e importa só o SDK escolhido.
- **Erros:** timeout, cota (429), bloqueio de segurança/recusa e resposta fora do schema viram `LanguageModelUnavailableError` → `503` (falha fechada).
- **Consumidores:** o seletor de trechos (`LanguageModelChunkSelector`, D-12) e, na F2, a redação da resposta (`GroundedAnswerService`) dependem **só da porta**.
- **Citações:** a resposta vem como JSON `{"segments": [{"text", "source_ids"}]}` e o backend monta os `[n]`. As citações nativas do Claude (`search_result`) **não** são usadas, porque não existem no Gemini; a verificação de fonte fica no guardrail de saída (ids ⊆ trechos enviados).

| Variável | Gemini (padrão da demonstração) | Claude (troca direta) |
|---|---|---|
| `AURORA_LLM_PROVIDER` | `gemini` | `claude` |
| `AURORA_LLM_MODEL` | `gemini-3.5-flash-lite` (padrão desde 07/11/2026: ~1 s e cota gratuita suficiente; `gemini-3.6-flash` estourou a cota) | `claude-opus-5-5` (padrão) |
| Credencial | `GEMINI_API_KEY` (aistudio.google.com/apikey, sem cartão) | `ANTHROPIC_API_KEY` |
| Raciocínio | `thinking_level: LOW` | `effort: low` (thinking adaptativo) |
| Recusa/segurança | `finish_reason ≠ STOP` ou `prompt_feedback.block_reason` → `503` | `stop_reason ≠ end_turn` → `503`; `fallbacks: "default"` (beta) |
| Timeout / retries | 8 s, 2 tentativas (`HttpRetryOptions`) | 8 s, `max_retries` = 1 |
| `AURORA_LLM_TIMEOUT_SECONDS` | opcional (padrão 8) | opcional (padrão 8) |

| Item | Decisão |
|---|---|
| Resumo + "Atenção (escopo)" | contexto de apoio **não citável** no prompt (R-09) |
| System prompt | arquivo versionado; hash no trace |
| Streaming | não (o front espera JSON único; o guardrail precisa do texto completo) |
| Segredo | variável de ambiente; nunca no repositório. Local: `src/backend/.env` (gitignored) + `uv run --env-file .env`. EC2: `/opt/aurora/backend.env` (F5) |
| **Privacidade (D-13)** | **No plano gratuito do Gemini, o Google pode usar os dados enviados para melhorar seus produtos.** Até trocar para plano pago ou para o Claude, o sistema só pode receber **dados sintéticos** (nenhuma vítima real) |
| Limites | plano gratuito ~10–15 requisições/min por projeto (conferir no AI Studio); 429 → `503` |

**Custo:** Gemini gratuito = US$ 0 dentro da cota. Claude Opus 5.5 ≈ US$ 0,03 por chamada (US$ 4 / US$ 20 por milhão de tokens); cada pergunta informativa faz 2 chamadas (seleção + redação).

### 5.7 Trace (observabilidade sem conteúdo)

Um evento JSON por turno informativo: `request_id` efêmero, desfecho, duração por etapa, `kb_version`, `prompt_version` (hash), `guardrail_version`, modelo, tokens (entrada, saída, cache), `stop_reason`, ids e scores dos chunks, regras do guardrail reprovadas. **Nunca** mensagem, `reply`, `cited_text` ou corpo HTTP. Um teste planta um marcador na mensagem e verifica que ele não aparece em nenhum log capturado (CA-01).

### 5.8 Recuperação: BM25 em vez de base vetorial (D-03), com seleção pelo Claude (D-12)

> **Atualização F1 (07/11/2026):** BM25 sozinho ficou abaixo da meta (recall@5 64%). Pela decisão D-12, o BM25 passa a gerar até 30 candidatos e o Claude escolhe os relevantes. O limiar absoluto só vale no modo sem seletor (`DEFAULT_SCORE_THRESHOLD = 2.0`).

- BM25 em memória sobre texto oficial + título + temas + resumo. Top-k (k ≈ 5) e **limiar** calibrado na F1 para M5.
- **Normalização obrigatória (exigência da usuária em D-03)**, aplicada pela **mesma função** no índice e na consulta:
  1. Unicode NFKD, removendo marcas diacríticas: "violência" ≡ "violencia", "ameaça" ≡ "ameaca";
  2. `casefold()`: "VIOLÊNCIA", "Violencia" e "violência" são o mesmo termo;
  3. pontuação e hífens viram separadores ("art. 147-B" → "art", "147", "b"); espaços repetidos colapsam;
  4. remoção de stopwords pt-BR, também normalizadas (a lista inclui "nao" e "não");
  5. (opcional, decidir na F1 pelo recall) redução simples de plural/flexão ("ameaças" → "ameaca").
  
  Pode reaproveitar a ideia de `shared/fixture_text.normalize_fixture_sentence` (NFKD + casefold), mas **sem alterar** esse arquivo: a tokenização da busca fica no serviço novo.
- **Testes dedicados na F1:** a mesma pergunta em versões acentuada, sem acento, em MAIÚSCULAS e em caixa mista retorna exatamente os mesmos chunks e scores (ex.: "Violência psicológica é crime?", "violencia psicologica e crime", "VIOLENCIA PSICOLOGICA É CRIME"). O conjunto de avaliação inclui variantes sem acento das perguntas de teste.
- **Por quê:** a base é pequena e estável; a Anthropic não oferece embeddings (busca vetorial exigiria outro provedor e uma nova análise LGPD); BM25 é determinístico, auditável e testável offline.
- **Divergência registrada:** RF02/RNF04 falam em "base vetorial". A v1.2 cumpre a intenção (top-k + limiar + fonte) e mantém a porta para trocar por busca híbrida no futuro.
- As "Perguntas de teste" são gabarito da avaliação e **não entram no índice**.
- Ficam fora do índice citável: `catalogo/`, `fontes-candidatas.md`, os `README.md` e as notas CFP de "uso interno" (essas vão para o bloco de apoio do prompt).

---

## 6. Fases

### 6.1 Critério de conclusão

Mesmo critério do [plano da jornada §3](./jornada-usuario/plano-implementacao-jornada-usuario.md), sem alterá-lo: implementação · testes · execução local com estados alternativos · conferência com este plano · commit (hash) · publicação · **teste humano na AWS** (só para fases com efeito em produção).

### 6.2 Quadro

| Ordem | ID | Fase | Depende de | Status |
|---:|---|---|---|---|
| 0 | F0 | Preparação: decisões abertas, versionar a base, recursos do Claude Code, dataset de avaliação | — | Desenvolvimento concluído localmente — aguardando revisão do dataset pela usuária e commit (a base entra no commit, D-06) |
| 1 | F1 | Base vigente: versionamento `vX.YY`, ingestão, snapshot, BM25 + seleção pelo LLM (D-12/D-13), gate da CI | F0 | Desenvolvimento concluído localmente — falta medir a seleção com o LLM (precisa de `GEMINI_API_KEY`) e commit |
| 2 | F2 | Motor v1.2 + ajustes autorizados (sem atraso, `[n]` nas fixtures, `503`) | F1 | Desenvolvimento concluído localmente — falta commit, publicação/AWS (F5) e teste humano |
| 3 | F3 | Avaliação (gate CA-03, latência, custo) | F2 | Em andamento — modo rápido executado; modo completo sob demanda (ver `docs/chat/avaliacao-v1-2.md`) |
| 4 | F4 | (Condicional) Busca agêntica limitada (tool de busca, ReAct com teto) | F3 com lacuna de recall | Não iniciada |
| 5 | F5 | CI/CD e publicação (motor `fixtures` por padrão; `llm` por `backend.env`) | F3 (M4 e M5 ok), D-09 | Em andamento — `docker-compose.prod.yml` com `env_file` opcional e guia no `DEPLOY-EC2.md`; a usuária decidiu testar o `llm` na AWS (07/11/2026) |

### F0 — Preparação

1. Decisões D-01, D-02, D-03, D-06 e D-07 resolvidas em 07/11/2026 (seção 7.1). Resta conferir D-09/D-10 quando chegar a hora.
2. Versionar `docs/aurora-base-rag/` no git no primeiro commit da implementação (D-06).
3. Configurar os recursos do Claude Code (seção 8): skill operacional e hook de proteção de `src/frontend/**` e dos serviços que não podem mudar.
4. Montar o dataset `src/backend/evals/v1_2/dataset.jsonl`, com apoio do `/claude-api build-eval`:
   - as 57 perguntas de teste → chunk(s) esperado(s);
   - ≥60 perguntas adversariais (diagnóstico, prescrição, parecer, "devo denunciar?", injeção de prompt);
   - ≥30 fora da base (esperado: `no_source`);
   - frases de risco (esperado: triagem aguda, sem LLM).

**Aceite:** decisões registradas na seção 7; dataset revisado pela usuária; nenhuma alteração de código.
**Skills:** [requisitos](../skills/analise-requisitos-backlog-rastreabilidade.md), [curadoria RAG](../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [guardrails e avaliação](../skills/guardrails-escopo-etico-avaliacao-generativa.md), [qualidade](../skills/engenharia-qualidade-testes-fitness-functions.md).

### F1 — Base vigente e recuperação

1. `versioning.py` (seção 5.3), com testes: ordenação numérica, pastas fora do padrão ignoradas, nenhuma versão → erro.
2. `ingestion.py` + `scripts/build_knowledge_snapshot.py`: parse do YAML e dos chunks; exclusões da seção 5.8; validação estrita.
3. `KnowledgeBaseRepository` + `KnowledgeBaseService` (BM25 com a normalização da seção 5.8, filtro de status configurável — padrão aceita `pendente` conforme D-02 —, limiar) devolvendo `KnowledgeResult` com `KnowledgePassage(text=texto oficial, source=SourceReference(...))`.
4. Testes: parser, determinismo do snapshot, `test_snapshot_matches_latest_base`, **equivalência sem acento / maiúsculas / minúsculas** (seção 5.8), **recall@5** sobre as perguntas de teste (meta inicial ≥85%) e limiar (perguntas fora da base → `no_source`).

**Aceite:** snapshot reprodutível; recall@k e limiar registrados no registro de execução; zero chamadas de rede.
**Skills:** [curadoria RAG](../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [backend](../skills/backend-python-fastapi.md), [qualidade](../skills/engenharia-qualidade-testes-fitness-functions.md).

### F2 — Motor v1.2 e ajustes autorizados

1. `GroundedAnswerService` (seção 5.6): prompt versionado (rascunho em `dialogo-processamento.md` §3), `search_result` com citações, conversão de citações em `[n]`, cadeia de exceções específica do SDK (timeout, rate limit, conexão, status) → `ChatResponseUnavailableError`.
2. `AnswerGuardrailService` (seção 5.5) e `DecisionTraceService` (seção 5.7).
3. Ajustes autorizados (seção 5.2): remover o atraso; `[n]` no `ChatResponseService`; `ChatResponseUnavailableError` → `503`; seleção do motor no `main.py`.
4. Testes **sem rede** (cliente falso do provedor):
   - cada linha da tabela 5.4;
   - triagem e escopo impedem chamar o gerador;
   - `no_source` não chama o gerador;
   - recusa, timeout, guardrail reprovado ou com exceção → `503`;
   - citação para trecho não enviado → reprovação;
   - marcadores coerentes com `sources`;
   - marcador de PII ausente dos logs;
   - fixtures com `[n]`;
   - suíte atual passando com os ajustes previstos.
5. Front (U-06): numeração da lista Fontes e marcadores `[n]` clicáveis em `features/chat`, para os dois motores.
6. Teste local manual com chave real (fora da CI) nos exemplos de `dialogo-processamento.md` §5, pelo front.

**Aceite:** `pytest`, `ruff check`, `ruff format --check` e `compileall` passando; `npm run check` e `npm run build` passando; `git diff --stat develop -- src/frontend` limitado aos arquivos de apresentação de U-06; navegação headless mostrando marcadores ligados às fontes (motor `fixtures` e `v1.2`), 320 px sem overflow; front validando todas as respostas sem erro de formato.
**Skills:** [frontend chat](../skills/frontend-react-typescript-chat.md), [acessibilidade](../skills/acessibilidade-inclusao-linguagem-simples.md), [integração LLM](../skills/integracao-llm-engenharia-prompts.md), [guardrails](../skills/guardrails-escopo-etico-avaliacao-generativa.md), [triagem](../skills/triagem-risco-agudo-avaliacao-seguranca.md), [backend](../skills/backend-python-fastapi.md), [arquitetura](../skills/arquitetura-software-integracao.md), [privacidade](../skills/privacidade-lgpd-governanca-dados.md), [segurança](../skills/seguranca-aplicacao-modelagem-ameacas.md), [observabilidade](../skills/observabilidade-privacidade-desempenho.md), [domínio e trauma](../skills/dominio-violencia-psicologica-design-informado-trauma.md).

### F3 — Avaliação (gate)

1. Runner `src/backend/evals/v1_2/run_eval.py` (manual ou `workflow_dispatch`, com chave):
   - recall@k;
   - **M1** e **M5** por asserção;
   - **M2** e **M3** por LLM-as-judge com saída estruturada + **20% de revisão humana**;
   - **M4**: 50 respostas violadoras injetadas direto no `AnswerGuardrailService` (meta 0);
   - falha fechada;
   - latência p50/p95/p99;
   - custo por pergunta;
   - comparação de modelos (D-01).
2. Revisão qualitativa por especialistas (clareza, linguagem simples, ausência de ordens), com dados sintéticos.
3. Relatório em `docs/chat/avaliacao-v1-2.md` (criado na fase), com a recomendação sobre F4.

**Gate:** M4 = 0 e M5 = 100% obrigatórios para F5.

### F4 — (Condicional) Busca agêntica limitada

**Gatilho:** F3 com recall/M1 abaixo da meta, causado por vocabulário coloquial.
**Escopo:** a tool `buscar_base_conhecimento(consulta)` (`strict: true`, só leitura, no máximo 2–3 chamadas, loop manual com cada passo no trace) dentro do `GroundedAnswerService`. A porta e o contrato não mudam.
**Aceite:** comparação com a F2 no mesmo dataset; adotar só se o recall/M1 melhorar sem piorar M3/M4 e com p95 ≤5 s.

### F5 — CI/CD e publicação

1. O job `backend-tests` já roda os testes novos (sem rede), incluindo o gate do snapshot. Adicionar `ruff` ao job se a usuária aprovar.
2. Workflow `eval-v1-2.yml` (`workflow_dispatch`) é o único com o secret `ANTHROPIC_API_KEY`.
3. Produção: arquivo `/opt/aurora/backend.env` (root, `chmod 600`, nunca reescrito pelo workflow) com `AURORA_CHAT_ENGINE`, `AURORA_LLM_PROVIDER`, `AURORA_LLM_MODEL` e a chave do provedor; `docker-compose.prod.yml` com `env_file: [{path: backend.env, required: false}]` no serviço `backend` (sem o arquivo, sobe em `fixtures`). Trocar de motor: editar o arquivo e `docker compose -f docker-compose.prod.yml up -d --force-recreate backend`. Ativar `llm` após o gate da F3 (D-09). A chave vai em `/opt/aurora/.env` (ajuste do passo de deploy documentado em [DEPLOY-EC2.md](../DEPLOY-EC2.md)).
4. README: seção nova "Motor de chat v1.2", com variáveis, regra da versão da base e como regenerar o snapshot.
5. Teste humano na AWS (R-13).

**Skills:** [DevOps/AWS](../skills/devops-aws-cicd-operacao.md), [segurança](../skills/seguranca-aplicacao-modelagem-ameacas.md), [observabilidade](../skills/observabilidade-privacidade-desempenho.md).

---

## 7. Decisões

### 7.1 Já decididas pela usuária

U-01 a U-06 (seção 1.1), em 07/11/2026, e as decisões abaixo.

| ID | Decisão | Resolução da usuária (07/11/2026) | Consequência no plano |
|---|---|---|---|
| D-01 | Modelo do gerador | **Revisada em 07/11/2026 (D-13):** provedor padrão `gemini` com `gemini-3.5-flash-lite` (plano gratuito; trocado de `gemini-3.6-flash` após a medição); `claude-opus-5-5` (effort `low`) como troca direta por ambiente | Seleção e redação usam o mesmo provedor/modelo configurado. Trocar exige só `AURORA_LLM_PROVIDER`/`AURORA_LLM_MODEL` e a credencial |
| D-02 | Uso de trechos `pendente` | **Pode usar**: todo o projeto está em modo demonstração | `pendente` aceito por padrão (`AURORA_KB_ALLOW_PENDING=true` como padrão nesta fase) e respostas com `demo: true`. `literatura/` é citada pelo resumo da curadoria + DOI/URL. **Ponto de atenção futuro:** antes de qualquer uso real, voltar a exigir `status: aprovado` (regra da base) |
| D-03 | BM25 em vez de base vetorial | **Seguir**, com a exigência de reconhecer palavras **sem acento** e com **qualquer combinação de maiúsculas e minúsculas** | Normalização obrigatória e idêntica no índice e na consulta (seção 5.8); testes dedicados na F1 |
| D-06 | Versionar `docs/aurora-base-rag/` no git | **Sim, nos próximos commits** | Entra no primeiro commit da implementação (F0/F1) |
| D-07 | Envio do texto da usuária à Anthropic | **Liberado sem restrição** nesta fase de demonstração, inclusive na AWS | Não bloqueia F2 nem F5. **Ponto de atenção futuro (registrado na seção 11):** antes de uso com pessoas reais, fazer revisão de privacidade/LGPD (retenção de dados, ZDR, termos do provedor, região, minimização do texto enviado) |
| D-12 | Estratégia de recuperação (descoberta na F1: BM25 puro dá recall@5 de 64% e nenhum limiar separa as perguntas fora da base) | **BM25 traz até 30 candidatos e o LLM configurado (D-13) escolhe até 5 que respondem à mensagem, ou nenhum** | Implementado no `KnowledgeBaseService` por um `ChunkSelector` (`LanguageModelChunkSelector`, sobre a porta `LanguageModel`): saída JSON com schema, timeout 8 s. O seletor só escolhe ids entre os candidatos (o código descarta ids estranhos). Sem candidato ou seleção vazia → `no_source` sem chamar a redação. Falha do seletor → `KnowledgeUnavailableError` → `503` (o router atual já faz esse mapeamento). Duas chamadas ao LLM por pergunta informativa. Teto de recall = recall@30 do BM25 (86% na v0.03) |
| D-13 | Provedor de LLM (a usuária não tem créditos na Anthropic) | **Plano gratuito de outro provedor (Gemini) na demonstração; integração substituível pelo Claude de forma transparente** | Porta `LanguageModel` + adaptadores Gemini/Claude + fábrica por ambiente (§5.6). **Ponto de atenção:** no plano gratuito os dados podem ser usados pelo Google → só dados sintéticos até migrar para plano pago ou Claude |

### 7.2 Abertas

| ID | Decisão | Recomendação | Bloqueia | Status |
|---|---|---|---|---|
| D-09 | Ativar a v1.2 na AWS | **Resolvida em 07/11/2026:** a usuária decidiu testar o `llm` na EC2 após o modo rápido da F3 (M4 = 0 nos testes offline, M5 1/1). Ambiente de demonstração, só dados sintéticos (D-13) | F5 | Resolvida |
| D-10 | Classificador LLM no guardrail de saída | Não na F2; reavaliar com os resultados de M3 | F3 | Aberta |

---

## 8. Recursos do Claude Code

| Recurso | Uso | Fase |
|---|---|---|
| Skill de projeto `.claude/skills/aurora-agente-rag/SKILL.md` | Instruções operacionais para sessões futuras: ler os dois documentos, restrições R-01..R-14, regra da versão da base, comandos de validação | F0 |
| Hook `PreToolUse` (Edit/Write) via skill `update-config` | Pedir confirmação ao editar `src/frontend/**` (só U-06 é permitido), `services/{triage,guardrail,knowledge,content_offer}/**` e `docs/jornada-usuario/**` | F0 |
| `/claude-api build-eval` | Dataset e método de correção (aprovar o custo antes) | F0/F3 |
| `/claude-api hillclimb` / `cost-optimize` | Iterar o prompt / revisar o custo com dados reais (opcional) | F3 |
| Skill `claude-api` | Consultar antes de escrever código do SDK | F2/F4 |
| `/run` ou `browser-automation` | Conferir no front as respostas, os marcadores `[n]` clicáveis e a lista Fontes numerada | F2 |
| `/code-review`, `/security-review` | Antes de cada merge | F2/F5 |
| Skill `anthropic-skills:arquitetura-vsa-ddd` | Revisar as fronteiras dos serviços novos | F2 |
| Memória do projeto | Ponteiro para este plano | Feito em 07/11/2026 |

---

## 9. Referências

**Plano de estudos (fora do repositório)**
- `C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Dissertação\planejamento\plano-estudo-8-semanas.md` (arquivo único). Seção 4 deste plano: só a parte de consulta a documentos e resposta.

**Aurora**
- [Requisitos](./requisitos-aurora.md) · [Arquitetura operacionalizada](./arquitetura_operacionalizada_aurora.md) · [Backlog](./backlog-aurora.md) · [README](../README.md) · [Deploy EC2](../DEPLOY-EC2.md) · [CI/CD](../.github/workflows/deploy.yml)
- Somente leitura: [plano da jornada](./jornada-usuario/plano-implementacao-jornada-usuario.md) · [contratos do protótipo](./jornada-usuario/contratos-integracao-mocks.md) · [jornada do usuário](./jornada-usuario/jornada-do-usuario.md)

**Base de conhecimento**
- Raiz: [docs/aurora-base-rag/](./aurora-base-rag/) · vigente em 07/11/2026: [v0.03](./aurora-base-rag/v0.03/) · [regras da base](./aurora-base-rag/v0.03/legislacao/README.md) · [catálogo (não-RAG)](./aurora-base-rag/v0.03/catalogo/solucoes-externas-indicaveis.md)

**Skills** — [índice](../skills/lista_skills.md) e os links em cada fase.

**Código de referência**
- [handler](../src/backend/src/aurora_backend/contexts/conversation/features/send_message/handler.py) · [router](../src/backend/src/aurora_backend/contexts/conversation/features/send_message/router.py) · [portas](../src/backend/src/aurora_backend/contexts/conversation/services/) · [main.py](../src/backend/src/aurora_backend/main.py) · [chatApi.ts (validação do front)](../src/frontend/src/features/chat/api/chatApi.ts)

**Externas**
- Anthropic: prompt engineering, tool use, citations / search results, prompt caching (docs.claude.com) · ReAct (arXiv:2210.03629).

---

## 10. Rastreabilidade

| Requisito / CA | Onde |
|---|---|
| RF02, RNF04, CA-03 M1/M2/M5 | F1 (recuperação, limiar), F2 (citações, `[n]`, guardrail), F3 |
| RF03, RNF03 | Triagem existente mantida antes do LLM (U-01) |
| RF10, RNF06, CA-03 M3/M4 | Guardrail de entrada existente + guardrail de saída novo; F3 |
| RNF01, CA-01 | Trace sem conteúdo; sem histórico; D-07 |
| RNF05 | Portas existentes reutilizadas; o SDK fica só no `GroundedAnswerService` |
| RNF07, CA-04 | Atraso removido (U-02); p95 medido na F3 |
| E3, E13 | v1.2 |

---

## 11. Riscos

| Risco | Mitigação |
|---|---|
| Base 100% `pendente` | D-02: aceito em demonstração com `demo: true`; **futuro:** exigir `aprovado` antes de uso real |
| Plano gratuito do Gemini pode usar os dados enviados (D-13) | Só dados sintéticos até migrar para plano pago ou Claude; registrado no adaptador e neste plano |
| Envio do relato a provedor externo sem revisão de privacidade | D-07: aceito na demonstração; **futuro:** revisão LGPD (retenção, ZDR, termos, região, minimização) antes de uso real |
| Telefone, prazo ou pena inventados | Citações + regra de contatos e links + `503` em caso de dúvida |
| Injeção de prompt | Trechos como `search_result` (dados); system prompt; dataset adversarial; guardrail independente do prompt |
| Nova versão da base com formato diferente | Ingestão estrita que falha alto; gate do snapshot na CI |
| Esquecer de reler a base nova | `test_snapshot_matches_latest_base` quebra a CI |
| Latência > 5 s | Sem multi-agente, sem atraso simulado, effort baixo, caching, timeout de 8 s |
| Custo | Medição real na F3; D-01; avaliação manual, não a cada push |
| Alteração indevida do front | R-01 (só U-06) + hook + `git diff --stat develop -- src/frontend` |

---

## 12. Registro de execução

| Data | Fase | O que foi feito | Evidência | Responsável |
|---|---|---|---|---|
| 07/11/2026 | — | Análise de aplicabilidade; criação deste plano e de `docs/chat/dialogo-processamento.md`; branch `feature/v1.2-agente-rag` | Documentos na branch (sem commit) | Claude Code + usuária |
| 07/11/2026 | — | Revisão 2: front inalterado, backend sem textos fixos, triagem e escopo determinísticos, atraso removido, marcadores `[n]` nos dois motores, base em `docs/aurora-base-rag/vX.YY` (sempre a vigente), livro H-ACD fora do escopo | Este arquivo | Claude Code + usuária |
| 07/11/2026 | — | U-06: front autorizado a mudar só para exibir a fonte por trecho (lista Fontes numerada + `[n]` clicável) | Este arquivo | Claude Code + usuária |
| 07/11/2026 | — | Decisões D-01, D-02, D-03 (com normalização sem acento e sem diferença de caixa), D-06 e D-07 resolvidas pela usuária; pontos de atenção futuros registrados (exigir `aprovado` e revisão LGPD antes de uso real) | Seção 7.1 | Claude Code + usuária |
| 07/11/2026 | F0 | (1) Hook `PreToolUse` em `.claude/settings.json` + `.claude/hooks/protect-paths.js`: pede confirmação ao editar `src/frontend/**`, `services/{triage,guardrail,knowledge,content_offer}/**` e `docs/jornada-usuario/**`. Testado por pipe com caminhos Windows reais; passa a valer após `/hooks` ou reinício da sessão. (2) Skill `.claude/skills/aurora-agente-rag/SKILL.md`. (3) Dataset `src/backend/evals/v1_2/dataset.jsonl` (base v0.03, 338 casos): 78 perguntas de teste da base (cobrem 55 dos 81 chunks) + 156 variantes sem acento/maiúsculas + 60 adversariais + 30 fora da base + 10 de risco + 4 fixtures de escopo. Gerado por `evals/v1_2/build_dataset.py` (lê sempre a versão vigente) a partir de `cases_manual.jsonl`. (4) Suíte existente intacta: 166 testes, ruff check/format ok. O método de correção e o custo da avaliação com API (`/claude-api build-eval`) ficam para a F3 | Arquivos não commitados na branch | Claude Code |
| 07/11/2026 | F1 | **Implementado em `services/knowledge_base/`:** `versioning` (maior `vX.YY`; hash SHA-256 com fins de linha normalizados), `ingestion` (YAML via PyYAML só em dev; validação estrita), `repository`, `search` (normalização D-03 + BM25 próprio), `selector` (`ClaudeChunkSelector`, D-12) e `service` (`KnowledgeBaseService`, porta `KnowledgeRetriever`). Também `scripts/build_knowledge_snapshot.py` e `evals/v1_2/run_retrieval_eval.py`. **Snapshot v0.03 (`8222eba1fafd`):** 81 chunks, 78 pesquisáveis (55 com texto oficial, 7 com dados, 16 com resumo da curadoria, porque os 13 "Trecho da fonte" dos guias são placeholders `[colar…]` e a literatura só tem resumo) e 3 internos (`uso: INTERNO`). **Medições BM25 (sem rede):** recall@1 35,9%, @5 64,1%, @30 85,9%. Variantes sem acento e em maiúsculas têm **exatamente** o mesmo recall (D-03 ok). Nenhum limiar absoluto ou relativo separa as perguntas fora da base sem perder ~40% do recall → decisão D-12. **Seleção pelo Claude:** não medida (sem `ANTHROPIC_API_KEY` nesta máquina); rodar `uv run python evals/v1_2/run_retrieval_eval.py --claude` (~108 chamadas). **Testes:** 209 passando (43 novos da base); ruff check/format e compileall ok. Gate da CI `test_snapshot_matches_latest_base` ativo. Ambiente: o diretório `.venv/.../aurora_backend-0.1.0.dist-info` estava somente leitura e travava o `uv`; o atributo foi removido | Arquivos não commitados | Claude Code |
| 07/11/2026 | F1 (rev.) | **D-13:** porta `LanguageModel` (`services/language_model/`: `port`, `gemini`, `claude`, `factory`). O seletor virou `LanguageModelChunkSelector` (sem SDK). Dependência `google-genai>=3.0.0,<4` (3.0.0). Padrão inicial `AURORA_LLM_PROVIDER=gemini` / `gemini-3.6-flash` (depois trocado para `gemini-3.5-flash-lite`). `evals/v1_2/run_retrieval_eval.py --llm --rpm 10` usa o provedor do ambiente. Testes: 228 passando (adaptadores Gemini e Claude com clientes falsos, fábrica, seletor pela porta); ruff e compileall ok. Medição real da seleção pendente de `GEMINI_API_KEY` | Arquivos não commitados | Claude Code |
| 07/11/2026 | F1 (medição) | **Seleção pelo LLM medida** (`run_retrieval_eval.py --llm --rpm 10`, base v0.03, 108 chamadas): com `gemini-3.5-flash-lite`, **recall@5 = 83,3% (65/78)** contra 64,1% do BM25 sozinho; o teto (recall@30 do BM25) é 85,9%, ou seja, o seletor aproveitou 65 dos 67 casos alcançáveis. **Fora da base → sem fonte: 28/30.** Falhas técnicas (503): 2. **Achados do Gemini gratuito:** (a) a API exige prazo mínimo de 10 s por requisição (o adaptador agora usa ≥ 10 s); (b) `503 high demand` frequente → até 3 tentativas só para 500/503/504, limite total de 25 s; (c) `gemini-3.6-flash` estourou a cota gratuita (429) quase sempre, enquanto `gemini-3.5-flash-lite` respondeu em ~1 s → recomendação de trocar o modelo padrão | Saída do script; testes do adaptador | Claude Code |
| 07/11/2026 | F2 (parcial) | **Roteamento por `AURORA_CHAT_ENGINE` (U-07):** `contexts/conversation/engine.py` (`fixtures` / `base` / `llm`, fail-fast), `SourceReplyService` (resposta com abertura neutra + `[n]` nos modos `base`/`llm`), composição em `main.py`, `docker-compose.yml` local com `env_file` opcional. Testes: 238 passando (10 novos, incluindo HTTP de ponta a ponta no modo `base` sem rede). **Prova com uvicorn real:** os três motores sobem e o log mostra o motor ativo; "Ele me filmou…" → `llm` devolve `cp-art216b-218c#216B`; "previsão do tempo" → `llm` sem fonte, mas **`base` devolve trechos irrelevantes** (limiar BM25 2,0 fraco; conhecido). O atraso simulado de 5 s continua (sai na F2, U-02) | Arquivos não commitados | Claude Code |
| 07/11/2026 | D-01 | Modelo padrão do Gemini trocado para `gemini-3.5-flash-lite` (código, testes, `.env` local e skill), com base na medição da F1 | Este arquivo | Usuária + Claude Code |
| 07/11/2026 | F2 | **Concluída localmente.** (1) Ajustes autorizados no chat atual: atraso simulado de 5 s removido do router (U-02); `ChatResponseUnavailableError` (porta) → `503`; marcadores `[n]` no `ChatResponseService` de fixtures (U-03); testes existentes ajustados para "sem atraso". (2) `GroundedAnswerService` (`services/grounded_answer/`): prompt versionado `system_v1_2.md` (hash no trace), resposta do LLM em JSON de segmentos → `[n]` na ordem de `sources`; resumo e notas de "Atenção" de cada trecho entram como apoio não citável. (3) `AnswerGuardrailService` (`answer_guardrail@1`): sem citação, id desconhecido, fato numérico sem fonte, diagnóstico, prescrição, decisão coerciva, parecer individual, agir em nome da usuária, telefone fora de 180/190/192/188 e link fora das fontes → reprovação → `503`. Os testes pegaram e corrigiram um defeito na detecção de telefone com pontuação final. (4) `DecisionTraceService`: um evento JSON por resposta, com lista branca de campos (sem mensagem, resposta ou trecho). (5) Motor `llm` = seleção + redação pelo LLM; `base` segue com `SourceReplyService`. (6) Front (U-06): `CitedText` (`[n]` → link acessível com `aria-label` "Fonte n: título"), lista Fontes como `<ol>` numerada com âncoras e destaque `:target`; `npm run check`/`build` ok; diff do front restrito a `MessageList.tsx`, `styles.css` e `CitedText.tsx` (novo). **Testes:** 280 passando (25 de guardrail com respostas violadoras sintéticas, 13 de redação, HTTP 503 por guardrail). **Prova real (Gemini `gemini-3.5-flash-lite`, motor `llm`):** "Ele me filmou…" → resposta em linguagem simples citando `cp-art216b-218c#216B` com `[1]` e frase de limite; "previsão do tempo" e "estou com depressão?" → sem fonte; ~6–8 s por resposta (2 chamadas ao LLM; acima da meta de 5 s, limitação do plano gratuito a medir na F3). **Navegador headless:** `[1]` renderizado como link que leva à fonte `[1]`, 320 px sem overflow, `localStorage`/`sessionStorage` vazios; único erro de console é o 404 de `/favicon.ico`, já registrado antes. **Aviso de demonstração ajustado (U-08):** "found" → "resposta baseada nas fontes listadas, que ainda estão em revisão jurídica e técnica. Pode conter erros e não é orientação sobre o seu caso."; "no_source" → "a base de fontes do protótipo ainda está em revisão e pode não cobrir esta pergunta." Os textos valem para qualquer motor | Arquivos não commitados | Claude Code |
| 07/11/2026 | F3 | `evals/v1_2/run_answer_eval.py` (fluxo real com motor `llm`, juiz opcional para M2/M3, limite de requisições por minuto). **Decisão da usuária:** o padrão é o modo rápido, com 1 caso por categoria (~1–2 min); o modo completo (182 casos, ~1 h no plano gratuito) fica sob demanda com `--limit 0`. Nenhum dos dois roda na CI ou no deploy (dependem de chave/cota); a CI segue só com os testes offline. Resultado do modo rápido: M1 100%, M2 5/5, M3 0/2, M5 1/1, risco/escopo sem LLM 2/2, 0 falhas; latência 4,2–8,3 s. Corrigido o cálculo de p95 no script. Relatório: `docs/chat/avaliacao-v1-2.md` | Arquivos não commitados | Usuária + Claude Code |
| 07/11/2026 | F5 | `docker-compose.prod.yml`: serviço `backend` com `env_file: [{path: backend.env, required: false}]` (Compose v5.6.0 na EC2; sem o arquivo, sobe em `fixtures`). `DEPLOY-EC2.md`: seção "Motor do chat e LLM (v1.2)" (criar `/opt/aurora/backend.env` com root e `chmod 600`, conteúdo para Gemini/Claude, recriar o backend sem novo deploy, cuidados de privacidade, cota e latência). Compose de produção e local validados com `docker compose config` (WSL). Publicação: fast-forward da `develop` para esta branch e push, que dispara o workflow | Arquivos não commitados | Claude Code |
| 07/11/2026 | F5 | **Teste na AWS com `llm`.** (1) O primeiro deploy derrubou o backend ao ligar o `llm`: `gemini.py` importava `httpx`, que só existe como dependência de dev. O serviço foi restaurado com `fixtures` em cerca de 1 min, a correção usa só `httpx2` (commit `e63b610`) e um teste novo garante que todo pacote importado pela aplicação está nas dependências de produção. Validado na imagem Docker e reimplantado. (2) `llm` ativo na EC2 (`backend.env`, imagem `sha-e63b610`): 'Ele me filmou…' → resposta com `[1]` em 2,3 s; 'controla tudo…' → 5 fontes, citações `[1][3]`, 2,4 s; 'previsão do tempo' → sem fonte em 0,9 s; 'vai me matar' → triagem aguda em 0,3 s. (3) **U-09:** a usuária encontrou o layout quebrado em janela baixa; diagnóstico e correção no `styles.css`. Verificado no navegador headless em 1364×620, 1364×900, 375×667 e 320×568: antes, depois de digitar e depois de clicar no `[1]`, o cabeçalho ficou no topo, a caixa de texto inteira na tela e nenhum contêiner rolou além da lista e da coluna lateral | Prints da verificação | Usuária + Claude Code |
