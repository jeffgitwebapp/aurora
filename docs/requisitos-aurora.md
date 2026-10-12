# Projeto Aurora — Requisitos Funcionais e Não Funcionais

**Disciplina:** Arquitetura de Software — MPES / CESAR School
**Versão:** 1.0 — Agosto/2026
**Base:** TAP v1, Matriz de Encaminhamento Aurora, Justificativa do Projeto, Backlog Aurora, "O Problema: A Crise Invisível da Violência Psicológica"

---

## 1. Contexto do Sistema

O **Projeto Aurora** é uma plataforma de **psicoeducação e informação** (PWA + LLM com RAG) destinada a mulheres em situação de violência psicológica. Seu propósito é atuar sobre três lacunas documentadas:

| Lacuna | Descrição | Evidência |
|---|---|---|
| **Reconhecimento** | A violência psicológica é invisível; a vítima frequentemente não a nomeia como violência | 94% dos casos de violência doméstica envolvem componente psicológico |
| **Informação** | Desconhecimento de direitos (Lei 11.340/06, Lei 14.188/21) e da rede de proteção existente | ~3,7 milhões de mulheres afetadas anualmente no Brasil |
| **Risco digital** | O agressor frequentemente monitora o dispositivo da vítima | Necessidade de camuflagem e ausência de rastro |

### Limites de escopo (definidos no TAP)

O Aurora **NÃO**:

- realiza diagnóstico clínico ou psicológico;
- oferece psicoterapia ou relação terapêutica;
- presta aconselhamento jurídico individualizado;
- decide ou age pela usuária.

O Aurora **SIM**:

- ajuda a **reconhecer** padrões de violência com base em literatura citável;
- **informa** direitos e recursos existentes;
- **sugere** qual entidade da rede de proteção procurar, segundo hierarquia jurídica. O contato com o serviço é ação da própria usuária.

---

## 2. Requisitos Funcionais

### RF01 — Relatar Situação de Violência

| Campo | Conteúdo |
|---|---|
| **Ator** | Usuária |
| **Descrição** | A usuária descreve sua situação em linguagem natural, por texto livre, em interface conversacional. |
| **Pré-condição** | Acesso à PWA (não requer cadastro nem login no modo anônimo). |
| **Fluxo principal** | 1. Usuária abre a PWA → 2. Sistema apresenta tela de acolhimento com botão de Saída Rápida sempre visível → 3. Usuária digita o relato → 4. Sistema processa o texto sem persistir identificadores. |
| **Pós-condição** | Relato disponível em memória de sessão volátil para as etapas de triagem e psicoeducação. |
| **RNF vinculados** | RNF01 (anonimato), RNF06 (LGPD/ética), RNF07 (desempenho) |
| **Épico do backlog** | E1, E3 |

### RF02 — Consultar Conteúdo Psicoeducativo

| Campo | Conteúdo |
|---|---|
| **Ator** | Usuária |
| **Descrição** | O sistema recupera, via RAG, conteúdo da base de conhecimento oficial e devolve informação científica e **citável** sobre ciclo do abuso, tipos de violência psicológica (gaslighting, isolamento, controle coercitivo, chantagem emocional) e direitos previstos em lei. |
| **Pré-condição** | Base vetorial indexada e versionada. |
| **Fluxo principal** | 1. Sistema recebe a consulta → 2. Recuperador busca top-k trechos na base vetorial → 3. Guardrails validam o escopo da resposta → 4. Gerador produz resposta ancorada → 5. Resposta é exibida **com as fontes citadas**. |
| **Fluxo alternativo** | Se não houver trecho relevante acima do limiar de similaridade, o sistema declara a limitação em vez de gerar conteúdo não fundamentado. |
| **Pós-condição** | Resposta entregue com ≥1 fonte rastreável (artigo de lei, cartilha oficial ou literatura científica). |
| **RNF vinculados** | RNF04 (rastreabilidade), RNF06 (limites éticos), RNF07 (desempenho) |
| **Épico do backlog** | E3, E6, E13 |

