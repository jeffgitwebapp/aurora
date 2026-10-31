# Plano de Implementação — Jornada do Usuário Aurora

**Status:** J-00 e J-01 concluídos como preparação documental/técnica; desenvolvimento de I-01, I-02, I-03, I-04 e C-01 concluído e publicado, aguardando validação do time de produto; desenvolvimento de C-02 concluído localmente com serviços em camadas e dados estáticos de protótipo, aguardando validação do time de produto/especialistas e publicação; revisões profissionais de segurança, privacidade e conteúdo ainda pendentes conforme indicado em cada tarefa; demais tarefas de implementação não iniciadas
**Documento-base:** [Jornada do Usuário](./jornada-do-usuario.md)
**Escopo:** protótipo funcional ponta a ponta, com frontend e backend integrados a serviços de produção que utilizam dados e provedores simulados nesta fase
**Regra de conclusão:** uma jornada só fica concluída após implementação, testes locais, commit, publicação e teste no ambiente AWS realizado por uma pessoa.

## 1. Objetivo e escopo

Este plano transforma as jornadas descritas em [Jornada do Usuário](./jornada-do-usuario.md) em tarefas ordenadas por prioridade e dependência. O objetivo é ter um protótipo navegável e funcional de ponta a ponta, preservando o comportamento e as referências visuais do wireframe, sem afirmar que mocks equivalem a serviços reais.

O plano inclui as ações independentes de segurança e acesso, a conversa anônima e seus percursos dependentes, além das jornadas opcionais registradas no documento-base: questionário, área logada, módulos, diário e guia/plano de segurança. Jornadas opcionais não devem bloquear o acesso anônimo nem as ações de emergência.

### Limites do protótipo

- Frontend e backend devem se comunicar por contratos explícitos. Serviços e componentes de produção podem operar temporariamente com dados estáticos para representar triagem, recuperação de conteúdo, guardrails, catálogo e persistência.
- Os componentes e serviços devem ser criados com os nomes e responsabilidades que manterão em produção; não criar classes ou serviços prefixados/sufixados com `Mock`. Durante o protótipo, as implementações podem usar fixtures, respostas e outros dados estáticos internamente. Quando os provedores reais forem integrados, substituir esses dados estáticos pela integração na mesma classe/serviço, preservando seu contrato e sua responsabilidade sempre que possível. Portas/interfaces podem separar contratos de implementações. As portas de serviços que podem acessar provedores externos devem ser assíncronas. Handlers orquestram portas e casos de uso, sem conter regras de classificação, fixtures ou lógica de provedores; routers validam transporte e convertem contratos HTTP; a composição de dependências acontece na inicialização da aplicação.
- O fluxo da conversa chama o serviço de triagem antes do serviço de resposta. Resultado agudo devolve sinais e orientação do serviço e interrompe a geração; resultado indeterminado devolve a orientação de incerteza e também não gera resposta; somente o resultado explícito sem sinal agudo segue para o serviço de chat/LLM. Quando as integrações reais forem habilitadas, os dados/provedores temporários serão substituídos dentro dos mesmos serviços, preservando a regra de orquestração do handler.
- Dados e respostas simulados devem ser identificados como comportamento de protótipo; não usar respostas fictícias para afirmar que uma situação é segura, que uma fonte foi verificada ou que um serviço está disponível.
- Não integrar provedores reais de LLM/RAG, bases vetoriais, autenticação externa, banco de dados ou serviços da rede nesta etapa. Deixar fronteiras substituíveis e contratos documentados para integrações futuras.
- Não armazenar relatos anônimos em banco, logs, telemetria, `localStorage` ou `sessionStorage`. O protótipo deve manter a sessão anônima apenas em memória da aplicação e descartá-la ao encerrar a sessão.
- Não alegar que a Saída Rápida apaga o histórico do navegador, do sistema operacional, da rede ou de terceiros.
- O wireframe é a referência visual. O documento de jornada e as fontes rastreadas nele são a referência de comportamento. Não transformar lacunas ou sugestões não validadas em requisitos silenciosamente.
- Aprovação de conteúdo de risco, saúde, direitos, privacidade e rede de serviços continua sendo responsabilidade de pessoas especialistas.

## 2. Estado e acompanhamento

Use estes estados em cada tarefa:

- **Não iniciada** — ainda não começou.
- **Em andamento** — implementação ativa.
- **Bloqueada** — falta decisão, conteúdo aprovado ou dependência; registrar o motivo.
- **Implementada localmente** — código e testes locais concluídos, mas ainda faltam commit, publicação e teste humano na AWS.
- **Desenvolvimento concluído localmente** — implementação e testes locais finalizados; aguardam validação do time de produto/especialistas e/ou publicação.
- **Concluída** — todos os critérios da seção 3 foram cumpridos e as evidências foram registradas.

Atualize o estado, os critérios e as evidências deste arquivo durante cada implementação. Não marque uma jornada como concluída apenas porque a interface foi codificada ou porque os testes locais passaram.

## 3. Critério de conclusão de cada jornada

Para cada tarefa de jornada, marcar cada etapa somente quando houver evidência:

- [ ] Frontend e backend do escopo foram implementados e integrados; quando aplicável, os mocks e seus limites estão visíveis e documentados.
- [ ] Testes automatizados relevantes passaram.
- [ ] Fluxo foi executado localmente, incluindo estados alternativos e erros previstos.
- [ ] Comportamento e apresentação foram conferidos contra a jornada e o wireframe.
- [ ] Alterações foram commitadas; registrar o hash do commit.
- [ ] Versão foi publicada/deployada; registrar a versão ou referência da publicação.
- [ ] Uma pessoa testou o fluxo no ambiente AWS e registrou data, resultado e eventuais problemas.

**O teste na AWS é uma etapa humana obrigatória.** O assistente não deve declarar uma jornada concluída sem a confirmação e evidência dessa validação humana.

## 4. Skills necessárias

As especificações estão no [índice de skills](../../skills/lista_skills.md). Os links abaixo apontam para as competências a serem consultadas em cada tarefa.