### RF03 — Realizar Triagem de Risco

| Campo | Conteúdo |
|---|---|
| **Ator** | Usuária |
| **Descrição** | O sistema processa o relato para classificar o risco em três variáveis: **urgência**, **tipo de necessidade** e **localização**. Detecta sinais agudos — ideação suicida, agressão em curso, ameaça de morte, presença de arma. |
| **Fluxo principal** | 1. Classificador de urgência analisa o relato → 2. Se risco agudo, o fluxo é **interrompido** e a sugestão prioritária de emergência é exibida imediatamente → 3. Se não agudo, segue para classificação de necessidade e localização. |
| **Regra crítica** | A sugestão prioritária de emergência deve ser **exibida** em **100%** dos casos detectados, antes de qualquer conteúdo psicoeducativo. O contato com o serviço é ação da usuária, fora do sistema. |
| **RNF vinculados** | RNF03 (confiabilidade da triagem), RNF07 (desempenho) |
| **Épico do backlog** | E4 |

### RF04 — Obter Encaminhamento Priorizado

| Campo | Conteúdo |
|---|---|
| **Ator** | Usuária |
| **Descrição** | Com base na triagem (localização + tipo de necessidade), o sistema apresenta opções de ajuda da Matriz de Encaminhamento, respeitando a **hierarquia jurídica**: órgãos públicos formais → serviços especializados → organizações da sociedade civil → voluntariado. |
| **Regra de hierarquia** | Delegacia da Mulher (DEAM) e Defensoria Pública precedem ONGs e projetos voluntários em qualquer cenário de natureza jurídica. |
| **Fluxo principal** | 1. Sistema consulta o Catálogo de Serviços com os parâmetros da triagem → 2. Motor de priorização aplica a hierarquia → 3. Sistema exibe até 3 opções com nome, natureza, canal de contato e horário de funcionamento. |
| **Meta de qualidade** | Acurácia de encaminhamento ≥95% em testes roteirizados; máximo de 3 cliques até o recurso. |
| **RNF vinculados** | RNF03, RNF05, RNF07 |
| **Épico do backlog** | E5 |

### RF05 — Atualizar Catálogo de Serviços

| Campo | Conteúdo |
|---|---|
| **Ator** | Administrador |
| **Descrição** | Permite inserção, edição, desativação e **versionamento** de serviços parceiros e da base de conhecimento citável. |
| **Pré-condição** | Autenticação administrativa com perfil autorizado. |
| **Fluxo principal** | 1. Admin acessa painel → 2. Cadastra/edita serviço (nome, natureza jurídica, abrangência, canal, horário, cenários atendidos) → 3. Sistema versiona o registro → 4. Publicação entra em vigor **sem interrupção do serviço** (hot reload de cache/índice). |
| **Requisito de continuidade** | Atualização não pode gerar downtime perceptível para a usuária final. |
| **RNF vinculados** | RNF02 (disponibilidade), RNF05 (manutenibilidade), RNF06 (auditoria) |
| **Épico do backlog** | E11, E13 |

### Requisitos funcionais complementares

| ID | Requisito | Origem |
|---|---|---|
| RF06 | Saída Rápida (Quick Exit) — abandono imediato da sessão com redirecionamento neutro e limpeza de histórico | E1 |
| RF07 | Camuflagem da PWA — ícone e título neutros, sem rastro de instalação | E1 |
| RF08 | Registro de incidentes em diário local criptografado (modo logado, opcional) | E7 |
| RF09 | Painel administrativo com métricas agregadas e não identificáveis | E11 |
| RF10 | Guardrails de escopo — bloqueio de solicitações de diagnóstico, prescrição ou parecer jurídico individualizado | E13 |

---

## 3. Requisitos Não Funcionais

### RNF01 — Anonimato e Privacidade

**Definição:** o sistema não coleta, não trafega e não persiste dados de identificação pessoal (PII) da usuária.

**Critérios verificáveis:**

- Nenhum campo de nome, CPF, e-mail, telefone ou endereço no modo anônimo.
- Ausência de cookies de rastreamento e de identificadores de terceiros.
- Localização capturada apenas em granularidade de **município/UF**, informada pela usuária, nunca por geolocalização precisa.
- Sessão volátil: relato mantido apenas em memória, descartado ao encerramento.
- Logs de aplicação sem conteúdo do relato.

**Atributo ISO/IEC 25010:** Segurança → *Confidencialidade*
**Impacto arquitetural:** sessão sem estado persistente; ausência de banco de usuários no fluxo anônimo; anonimização antes de qualquer telemetria.

---

### RNF02 — Disponibilidade

**Definição:** o sistema opera 24 horas por dia, 7 dias por semana.

**Critérios verificáveis:**

- Disponibilidade alvo: **99,5% mensal** (≈ 3h39min de indisponibilidade máxima/mês).
- Degradação graciosa: se o serviço de LLM estiver indisponível, o sistema mantém acesso à sugestão estática de emergência e ao conteúdo psicoeducativo pré-renderizado.
- PWA com service worker: conteúdo essencial e sugestão de emergência disponíveis **offline** — apenas após o primeiro carregamento bem-sucedido.

**Justificativa:** a violência doméstica tem pico noturno e em finais de semana — janelas nas quais serviços presenciais estão fechados. Indisponibilidade nesse horário anula o valor do sistema.

**Atributo ISO/IEC 25010:** Confiabilidade → *Disponibilidade*, *Tolerância a falhas*
**Impacto arquitetural:** múltiplas zonas de disponibilidade, CDN para o front, fallback estático, health checks.

---

### RNF03 — Confiabilidade da Triagem

**Definição:** acurácia ≥95% nos cenários gerais e **100%** em cenários de emergência e na hierarquia jurídica, validada por testes roteirizados.

**Critérios verificáveis:**

| Categoria | Meta | Método de validação |
|---|---|---|
| Encaminhamento geral (19 cenários da Matriz) | ≥95% | Suíte de testes roteirizados com casos-âncora por cenário |
| Detecção de risco agudo e exibição da sugestão de emergência | 100% | Casos de teste com sinais agudos explícitos e implícitos |
| Respeito à hierarquia jurídica | 100% | Verificação de ordenação: público formal antes de voluntário |

- Falso negativo em emergência é considerado **defeito bloqueante** (severidade máxima).
- Regressão obrigatória a cada atualização do modelo, prompt ou catálogo.

**Atributo ISO/IEC 25010:** Confiabilidade → *Maturidade*; Adequação Funcional → *Correção funcional*
**Impacto arquitetural:** classificador de urgência determinístico (regras + palavras-âncora) **em paralelo** ao classificador semântico; a regra determinística tem precedência — prefere-se falso positivo a falso negativo.

---

### RNF04 — Fundamentação e Rastreabilidade do Conteúdo (RAG)

**Definição:** respostas baseadas em fontes citáveis (artigos de lei, cartilhas oficiais, literatura científica), reduzindo alucinação do modelo de IA.

**Critérios verificáveis:**

- **≥90%** das respostas de conteúdo exibem ao menos uma fonte rastreável (meta do TAP).
- Toda fonte da base possui metadados: título, autoria/órgão, ano, URL ou referência, versão do documento.
- Limiar mínimo de similaridade na recuperação; abaixo dele o sistema responde com declaração de limitação em vez de gerar texto.
- **≤5%** de respostas fora do escopo definido (meta do TAP).

**Atributo ISO/IEC 25010:** Adequação Funcional → *Correção funcional*; Confiabilidade → *Maturidade*
**Impacto arquitetural:** base vetorial versionada; pipeline de ingestão com curadoria humana; camada de citação obrigatória entre gerador e apresentação.

---

### RNF05 — Escalabilidade e Manutenibilidade

**Definição:** arquitetura que permita atualização contínua da base de serviços parceiros sem downtime significativo.

**Critérios verificáveis:**