**Verificação de cobertura:** não foi identificada ausência de skill para este plano. A composição de contratos e mocks é coberta por Arquitetura de software e integração ponta a ponta, Backend Python/FastAPI, Frontend React/TypeScript e Engenharia de qualidade/testes. Não foi criada uma skill nova. Se uma implementação revelar uma lacuna real, adicionar a competência ao índice e criar sua especificação individual antes de usá-la como referência recorrente.

## 5. Ordem de implementação

As tarefas de preparação não substituem a priorização das jornadas: são a base técnica e as decisões necessárias. Entre as jornadas, implementar primeiro as ações independentes de segurança e emergência; depois as entradas independentes de informação; então avançar pelas dependências da conversa. As jornadas opcionais ficam depois da jornada anônima principal.

| Ordem | ID | Jornada/tarefa | Tipo | Dependências | Status |
|---:|---|---|---|---|---|
| 0 | J-00 | Resolver decisões e lacunas que bloqueiam comportamento seguro | Preparação funcional | Jornada-base e fontes relacionadas | Resolvido — decisões e lacunas registradas |
| 0 | J-01 | Definir contratos e estrutura dos mocks ponta a ponta | Preparação técnica | J-00 para contratos de comportamento | Resolvido — contratos e estrutura de mocks definidos |
| 1 | I-01 | Acesso a emergência por telefone | Independente, P0 | J-01 | Desenvolvimento concluído — implementação publicada; falta validação do time de produto |
| 2 | I-02 | Saída Rápida e descarte da sessão | Independente, P0 | J-00, J-01 | Desenvolvimento concluído — implementação funcional no protótipo, publicada; falta validação do time de produto |
| 3 | I-03 | Início anônimo e sugestões | Independente, P1 | J-01 | Desenvolvimento concluído — implementação funcional no protótipo, publicada; falta validação do time de produto |
| 4 | I-04 | Privacidade e contatos úteis | Independente, P1 | J-00, I-03 | Desenvolvimento concluído — implementação funcional no protótipo, publicada; falta validação do time de produto |
| 5 | C-01 | Conversa anônima, mensagens e contexto em memória | Início da jornada dependente | I-03, J-01 | Desenvolvimento concluído — conversa integrada ao mock funcional e publicada; falta validação do time de produto |
| 6 | C-02 | Triagem de risco agudo antes de resposta informativa | Dependente da mensagem | C-01, J-00 | Desenvolvimento concluído localmente — `TriageService` separado do handler, com dados estáticos substituíveis; falta validação do time de produto/especialistas e publicação |
| 7 | C-03 | Tela de risco agudo, canais e retorno | Dependente da triagem | I-01, I-02, C-02 | Pendente |
| 8 | C-04 | Resposta informativa com fontes simuladas | Dependente da triagem sem risco agudo | C-02, J-00 | Pendente |
| 9 | C-05 | Limite de escopo e alternativas seguras | Ramo dependente da conversa | C-02, J-00 | Pendente |
| 10 | C-06 | Localização opcional e encaminhamento simulado | Ramo dependente da conversa | C-04, J-00 | Pendente |
| 11 | I-05 | Entrada independente para questionário e resultado simulado | Independente, opcional | C-02, C-06, decisões de conteúdo | Pendente |
| 12 | L-01 | Cadastro, login e saída da área logada (mock) | Jornada futura opcional | J-00, J-01, jornada anônima estável | Pendente |
| 13 | L-02 | Migração, histórico e exclusão de conta (mock) | Dependente de conta e sessão | C-01, L-01 | Pendente |
| 14 | L-03 | Módulos de psicoeducação (mock) | Jornada futura opcional | L-01, decisões de conteúdo | Pendente |
| 15 | L-04 | Diário de incidentes e exportação demonstrativa | Jornada futura opcional | L-01, J-00 | Pendente |
| 16 | L-05 | Guia/plano de segurança demonstrativo | Jornada futura opcional | J-00; L-01 se a decisão aprovada exigir conta | Pendente |

**Legenda de status:** “Desenvolvimento concluído” indica implementação publicada, com validação do time de produto pendente para I-01, I-02, I-03, I-04 e C-01. “Desenvolvimento concluído localmente” indica implementação e testes locais finalizados, mas sem validação do time de produto/especialistas e publicação; aplica-se atualmente a C-02. O protótipo deve manter componentes e serviços com nomes/responsabilidades de produção; respostas e fixtures estáticas identificam somente a implementação temporária, não a classe/serviço nem a arquitetura final. “Pendente” indica tarefa ainda não concluída e não necessariamente iniciada.

O questionário é uma entrada independente para a usuária, mas sua implementação depende da triagem e do encaminhamento para reutilizar regras e contratos. As tarefas L-01 a L-05 são de protótipo; não implementam segurança, persistência ou proteção de dados adequadas para uso real.

## 6. Tarefas de preparação

### J-00 — Resolver decisões e lacunas que bloqueiam comportamento seguro

**Estado:** Concluída — decisões e pendências documentadas; tarefas dependentes bloqueadas conforme necessário
**Tipo:** preparação funcional e validação humana
**Objetivo:** registrar decisões de produto e de domínio necessárias para que o protótipo não invente regras sensíveis.

**Decisões e encaminhamentos registrados em 31/10/2026:**