- Atualização do Catálogo de Serviços com **zero downtime** (invalidação de cache e reindexação incremental em background).
- Reindexação da base de conhecimento sem interromper consultas — índice novo publicado por *alias swap*.
- Escala horizontal automática dos serviços de aplicação sob variação de carga (campanhas públicas geram picos).
- Módulos desacoplados: substituir o provedor de LLM não deve exigir alteração no domínio.

**Atributo ISO/IEC 25010:** Manutenibilidade → *Modularidade*, *Modificabilidade*; Eficiência de Desempenho → *Capacidade*
**Impacto arquitetural:** arquitetura hexagonal (portas e adaptadores) isolando o provedor de LLM; catálogo em serviço próprio com cache invalidável; blue-green ou rolling deploy.

---

### RNF06 — Conformidade Legal e Ética

**Definição:** aderência à LGPD — mesmo sem PII, o relato constitui dado sensível — e aos limites éticos definidos: não diagnosticar, não prestar aconselhamento jurídico individualizado, não decidir pela mulher.

**Critérios verificáveis:**

| Dimensão | Controle |
|---|---|
| LGPD — minimização | Coleta restrita ao estritamente necessário (Art. 6º, III) |
| LGPD — finalidade | Aviso de privacidade em linguagem simples na primeira interação |
| LGPD — segurança | Criptografia em trânsito (TLS 1.3) e em repouso para dados do modo logado |
| Ética — não diagnóstico | Guardrail bloqueia formulações do tipo "você tem/sofre de [transtorno]" |
| Ética — não aconselhamento jurídico | Guardrail restringe a resposta a informação sobre a lei, sem parecer sobre o caso concreto |
| Ética — autonomia | Sistema apresenta opções; nunca instrui "você deve denunciar/sair de casa" |
| Auditoria | Registro versionado de prompts, guardrails e conteúdo da base |

**Atributo ISO/IEC 25010:** Segurança → *Conformidade*, *Integridade*; Adequação Funcional → *Adequação*
**Impacto arquitetural:** camada de guardrails obrigatória entre gerador e apresentação, com bloqueio *fail-closed*; versionamento auditável de prompts.

---

### RNF07 — Desempenho

**Definição:** tempo de resposta rápido o suficiente para não gerar fricção em momento de crise.

#### Fundamentação por benchmark

A literatura de interação humano-computador e os benchmarks de sistemas RAG convergem para as seguintes faixas:

| Referência | Faixa | Interpretação |
|---|---|---|
| Limiares de Nielsen (HCI) | 0,1 s / 1 s / 10 s | 0,1 s = instantâneo; 1 s = mantém o fluxo de pensamento; 10 s = limite antes do abandono |
| Latência aceitável para RAG interativo (Milvus/Zilliz) | 1–3 s ponta a ponta; recuperação e geração ≤500–1000 ms cada | Faixa de referência para chatbot conversacional |
| Prática de benchmarking RAG | <3 s para consultas curtas; <5 s para consultas longas | Critério operacional de teste |
| Expectativa de usuários de chatbot (2024) | <1 s percebido; degradação de satisfação acima de 2 s | 82% esperam resposta praticamente imediata |

#### Metas adotadas pelo Aurora

| Operação | Meta (p95) | Limite máximo (p99) | Justificativa |
|---|---|---|---|
| **Exibição da sugestão de emergência** (RF03, risco agudo) | **≤ 500 ms** | 1 s | Caminho determinístico, sem LLM. Resposta em momento de risco de vida não pode depender de inferência. |
| **Encaminhamento** (RF04, consulta ao catálogo) | **≤ 1 s** | 2 s | Consulta a base estruturada com cache; deve manter o fluxo de pensamento (limiar de 1 s de Nielsen). |
| **Primeiro token da resposta psicoeducativa** (RF02) | **≤ 1,5 s** | 2,5 s | *Streaming* de resposta: a percepção de espera é governada pelo primeiro token, não pela resposta completa. |
| **Resposta psicoeducativa completa** (RF02) | **≤ 3 s** | 5 s | Alinhado ao benchmark de RAG interativo. |
| **Carga inicial da PWA** | **≤ 2 s** em 3G | 4 s | Usuárias podem estar em conexão precária; a camuflagem exige carregamento rápido para não chamar atenção. |
| **Saída Rápida** (RF06) | **≤ 200 ms** | 300 ms | Ação de segurança física — atraso perceptível representa risco real. |

**Decisão de projeto derivada:** a exibição da sugestão de emergência e a Saída Rápida são **implementadas sem dependência de LLM**, executando por regras determinísticas no cliente e/ou em serviço leve. Isso desacopla o requisito de segurança da latência variável da inferência.

**Atributo ISO/IEC 25010:** Eficiência de Desempenho → *Comportamento temporal*
**Impacto arquitetural:** streaming de tokens (SSE/WebSocket); cache de respostas frequentes; sugestão de emergência embarcada no service worker; recuperação vetorial com índice ANN (HNSW).

---

## 4. Atributos de Qualidade Priorizados (ISO/IEC 25010)

Seleção justificada dos atributos mais relevantes para o domínio.

| Prioridade | Característica ISO 25010 | Subcaracterística | RNF | Por que é crítico neste domínio |
|---|---|---|---|---|
| **1** | Segurança (Security) | Confidencialidade | RNF01 | Vazamento de identidade pode resultar em **agravamento da violência ou morte**. É o atributo de maior severidade. |
| **2** | Confiabilidade (Reliability) | Maturidade / Tolerância a falhas | RNF03 | Falha na detecção de emergência tem consequência irreversível. |
| **3** | Adequação Funcional | Correção funcional | RNF03, RNF04 | Encaminhamento incorreto desperdiça a única janela de coragem da usuária. |
| **4** | Confiabilidade | Disponibilidade | RNF02 | O pico de necessidade ocorre fora do horário de funcionamento dos serviços presenciais. |
| **5** | Eficiência de Desempenho | Comportamento temporal | RNF07 | Fricção em situação de crise gera abandono; a usuária pode não ter uma segunda oportunidade de acesso. |
| **6** | Segurança | Conformidade | RNF06 | Exposição jurídica do projeto e risco ético de dano à usuária. |
| **7** | Manutenibilidade | Modularidade / Modificabilidade | RNF05 | A rede de proteção muda constantemente; catálogo desatualizado encaminha para serviço inexistente. |
| **8** | Usabilidade | Proteção contra erro do usuário / Acessibilidade | RF06, E9 | Design trauma-informado: baixa carga cognitiva sob estresse agudo. |

### Trade-offs entre atributos

| Tensão | Resolução adotada |
|---|---|
| **Anonimato (RNF01) × Personalização** | Prevalece o anonimato. O modo logado é **opt-in** e usa identificador pseudonimizado, jamais PII. |
| **Desempenho (RNF07) × Rastreabilidade (RNF04)** | Recuperação vetorial acrescenta latência. Mitigado por índice ANN + cache + streaming, mantendo a citação obrigatória. |
| **Confiabilidade da triagem (RNF03) × Naturalidade da conversa** | Prevalece a confiabilidade. Regras determinísticas têm precedência sobre o classificador semântico, ainda que interrompam abruptamente a conversa. |
| **Disponibilidade (RNF02) × Custo** | Multi-AZ sim, multi-região não, dado o orçamento de R$ 5.865 do TAP. Fallback estático offline compensa parcialmente. |
| **Anonimato (RNF01) × Observabilidade** | Telemetria estritamente agregada e não identificável; logs jamais contêm o relato. |

---

## 5. Restrições de Projeto