| Decisão | Resultado atual | Estado / responsável pela próxima validação |
|---|---|---|
| Jornada-base | A usuária já aprovou a jornada em revisão anterior. Textos e fluxos sensíveis continuam sujeitos a revisão profissional. | Aprovada pela usuária; profissionais de saúde mental, direito, proteção e acessibilidade devem revisar o conteúdo antes de uso real |
| Saída Rápida | Decisão revisada pela usuária em 31/10/2026: abrir a página local `/receitas` com uma receita escolhida aleatoriamente entre pudim, pão de forno e frango assado; cada novo acionamento apresenta uma receita diferente da última exibida. A tecla Esc troca imediatamente para ela, sem confirmação, em qualquer tela, inclusive com foco em campo. Conteúdo e imagens locais devem estar pré-carregados desde a abertura do site. | Escopo da tela aprovado pela usuária; textos e imagens do protótipo foram produzidos para esta implementação; revisão de segurança será feita pela usuária após os ajustes e antes da publicação/teste AWS |
| Privacidade da sessão | Texto aprovado para o protótipo: “Esta conversa fica na memória enquanto esta página está aberta. Ao usar a Saída Rápida ou encerrar a página, o Aurora descarta o conteúdo da sessão que mantém. Isso não apaga possíveis registros do navegador, dispositivo, rede ou terceiros.” | Aprovado pela usuária; profissional de privacidade/LGPD deve revisar a redação antes de uso real |
| Triagem de risco agudo | Sinais documentados: ideação suicida, agressão em curso, ameaça de morte e presença de arma. Sinal agudo interrompe o fluxo informativo antes de qualquer geração por LLM. Na classificação indeterminada, não afirmar ausência de risco; mostrar estado de incerteza e canais gerais, sem resposta informativa até escolha explícita da usuária. Destacar canais conforme E5-US1/2: 190 para morte iminente/agressão em curso; 192 quando houver lesão ou risco de ato iminente; 188 para crise emocional/ideação; 180 permanece disponível como canal de orientação. | Política de produto registrada; profissionais da rede de proteção e saúde mental devem aprovar critérios, mapeamento e mensagem antes de uso real |
| Limite de escopo | Aplicar o texto do wireframe a pedidos de diagnóstico/prescrição ou parecer jurídico individual; perguntas gerais sobre direitos permanecem no fluxo informativo. | Decisão de produto registrada; profissionais de direito e saúde mental devem revisar exemplos limítrofes |
| Fontes e mocks de conteúdo | Usar somente fontes reais identificáveis e aprovadas. Mocks devem estar rotulados como demonstração; não inventar citações nem afirmações factuais. Conteúdo sensível não aprovado não deve ser exibido como resposta real. | Política registrada; curadoria/produto e especialistas do domínio devem aprovar cada fixture |
| Localização e catálogo | A solicitação da usuária para obter localização do dispositivo e confirmá-la em modal conflita com RF/RNF e wireframe, que preveem município/UF informado voluntariamente, sem geolocalização nem pedido de permissão. Até uma decisão formal, prevalece a especificação vigente: campo manual opcional, sem geolocalização. | Solicitação de mudança bloqueada para revisão de produto; privacidade/segurança devem avaliar qualquer proposta de alteração. Fallback de cidade vazia/ambígua continua pendente de produto |
| Frescor do catálogo | Regras existentes: meta de ≥95% dos registros ativos verificados nos últimos 90 dias; serviços de emergência 100% revistos nos últimos 30 dias; registros com mais de 180 dias sem verificação não podem aparecer como sugestão prioritária e só podem aparecer com aviso explícito. | Definido pelas métricas CA-05; responsável pelo catálogo/rede de serviços deve verificar os contatos |
| Jornadas futuras | Especificar campos, validações e estados ao iniciar cada tarefa correspondente; manter cada fluxo bloqueado até decisões de produto e revisão de domínio aplicáveis. | Decisão de processo registrada; responsável de produto e especialistas relevantes em cada tarefa L-01 a L-05 e I-05 |

**Critério de aceite:** concluído como preparação documental após confirmação final da usuária; decisões, estados, responsáveis por validação e dependências estão registrados. Pendências especializadas não foram declaradas como aprovadas. Não solicitar geolocalização nem implementar o modal de localização até que a política seja revista, aprovada e os requisitos pertinentes sejam atualizados. Tarefas dependentes dessas pendências permanecem **Bloqueadas** ou usam somente mocks claramente identificados, sem alegar que o comportamento é validado.

**Impacto nas dependências:**

| Tarefa dependente | Estado após J-00 | Motivo |
|---|---|---|
| I-02 — Saída Rápida | Desenvolvimento concluído e publicado; falta validação do time de produto; revisão de segurança ainda pendente | A definição funcional de `/receitas` inclui três opções de receita, mostrando uma por acionamento e sem repetir a última. A revisão de segurança continua registrada como pendência antes de considerar o fluxo aprovado para uso real |
| C-02/C-03 — Triagem e risco agudo | C-02 tem mock local; uso real bloqueado até revisão da rede de proteção e saúde mental; C-03 não iniciada | Fixtures sintéticas exercitam os estados; critérios de risco, destaque dos canais e texto de incerteza exigem validação especializada |
| C-04 — Resposta com fontes | Bloqueada para conteúdo real até curadoria/aprovação de fontes e fixtures | Não há autorização para inventar fontes ou afirmações sensíveis |
| C-05 — Limite de escopo | Bloqueada para casos limítrofes até revisão jurídica e clínica | A distinção geral foi definida; exemplos e gatilhos ainda precisam de revisão |
| C-06 — Localização/encaminhamento | Bloqueada até decisão de produto sobre localização e fallback | A proposta de geolocalização está em revisão; permanece vigente a entrada manual opcional |
| I-03/I-04 — Início e privacidade | Podem avançar com o texto registrado, sujeitos à revisão de privacidade antes de uso real | Aviso aprovado para o protótipo, mas revisão LGPD continua pendente |
| I-01 — Telefones de emergência | Pode avançar com destinos e números documentados; verificar os contatos antes de publicação | O protótipo não valida disponibilidade ou atendimento real |
| I-05/L-01 a L-05 — Jornadas futuras | Aguardam detalhamento ao iniciar cada tarefa | Perguntas, campos, validações e estados ainda não foram aprovados |

**Skills:** [Análise de requisitos, backlog e rastreabilidade](../../skills/analise-requisitos-backlog-rastreabilidade.md), [Jornada do usuário e especificação de usabilidade](../../skills/jornada-usuario.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md).

### J-01 — Definir contratos e estrutura dos mocks ponta a ponta

**Estado:** Concluída — contratos técnicos aprovados pela usuária; implementações de domínio continuam nas tarefas próprias
**Tipo:** preparação técnica; não é uma jornada de tela
**Objetivo:** permitir que cada fluxo use mocks substituíveis e tenha comportamento consistente entre frontend e backend.

**Escopo:** documentar contratos tipados e erros para conversa, resultado de triagem, resposta com fontes, guardrail e catálogo/encaminhamento. Contratos de conta e persistência ficam adiados para L-01/L-02. Definir adaptadores/mock services e fixtures sintéticas; manter regras de domínio separadas das chamadas HTTP e das dependências futuras. A especificação aprovada está em [Contratos de Integração e Padrão de Mocks](./contratos-integracao-mocks.md).

**Critérios de aceite:**

- Contrato HTTP atual e sua evolução coordenada para o fluxo conversacional estão documentados; a usuária aprovou não manter compatibilidade externa nem rota legada paralela.
- Contratos internos de triagem, fontes, guardrail e catálogo têm tipos, resultados alternativos e limites definidos; contratos de conta/persistência não são antecipados.
- Política dos mocks proíbe chamadas externas, armazenamento de relatos anônimos e logs com texto livre; fixtures são sintéticas ou fontes reais aprovadas, identificadas como demonstração.
- Erros de validação, indisponibilidade, timeout e resposta fora de schema estão documentados; os futuros clientes frontend devem validar runtime e não converter falha em sucesso.
- Está documentado quais propriedades exigem evidência fora de mocks (recall clínico, qualidade real de RAG, frescor de serviços e segurança de armazenamento real).
- Contratos não introduzem telas ou controles; o wireframe continua sendo a referência visual.
- As escolhas de compatibilidade do endpoint, envio de histórico e formato de erros foram confirmadas pela usuária em 31/10/2026 e estão registradas na especificação.
- A estrutura dos mocks não cria pastas vazias nem implementa serviços futuros; cada adaptador será criado na tarefa que o consumir.

**Skills:** [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md).

**Validações registradas em 31/10/2026:**

- [x] Proposta técnica revisada e aprovada pela usuária.
- [x] Backend: `src/backend/.venv/Scripts/python.exe -m pytest` — 10 testes passaram; uma advertência de depreciação do `starlette.testclient`/`httpx` já existente.
- [x] Frontend: `npm run check` em `src/frontend` — verificação TypeScript passou.
- [x] Links Markdown do contrato e do plano verificados; sem links locais quebrados ou whitespace residual.
- [x] `git diff --check` passou.

Essas verificações validam os contratos documentados e o contrato atual do scaffold; não implementam nem certificam os adaptadores futuros, RAG, triagem real, guardrails, catálogo, privacidade em produção ou as métricas CA-01 a CA-05.

## 7. Ações independentes — segurança e entrada

### I-01 — Acesso a emergência por telefone

**Prioridade:** P0
**Estado:** Concluída
**Dependências:** J-01
**Jornada-base:** ações independentes; início, conversa e telas de risco agudo.

**Escopo:** garantir acesso visível e acionável aos canais descritos na jornada: Polícia Militar 190, Central de Atendimento à Mulher 180, SAMU 192 e CVV 188. O controle inicia a ação de ligação do aparelho; o Aurora não liga nem envia dados por conta própria.

**Critérios de aceite:** destinos `tel:` correspondem aos números; controles são utilizáveis por teclado/leitor de tela; contatos aparecem nas superfícies previstas; nenhuma etapa exige cadastro ou envio de relato.