| # | Restrição | Origem | Consequência arquitetural |
|---|---|---|---|
| R1 | Orçamento de **R$ 5.865** | TAP v1 | Uso de serviços gerenciados de baixo custo; sem multi-região; LLM via API em vez de modelo próprio. |
| R2 | Cronograma **M1 (Jul/2026) → M6 (Jan/2027)** | TAP v1 | Escopo mínimo viável priorizado; E13 (base citável + guardrails) antecipado para M1/M2. |
| R3 | Equipe acadêmica de tempo parcial | MPES | Preferência por stack conhecido e componentes gerenciados sobre construção própria. |
| R4 | Proibição de diagnóstico e aconselhamento jurídico individualizado | Justificativa / TAP | Camada de guardrails é componente obrigatório, não opcional. |
| R5 | Aderência à LGPD | Legal | Arquitetura *privacy by design*; ausência de banco de usuários no fluxo anônimo. |
| R6 | Dispositivo potencialmente monitorado pelo agressor | Justificativa | PWA sem rastro de instalação; Saída Rápida; ausência de notificações push. |
| R7 | Conectividade precária e dispositivos de baixo custo | Contexto socioeconômico | Bundle leve, service worker, funcionamento offline do conteúdo essencial. |
| R8 | Dependência de provedor externo de LLM | Técnica | Adaptador isolado (porta/adaptador) e degradação graciosa quando indisponível. |

---

## 6. Matriz de Rastreabilidade RF × RNF

| | RNF01 Anonimato | RNF02 Disponib. | RNF03 Triagem | RNF04 RAG | RNF05 Escalab. | RNF06 Legal/Ético | RNF07 Desemp. |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **RF01** Relatar situação | ●● | ● | — | — | — | ●● | ● |
| **RF02** Consultar psicoeducação | ● | ● | — | ●● | ● | ●● | ●● |
| **RF03** Triagem de risco | ● | ●● | ●● | — | — | ● | ●● |
| **RF04** Encaminhamento priorizado | ● | ●● | ●● | ● | ●● | ● | ●● |
| **RF05** Atualizar catálogo | — | ●● | ● | ●● | ●● | ● | — |

Legenda: ●● dependência forte · ● dependência moderada · — sem dependência direta

---

## 7. Justificativa da Ferramenta de Modelagem

**Ferramenta escolhida: draw.io / diagrams.net**

| Critério | Avaliação |
|---|---|
| **Licença** | Gratuita e de código aberto (Apache 2.0) — atende à exigência da disciplina. |
| **Formato de arquivo** | XML aberto (`.drawio`), versionável em Git e legível como texto — permite *diagram as code* sem abrir mão do editor visual. |
| **Portabilidade** | Executa no navegador sem instalação, em desktop (Electron) e integra ao VS Code; a equipe é distribuída e usa sistemas operacionais distintos. |
| **Cobertura de notação** | Bibliotecas UML completas (casos de uso, classes, sequência, componentes, implantação) e conjuntos de ícones AWS/Azure — cobre as cinco visões do 4+1 em uma única ferramenta. |
| **Múltiplas páginas** | Um único arquivo comporta as cinco visões em abas separadas, mantendo a coesão do modelo arquitetural. |
| **Curva de aprendizado** | Baixa; não exige sintaxe própria, ao contrário do PlantUML, o que reduz o custo de contribuição da equipe acadêmica (restrição R3). |

**Alternativas descartadas:**

- **PlantUML** — excelente para versionamento, mas o controle fino de layout é limitado, dificultando diagramas de implantação legíveis.
- **StarUML** — apenas *trial* gratuito; conflita com a restrição orçamentária (R1).
- **Modelio** — open source e rigoroso em UML, mas exige instalação desktop e tem curva de aprendizado mais acentuada.

---

## 8. Referências

- ISO/IEC 25010:2011 — *Systems and software Quality Requirements and Evaluation (SQuaRE)*
- KRUCHTEN, P. *Architectural Blueprints — The "4+1" View Model of Software Architecture*. IEEE Software, 1995.
- BRASIL. Lei nº 11.340/2006 (Maria da Penha); Lei nº 14.188/2021 (violência psicológica); Lei nº 13.709/2018 (LGPD).
- NIELSEN, J. *Response Times: The 3 Important Limits*. Nielsen Norman Group.
- Milvus/Zilliz — *Acceptable latency for a RAG system in an interactive setting*.
- Documentos internos: TAP v1, Matriz de Encaminhamento Aurora, Justificativa do Projeto, Backlog Aurora, "O Problema: A Crise Invisível da Violência Psicológica".