**Skills:** [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

**Implementação e evidências locais (31/10/2026):**

- Criado `EmergencyContacts`, componente compartilhado com links `tel:190`, `tel:180`, `tel:192` e `tel:188` e nomes acessíveis que identificam o serviço e o número.
- Os quatro canais estão visíveis na tela inicial e no painel “Contatos úteis” da conversa; o link “Emergência” do cabeçalho continua apontando para `tel:190`.
- Os links são âncoras nativas, utilizáveis por teclado; a lista compacta na tela inicial mantém alvos de toque de pelo menos 44 px e se adapta ao breakpoint móvel.
- Validação: `npm run check`, `npm run build` e `git diff --check` passaram. Inspeção no navegador local confirmou os quatro rótulos e destinos `tel:` tanto no início quanto na conversa.
- Verificação adicional do fluxo local: o HTTP 500 observado ao abrir uma conversa por sugestão ocorreu porque o backend não estava em execução. Com frontend e backend ativos, a sugestão abriu a conversa e recebeu resposta normalmente.
- Conclusão confirmada pelo usuário em 31/10/2026: publicação realizada e teste humano validado no ambiente AWS.
- Commit da implementação: `687249b` (`resoluação I-01`), presente em `develop` e `origin/develop`.

### I-02 — Saída Rápida e descarte da sessão

**Prioridade:** P0
**Estado:** Desenvolvimento concluído — implementada, testada localmente, commitada e publicada; falta validação do time de produto
**Dependências:** J-00 (destino e regra Esc aprovados), J-01
**Jornada-base:** saída disponível sem depender de relato, triagem ou cadastro.

**Escopo:** implementar o acionamento visível e por Esc nas telas previstas; descartar estado volátil sob controle do Aurora e abrir o destino neutro aprovado. Não condicionar a saída à rede ou a uma chamada ao backend.

**Critérios de aceite:** funciona em cada tela e nos estados de envio; comportamento com foco em campo segue decisão aprovada; o fluxo não afirma apagar rastros externos; testes locais medem o comportamento do cliente e verificam o descarte da sessão. Registrar as metas de latência documentadas e indicar explicitamente que mock/local não equivale a medição de produção.

**Skills:** [PWA, privacidade de dispositivo e Saída Rápida](../../skills/pwa-privacidade-dispositivo-saida-rapida.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

**Implementação e evidências locais (31/10/2026):**

- Conforme decisão da usuária após o registro inicial de J-00, **Sair**, **Saída rápida (Esc)** e a tecla Esc substituem a rota atual por `/receitas`, exibindo uma única receita sorteada dentre as três disponíveis, sempre diferente da última apresentada. A ação limpa as mensagens iniciais mantidas no estado do app. A troca usa navegação interna, não aguarda a API nem faz uma chamada de rede.
- A página não mostra a marca Aurora nem um caminho para retornar ao relato. Título do documento: **Receitas**.
- Criadas três receitas com texto e ilustrações SVG originais locais: **Pudim de leite**, **Pão de forno** e **Frango assado**. Em cada pedido de Saída Rápida aparece apenas uma receita, sorteada sem repetir a última exibida. O conteúdo é demonstrativo e deve ser revisado pela usuária; nenhuma imagem ou serviço externo é requisitado.
- Texto das receitas está no bundle inicial; as três imagens têm `rel=preload` no HTML e são carregadas antecipadamente.
- A usuária informou que fará a revisão de segurança após estes ajustes. Até essa revisão, a página não deve ser publicada nem considerada adequada para uso real.
- Validação no navegador: Esc durante um envio pendente trocou para `/receitas` em 36 ms, cancelou a requisição no cliente e removeu o chat da tela; as três receitas e imagens estavam disponíveis.
- Validação do ajuste de seleção: em 10 acionamentos consecutivos de Esc no navegador, a página exibiu exatamente uma receita por vez e nenhuma receita repetiu a imediatamente anterior.
- A publicação de I-02 foi confirmada em 31/10/2026; falta validação do time de produto.
- Pré-carregamento verificado antes da saída para `/receitas`; em viewport de 320 px a página não apresentou overflow horizontal.
- Latência local de Escape medida em 30 execuções a partir do início: p95 47 ms, p99 48 ms, máximo 48 ms. Esta amostra local não certifica as metas em produção nem substitui medição AWS.
- `npm run check`, `npm run build` e `git diff --check` passaram.
- A revisão de segurança e a revisão do texto e das ilustrações permanecem pendentes; a conclusão de implementação/publicação não substitui essas revisões para uso real.

### I-03 — Início anônimo e sugestões

**Prioridade:** P1
**Estado:** Desenvolvimento concluído — implementada, testada localmente, commitada e publicada; falta validação do time de produto
**Dependências:** J-01
**Jornada-base:** tela inicial; texto livre e sugestões são entradas independentes.

**Escopo:** ajustar a tela inicial ao wireframe, preservando o envio do primeiro texto sem uma segunda ação e o início por uma das três sugestões documentadas. Campo vazio ou só com espaços não inicia a conversa. Não solicitar localização, permissão, pop-up ou notificação nesta entrada.

**Critérios de aceite:** rótulos, mensagens e ações rastreáveis ao wireframe/jornada; aviso de sessão aprovado em J-00; submissão com teclado e tecnologias assistivas; apresentação responsiva conforme referência visual.

**Skills:** [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

**Implementação e evidências locais (31/10/2026):**

- O envio do campo inicial usa o rótulo acessível **Enviar**, não inicia com texto vazio e envia o conteúdo digitado uma vez; as três sugestões continuam como entradas independentes.
- O aviso inicial informa que a conversa fica na memória enquanto a página está aberta; a interface não pede cadastro, localização, permissões nem notificações.
- Testes no navegador: envio por texto livre iniciou a conversa com uma única mensagem da usuária; em viewport de 320 px não houve overflow horizontal.
- `npm run check` e `npm run build` passaram.
- A publicação de I-03 foi confirmada em 31/10/2026; falta validação do time de produto.
- O aviso e a implementação ainda requerem revisão profissional de privacidade antes de uso real.

### I-04 — Privacidade e contatos úteis

**Prioridade:** P1
**Estado:** Desenvolvimento concluído — implementada, testada localmente, commitada e publicada; falta validação do time de produto
**Dependências:** J-00 (texto e destino aprovados), I-03, I-01
**Jornada-base:** links independentes na tela inicial.

**Escopo:** dar destino funcional aos controles **Privacidade** e **Contatos úteis**. A tela/área de contatos oferece os canais gerais e a ação telefônica; a explicação de privacidade descreve a sessão do protótipo e seus limites com precisão.

**Critérios de aceite:** nenhum link fica sem ação; textos aprovados não prometem eliminar rastros controlados pelo navegador/dispositivo; contatos mantêm acesso direto por telefone; retorno à tela anterior funciona sem perder uma sessão ainda ativa.

**Skills:** [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

**Implementação e evidências locais (31/10/2026):**

- **Privacidade** expande uma área acessível na própria tela e apresenta o texto aprovado em J-00, sem prometer apagar registros externos; **Fechar** retorna ao início.
- **Contatos úteis** leva ao painel com os quatro canais acionáveis; os links continuam usando `tel:` e o painel está acessível também na conversa.
- Testado no navegador: expansão/fechamento do aviso de privacidade, foco restaurado, navegação por âncora ao painel de contatos e ausência de overflow horizontal em 320 px.
- `npm run check`, `npm run build` e `git diff --check` passaram.
- A publicação de I-04 foi confirmada em 31/10/2026; falta validação do time de produto.
- Revisão profissional de privacidade/acessibilidade permanece pendente para uso real.

## 8. Jornada anônima dependente

### C-01 — Conversa anônima, mensagens e contexto em memória

**Prioridade:** P1
**Estado:** Desenvolvimento concluído — implementada, testada localmente, commitada e publicada; falta validação do time de produto
**Dependências:** I-03, J-01
**Jornada-base:** envio do primeiro relato, mensagens subsequentes e retorno durante a sessão.

**Escopo:** integrar o chat existente ao endpoint/mock de conversa; renderizar mensagens, estado de processamento, falhas e reenvio conforme decisões aprovadas; preservar contexto enquanto a sessão estiver ativa. Usar os textos e controles indicados na jornada/wireframe.

**Critérios de aceite:** o texto inicial é enviado uma vez; mensagens anteriores permanecem no estado de memória do frontend e somente a mensagem atual é enviada ao backend, sem promessa de contexto para geração; falhas não parecem sucesso e permitem recuperação clara; atualização/reabertura não transforma relato anônimo em histórico persistente; nenhuma mensagem vai para logs.

**Skills:** [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

**Implementação e evidências locais (31/10/2026):**

- O primeiro texto (livre ou sugestão) é enviado uma vez; mensagens seguintes acrescentam apenas o texto atual ao payload da API. O histórico fica em memória no frontend.
- Durante a espera a interface exibe **Lendo com atenção…** e desativa o campo; no backend, a resposta simulada aguarda cinco segundos.
- Falhas são apresentadas como erro e oferecem **Tentar novamente** sem duplicar a mensagem da usuária. Uma falha seguida de resposta simulada foi exercitada no navegador.
- Após recarregar a rota `/conversa`, o histórico não reaparece; localStorage e sessionStorage permaneceram vazios. O endpoint não registra o conteúdo da mensagem.
- Validação local: integração navegador→Vite→FastAPI retornou HTTP 200 em 5,1 s; segundo envio preservou as duas mensagens da usuária e respectivas respostas; 10 testes do backend passaram; Ruff, `npm run check`, `npm run build` e `git diff --check` passaram.
- A publicação de C-01 foi confirmada em 31/10/2026; falta validação do time de produto.
- A validação profissional de privacidade antes de uso real permanece pendente.

### C-02 — Triagem de risco agudo antes de resposta informativa

**Prioridade:** P0 de segurança
**Estado:** Desenvolvimento concluído localmente — serviços de triagem e resposta com dados estáticos e orquestração por portas implementados e testados; falta validação do time de produto/especialistas e publicação
**Dependências:** C-01, J-00
**Jornada-base:** toda mensagem deve passar pela regra de urgência antes do fluxo informativo.

**Escopo:** o handler de envio orquestra `TriageService` antes de `ChatResponseService`. A porta de triagem devolve status, sinais identificados e orientação de fluxo; se o resultado for agudo, interrompe o fluxo informativo; se for indeterminado, devolve orientação de incerteza e também interrompe; somente a fixture explicitamente classificada como sem sinal agudo segue ao serviço de resposta. Os serviços têm nomes e responsabilidades que serão mantidos em produção; atualmente suas implementações usam fixtures e respostas estáticas para o protótipo. Quando provedores reais forem integrados, substituir esses dados internos pela lógica/conexão real, mantendo os contratos públicos e a orquestração. Regras de domínio ficam no serviço de triagem, resposta conversacional no serviço de resposta, e nenhum dos dois detalhes fica no router ou no handler. A implementação não conecta um LLM real nem afirma detectar risco real.

**Fixtures de teste aprovadas pela usuária para o mock em 31/10/2026 — validação do time de produto e especialistas ainda pendente:**

| Sinal simulado | Frases de teste que acionam o mock |
|---|---|
| Ideação suicida | “Estou pensando em me matar”; “Quero tirar minha vida” |
| Agressão em curso | “Ele está me agredindo agora”; “Estou sendo atacada neste momento” |
| Ameaça de morte | “Ele disse que vai me matar”; “Recebi uma ameaça de morte” |
| Presença de arma | “Ele está com uma arma aqui”; “Há uma arma no local agora” |
| Fixture sem sinal agudo | “Quero informações sobre serviços de apoio na minha cidade” |

Atualmente, `TriageService` compara a mensagem após normalizar caixa, acentos, espaços e pontuação final com as frases completas dos fixtures estáticos; em mensagens com várias sentenças, cada segmento precisa corresponder integralmente a uma frase de risco ou ao controle definido. Não há correspondência por palavra isolada ou substring, nem uso de LLM. Uma ou mais frases de risco correspondentes resultam em **risco agudo**, registrando todos os sinais e devolvendo orientação sintética pelo resultado do serviço, sem invocar `ChatResponseService`. A fixture de controle, quando enviada sozinha, resulta em **sem sinal agudo detectado** e permite que o handler invoque o serviço de resposta. Mensagens não contempladas, ambíguas, negadas, hipotéticas ou misturadas com texto não reconhecido retornam **indeterminado**, com orientação de incerteza, sem invocar o serviço de resposta; ausência de correspondência nunca deve ser interpretada como confirmação de segurança. A priorização final de canais é responsabilidade do fluxo C-03 e requer validação especializada.

Estas frases servem exclusivamente para demonstrar estados e testar a integração do protótipo. Mesmo com correspondência exata, fixtures não constituem triagem confiável de mensagens reais, não reconhecem variações/contexto e não satisfazem critérios clínicos ou de segurança. O frontend identifica os resultados como simulação; não usar o mock para orientar situações reais nem declarar que detecta risco.

**Critérios de aceite:** contrato distingue risco agudo, fixture de controle sem sinal agudo e resultado indeterminado; falhas de transporte/servidor permanecem erros explícitos sem resposta informativa. O handler depende de portas de serviço, sem implementar classificação, fixtures ou geração de resposta. `TriageService` retorna status, sinais e orientação; `ChatResponseService` só é chamado após o status de controle sem sinal agudo. Risco agudo impede a resposta informativa e retorna os sinais reconhecidos para integração com C-03. O cliente mostra a orientação devolvida pelo serviço, identificada como simulação, e mantém os contatos úteis acessíveis; a tela completa e o mapeamento de canais pertencem a C-03. Testes cobrem cada fixture, múltiplos sinais, negações/contexto, fixture de controle, mensagens indeterminadas e não invocação do serviço de chat para casos agudos/indeterminados. Não declarar o CA-02 atendido com dados estáticos de protótipo: recall de 100% exige suíte e validação de domínio apropriadas antes de uso real.

**Implementação e evidências locais (31/10/2026):**

- `TriageService` aplica fixtures e dados estáticos no protótipo, produzindo `TriageResult` com status, sinais e orientação; `ChatResponseService` fornece a resposta demonstrativa. Esses são os serviços do produto, sem classes paralelas prefixadas com `Mock`; suas implementações serão conectadas a provedores/dados reais no momento oportuno.
- Portas assíncronas `TriageEvaluator` e `ChatResponseGenerator` definem os contratos consumidos pelo handler. A composição injeta ambos serviços na feature. Handler valida entrada, chama primeiro a triagem e só invoca o serviço de resposta para o status da fixture de controle; o router traduz o resultado para o contrato HTTP (`triage_status`, `signals`, `guidance`, `reply`).
- Casos agudos e indeterminados não recebem resposta informativa nem aguardam o atraso simulado de cinco segundos. Somente a fixture explícita de controle recebe o texto demonstrativo após o atraso.
- Frontend exibe a orientação devolvida pela triagem, rotulada como simulação, e mantém visíveis os contatos úteis; não implementa nem duplica regras de classificação.
- Testes cobrem os oito exemplos de risco, normalização de caixa/acentos/espaços/pontuação, mensagens negadas ou com contexto extra, dois sinais reconhecidos, fixture de controle, payloads e atraso.
- Revisão do time de produto/especialistas, publicação e validação em ambiente publicado permanecem pendentes. C-03 ainda deve implementar a tela e o mapeamento de encaminhamento; o mock não pode ser usado para situações reais.

**Skills:** [Triagem determinística de risco agudo e avaliação de segurança](../../skills/triagem-risco-agudo-avaliacao-seguranca.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md).

### C-03 — Tela de risco agudo, canais e retorno

**Prioridade:** P0 de segurança
**Estado:** Não iniciada
**Dependências:** I-01, I-02, C-02
**Jornada-base:** resultado de risco agudo.

**Escopo:** apresentar os textos e canais aprovados do wireframe; oferecer ligações apenas após ação explícita da usuária; implementar **Voltar à conversa** preservando a sessão ainda aberta e manter Saída Rápida acessível.

**Critérios de aceite:** resultado de risco agudo aparece antes de conteúdo informativo; falha de qualquer serviço externo simulado não oculta os números; links de telefone não iniciam automaticamente; retorno não duplica nem perde o relato.

**Skills:** [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Triagem determinística de risco agudo e avaliação de segurança](../../skills/triagem-risco-agudo-avaliacao-seguranca.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [PWA, privacidade de dispositivo e Saída Rápida](../../skills/pwa-privacidade-dispositivo-saida-rapida.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### C-04 — Resposta informativa com fontes simuladas

**Prioridade:** P1
**Estado:** Não iniciada
**Dependências:** C-02 (resultado sem risco agudo), J-00 (fontes aprovadas), J-01
**Jornada-base:** resposta psicoeducativa, fontes e continuação da conversa.

**Escopo:** representar recuperação de trechos e geração por adaptadores mockados, com resposta estruturada e fontes demonstrativas aprovadas. O estado sem fonte relevante declara a limitação; não usar placeholders como citações reais nem mostrar resposta sem fundamentação como informação verificada.

**Critérios de aceite:** resposta inclui fontes identificáveis como fixture de protótipo; estado sem resultado e falha do mock são distintos; LLM/RAG não decide risco nem encaminhamento; consulta posterior mantém contexto sem persistir a sessão anônima; limites do protótipo aparecem onde a pessoa possa confundir simulação com serviço real.

**Skills:** [Curadoria de conteúdo e engenharia de conhecimento RAG](../../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [Integração de LLM e engenharia de prompts](../../skills/integracao-llm-engenharia-prompts.md), [Guardrails, escopo ético e avaliação generativa](../../skills/guardrails-escopo-etico-avaliacao-generativa.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md).

### C-05 — Limite de escopo e alternativas seguras

**Prioridade:** P1
**Estado:** Não iniciada
**Dependências:** C-02, J-00 (regra e conteúdo aprovados)
**Jornada-base:** pedidos de diagnóstico ou parecer individualizado.

**Escopo:** apresentar o bloco **Fora do que eu posso fazer** nos casos aprovados, sem encerrar a conversa; permitir seguir para informação geral ou encaminhamento. Casos limítrofes não devem ser inventados como regra do mock.

**Critérios de aceite:** mensagem e alternativas correspondem ao texto aprovado; pedidos gerais sobre direitos continuam no fluxo informativo; nenhuma resposta simula diagnóstico, aconselhamento jurídico individual ou decisão pela usuária; testes cobrem limites e continuidade.

**Skills:** [Guardrails, escopo ético e avaliação generativa](../../skills/guardrails-escopo-etico-avaliacao-generativa.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### C-06 — Localização opcional e encaminhamento simulado

**Prioridade:** P1
**Estado:** Não iniciada
**Dependências:** C-04, J-00 (política de localização e fallback aprovados), I-01
**Jornada-base:** informar Cidade/UF e ver até três opções priorizadas.

**Escopo:** aceitar município/UF informado voluntariamente; consultar catálogo mockado; apresentar cartões no formato do wireframe e retorno à conversa. Não solicitar geolocalização precisa, não encaminhar o relato e não apresentar fixture como contato real/verificado.

**Bloqueio atual:** a usuária solicitou revisar a obtenção automática da localização do dispositivo e sua confirmação por modal. Esse comportamento não está aprovado e conflita com a especificação vigente de localização manual opcional. Não solicitar permissão nem obter coordenadas até a decisão de produto e a revisão de privacidade/segurança; enquanto isso, C-06 não pode ser implementada.

**Critérios de aceite:** localização pode ser omitida sem bloquear canais gerais; resultados simulados mostram indicação de protótipo; lista tem no máximo três itens e segue a ordem definida pelo requisito/matriz aprovada; cidade sem resultado, ambígua, indisponibilidade e contato desatualizado têm estados definidos; retorno preserva conversa em memória.

**Skills:** [Catálogo de serviços e motor de encaminhamento](../../skills/catalogo-servicos-motor-encaminhamento.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### I-05 — Entrada independente para questionário e resultado simulado

**Prioridade:** após a jornada anônima de segurança
**Estado:** Não iniciada
**Dependências:** C-02, C-06 e J-00 (perguntas, escalas e apresentação aprovadas)
**Jornada-base:** questionário de reconhecimento e triagem.

**Escopo:** construir o percurso guiado conforme instrumento e conteúdo aprovados, com opção de interromper e caminho de emergência. O plano não autoriza criar perguntas, opções, pesos ou classificações clínicas por inferência. A demonstração de resultado deve ser identificada como simulada.

**Critérios de aceite:** cada pergunta/alternativa tem rastreabilidade e aprovação; progresso, retorno/edição, interrupção e resultado correspondem à especificação aprovada; risco agudo interrompe o percurso e oferece canais; estado anônimo não grava respostas.

**Skills:** [Análise de requisitos, backlog e rastreabilidade](../../skills/analise-requisitos-backlog-rastreabilidade.md), [Triagem determinística de risco agudo e avaliação de segurança](../../skills/triagem-risco-agudo-avaliacao-seguranca.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

## 9. Jornadas opcionais/logadas

### L-01 — Cadastro, login e saída da área logada (mock)

**Prioridade:** jornada futura, depois do fluxo anônimo
**Estado:** Não iniciada
**Dependências:** J-00 (regras e mensagens aprovadas), J-01, jornada anônima estável.

**Escopo:** implementar telas e transições de cadastro por apelido/senha, login, tentativa inválida e saída, com autenticação simulada em memória. Não coletar e-mail/telefone real nem sugerir que o mock protege uma conta real.

**Critérios de aceite:** campos e validações vêm de decisão aprovada; estados de erro são explícitos; sessões demonstrativas não persistem como conta real; a área logada nunca é pré-requisito para emergência ou acesso anônimo.

**Skills:** [Autenticação, autorização e área logada pseudonimizada](../../skills/autenticacao-autorizacao-area-logada.md), [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-02 — Migração, histórico e exclusão de conta (mock)

**Prioridade:** jornada futura
**Estado:** Não iniciada
**Dependências:** C-01, L-01, J-00.

**Escopo:** demonstrar migração voluntária da sessão anônima, visualização/continuação de conversas anteriores e exclusão de conta/dados com estados e confirmações aprovados. Toda persistência é simulada e não sobrevive como armazenamento de conta real.

**Critérios de aceite:** migração exige confirmação explícita; o protótipo mostra claramente o limite do armazenamento simulado; exclusão tem confirmação e feedback; falhas não são apresentadas como exclusão concluída; os dados anônimos não são migrados automaticamente.

**Skills:** [Autenticação, autorização e área logada pseudonimizada](../../skills/autenticacao-autorizacao-area-logada.md), [Persistência, criptografia e diário seguro](../../skills/persistencia-criptografia-diario-seguro.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-03 — Módulos de psicoeducação (mock)

**Prioridade:** jornada futura
**Estado:** Não iniciada
**Dependências:** L-01, J-00 (catálogo e conteúdo aprovados).

**Escopo:** demonstrar navegação de catálogo → detalhe → consumo → retomar/concluir, com conteúdo de exemplo aprovado e controles de acessibilidade. Áudio/vídeo não deve parecer conteúdo publicado se for fixture.

**Critérios de aceite:** conteúdo, transcrição/legenda, reprodução, progresso e retomada têm estados rastreáveis; conteúdo simulado está identificado; a usuária pode sair sem pressão ou perda de autonomia.

**Skills:** [Conteúdo multimídia e aprendizagem acessível](../../skills/conteudo-multimidia-aprendizagem-acessivel.md), [Curadoria de conteúdo e engenharia de conhecimento RAG](../../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-04 — Diário de incidentes e exportação demonstrativa

**Prioridade:** jornada futura
**Estado:** Não iniciada
**Dependências:** L-01, J-00 (campos, avisos e ações aprovados).

**Escopo:** demonstrar criação/edição de registro com data, hora e descrição; anexos e exportação protegida só podem ser simulados depois de definir as interações. Não armazenar dados reais nem gerar arquivo que se apresente como evidência jurídica garantida.

**Critérios de aceite:** criação, cancelamento, edição, exclusão e exportação têm estados explícitos; aviso de privacidade precede armazenamento/exportação simulados; nenhuma informação é enviada ou persistida fora do mock em memória; não há promessa de segurança em dispositivo monitorado.

**Skills:** [Persistência, criptografia e diário seguro](../../skills/persistencia-criptografia-diario-seguro.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-05 — Guia/plano de segurança demonstrativo

**Prioridade:** jornada futura
**Estado:** Não iniciada
**Dependências:** J-00 (modo de acesso, conteúdo e regras de salvamento aprovados); L-01 somente se o escopo aprovado exigir conta.

**Escopo:** demonstrar conteúdo informativo, contatos e anotações opcionais conforme a jornada validada. A interface não presume que a usuária deve deixar o relacionamento ou a residência e não substitui atendimento especializado.

**Critérios de aceite:** uso é voluntário; saída sem salvar está disponível; conteúdos e sugestões têm aprovação de domínio; qualquer salvamento aparece como mock; não há ação automática de contato ou compartilhamento.

**Skills:** [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Curadoria de conteúdo e engenharia de conhecimento RAG](../../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

## 10. Referências de execução

- [Jornada do Usuário](./jornada-do-usuario.md) — fluxo, textos, dependências e lacunas funcionais.
- [Requisitos Aurora](../requisitos-aurora.md) — requisitos funcionais e não funcionais.
- [Backlog Aurora](../backlog-aurora.md) — épicos e histórias de usuário.
- [Arquitetura operacionalizada](../arquitetura_operacionalizada_aurora.md) — critérios CA-01 a CA-05 e metas verificáveis.
- Wireframe: `src/frontend/src/wireframe/Aurora — Wireframe.html`.
- Features atualmente observadas: `src/frontend/src/features/`.
- [Índice de skills](../../skills/lista_skills.md) — catálogo e especificações individuais.

## 11. Prompt de origem

O texto abaixo registra a solicitação usada para gerar este plano:

```text
Vamos criar um TO-DO de implementação baseado no documento Jornada do usuario.MD que está dentro da pasta jornada-usuario.

Essa doc se chamara plano-implementacao-jornada-usuario.md e será criado na mesma pasta.

Nessa doc será criada seção com uma lista da tarefas de implementação, aqui vamos definir a ordem de construação de cada jornada.
Essa ordem deve seguir a lógica do que for independente primeiro e da ordem do que possui dependencias.

Temos uma lista de skills verifique quais skills serão utilizadas em cada item de implementação, caso identifique a ausencia
de alguma skill adicione na lista de skill e gere a skill no arquivo devido para consulta futura. Faça referencia no item
de implementação desse plano qual skills será necessária para seguir com a implementação.

Esse documento será sempre consultado e atualizado a cada implementação, cada jornada concluida deve ser sinalizada, essa conclusão
significa, implementar, testar localmente, commitar, publicar, e testar no ambiente aws que, nesse passo deve ser feito por um humano.

As tarefas de implementação devem respeitar os padrões do projeto e do wireframe.

Nesse ponto iremos implementar o frontend e o backend com mocks, prevendo integrações e afins,
aqui, teremos um prototipo de aplicação 100% funcional, integrando front e back, mesmo que o backend
não tenha ainda integrações com RAG, banco e outros serviços, montaremos a estrutura necessário e criaremos
mocks de como seria o consumo e comunicação com esses serviços, mesmo que por inferencia.

Qualquer dúvida me consulte para ajustes. Ao final do documento esse prompt deve estar salvo
para que saibam como a doc foi gerada.
```
