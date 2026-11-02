# Plano de Implementação — Jornada do Usuário Aurora

**Status:** J-00 e J-01 concluídos como preparação documental/técnica; I-01, I-02, I-03, I-04, C-01, C-02, C-03, C-04 e C-05 validados pela usuária em ambiente publicado; nenhuma tarefa foi aprovada pelo time de produto até 02/11/2026; C-06, I-05 e L-01 a L-05 com desenvolvimento concluído localmente (testes locais vistos pela usuária), aguardando commit, publicação e validação humana na AWS; revisões profissionais de segurança/conteúdo pendentes conforme cada tarefa; demais tarefas de implementação não iniciadas
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
- Mensagens de estado e avisos não impeditivos devem ser apresentados no fluxo ou em tela própria, sem modais, tenham ações ou não. O risco agudo é exceção: seu diálogo modal sobrepõe a conversa e exige uma ação explícita para retornar ou escolher um canal.
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

**Aprovação do time de produto:** registrada à parte do teste funcional na AWS. Até 02/11/2026, nenhuma tarefa (I-01 a I-04, C-01 a C-05) foi validada pelo time de produto; o status “Concluída” indica somente implementação publicada e validação funcional pela usuária. Ao receber a aprovação, registrar data, responsável e eventuais ajustes em cada tarefa.

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
| 1 | I-01 | Acesso a emergência por telefone | Independente, P0 | J-01 | Concluída — validada pela usuária em ambiente publicado; aprovação do time de produto pendente |
| 2 | I-02 | Saída Rápida e descarte da sessão | Independente, P0 | J-00, J-01 | Concluída — validada pela usuária em ambiente publicado; aprovação do time de produto pendente |
| 3 | I-03 | Início anônimo e sugestões | Independente, P1 | J-01 | Concluída — validada pela usuária em ambiente publicado; aprovação do time de produto pendente |
| 4 | I-04 | Privacidade e contatos úteis | Independente, P1 | J-00, I-03 | Concluída — validada pela usuária em ambiente publicado; aprovação do time de produto pendente |
| 5 | C-01 | Conversa anônima, mensagens e contexto em memória | Início da jornada dependente | I-03, J-01 | Concluída — conversa e integração validadas pela usuária em ambiente publicado; aprovação do time de produto pendente |
| 6 | C-02 | Triagem de risco agudo antes de resposta informativa | Dependente da mensagem | C-01, J-00 | Concluída — versão inicial validada em 31/10/2026; ajuste das fixtures publicado com C-03 e validado em AWS em 02/11/2026; revisão profissional pendente; aprovação do time de produto pendente |
| 7 | C-03 | Tela de risco agudo, canais e retorno | Dependente da triagem | I-01, I-02, C-02 | Concluída — validada pela usuária em ambiente publicado (AWS) em 02/11/2026; revisão profissional pendente para uso real; aprovação do time de produto pendente |
| 8 | C-04 | Resposta informativa com fontes simuladas | Dependente da triagem sem risco agudo | C-02, J-00 | Concluída — validada pela usuária em ambiente publicado (AWS) em 02/11/2026; revisão jurídica e curadoria das fontes pendentes para uso real; aprovação do time de produto pendente |
| 9 | C-05 | Limite de escopo e alternativas seguras | Ramo dependente da conversa | C-02, J-00 | Concluída — validada pela usuária em ambiente publicado (AWS) em 02/11/2026; revisão jurídica/clínica dos gatilhos pendente; aprovação do time de produto pendente |
| 10 | C-06 | Localização opcional e encaminhamento simulado | Ramo dependente da conversa | C-04, J-00 | Desenvolvimento concluído localmente — validações locais registradas; commit, publicação/AWS, revisão de privacidade da geolocalização e aprovação do time de produto pendentes |
| 11 | I-05 | Entrada independente para questionário e resultado simulado | Independente, opcional | C-02, C-06, decisões de conteúdo | Desenvolvimento concluído localmente — perguntas provisórias e faixa fictícia; commit, publicação/AWS, instrumento validado e aprovação do time de produto pendentes |
| 12 | L-01 | Cadastro, login e saída da área logada (mock) | Jornada futura opcional | J-00, J-01, jornada anônima estável | Desenvolvimento concluído localmente — contas em memória; commit, publicação/AWS, revisão de segurança e aprovação do time de produto pendentes |
| 13 | L-02 | Migração, histórico e exclusão de conta (mock) | Dependente de conta e sessão | C-01, L-01 | Desenvolvimento concluído localmente — conversas cifradas em memória; commit, publicação/AWS, revisão de segurança/privacidade e aprovação do time de produto pendentes |
| 14 | L-03 | Módulos de psicoeducação (mock) | Jornada futura opcional | L-01, decisões de conteúdo | Desenvolvimento concluído localmente — 1 módulo com citações legais e 7 em preparação; commit, publicação/AWS, conteúdo aprovado e aprovação do time de produto pendentes |
| 15 | L-04 | Diário de incidentes e exportação demonstrativa | Jornada futura opcional | L-01, J-00 | Desenvolvimento concluído localmente — diário cifrado em memória, anexo simulado e prévia de exportação; commit, publicação/AWS, revisões e aprovação do time de produto pendentes |
| 16 | L-05 | Guia/plano de segurança demonstrativo | Jornada futura opcional | J-00; L-01 se a decisão aprovada exigir conta | Desenvolvimento concluído localmente — guia com placeholders, plano cifrado e convite por frase de teste; commit, publicação/AWS, conteúdo aprovado e aprovação do time de produto pendentes |

**Legenda de status:** “Concluída” indica implementação publicada e validação humana confirmada em ambiente publicado. I-01, I-02, I-03, I-04, C-01, C-02, C-03, C-04 e C-05 estão concluídas nesse sentido. Nenhuma delas foi aprovada pelo time de produto até 02/11/2026; essa aprovação é registrada separadamente e não é substituída pela validação funcional da usuária. Revisões profissionais de segurança, privacidade e conteúdo continuam pendentes quando indicadas nas tarefas e não são substituídas pela validação funcional. “Desenvolvimento concluído localmente” indica implementação e testes locais finalizados, mas sem publicação e validação humana. O protótipo deve manter componentes e serviços com nomes/responsabilidades de produção; respostas e fixtures estáticas identificam somente a implementação temporária, não a classe/serviço nem a arquitetura final. “Pendente” indica tarefa ainda não concluída e não necessariamente iniciada.

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
| Localização e catálogo | Decisão da usuária (responsável de produto do protótipo) em 02/11/2026: ao abrir **Onde buscar ajuda**, pedir a localização do aparelho e confirmar a cidade sugerida em modal. As coordenadas são convertidas em cidade/UF somente no aparelho (capital mais próxima em até 40 km) e descartadas; apenas a cidade/UF confirmada vai ao backend. O campo manual opcional continua disponível e é o caminho quando a permissão é negada, a localização não está disponível ou não há capital próxima. Fallback de cidade não encontrada: proposta da jornada aprovada (canais nacionais, **Tentar outra cidade**, **Voltar à conversa**). Catálogo do protótipo: serviços fictícios, sem contato. | RNF01 atualizado; revisão de privacidade/LGPD e segurança pendente — inclui o rastro da permissão de localização guardada pelo navegador; aprovação do time de produto pendente |
| Frescor do catálogo | Regras existentes: meta de ≥95% dos registros ativos verificados nos últimos 90 dias; serviços de emergência 100% revistos nos últimos 30 dias; registros com mais de 180 dias sem verificação não podem aparecer como sugestão prioritária e só podem aparecer com aviso explícito. | Definido pelas métricas CA-05; responsável pelo catálogo/rede de serviços deve verificar os contatos |
| Jornadas futuras | Especificar campos, validações e estados ao iniciar cada tarefa correspondente; manter cada fluxo bloqueado até decisões de produto e revisão de domínio aplicáveis. | Decisão de processo registrada; responsável de produto e especialistas relevantes em cada tarefa L-01 a L-05 e I-05 |

**Critério de aceite:** concluído como preparação documental após confirmação final da usuária; decisões, estados, responsáveis por validação e dependências estão registrados. Pendências especializadas não foram declaradas como aprovadas. Não solicitar geolocalização nem implementar o modal de localização até que a política seja revista, aprovada e os requisitos pertinentes sejam atualizados. Tarefas dependentes dessas pendências permanecem **Bloqueadas** ou usam somente mocks claramente identificados, sem alegar que o comportamento é validado.

**Impacto nas dependências:**

| Tarefa dependente | Estado após J-00 | Motivo |
|---|---|---|
| I-02 — Saída Rápida | Concluída — validada pela usuária em ambiente publicado; revisão de segurança ainda pendente | A definição funcional de `/receitas` inclui três opções de receita, mostrando uma por acionamento e sem repetir a última. A revisão de segurança continua registrada como pendência antes de considerar o fluxo aprovado para uso real |
| C-02/C-03 — Triagem e risco agudo | Concluídas e validadas em AWS como protótipo; uso real bloqueado até revisão da rede de proteção e saúde mental | Fixtures sintéticas exercitam os estados; critérios de risco, destaque dos canais e texto de incerteza exigem validação especializada |
| C-04 — Resposta com fontes | Concluída e validada em AWS em 02/11/2026 com duas fixtures de fontes oficiais aprovadas pela usuária em 02/11/2026 para demonstração; conteúdo real continua bloqueado até curadoria e revisão jurídica | Não há autorização para inventar fontes ou afirmações sensíveis; as fixtures citam literalmente a lei, sem interpretação do caso |
| C-05 — Limite de escopo | Concluída e validada em AWS em 02/11/2026 com quatro frases de teste aprovadas pela usuária em 02/11/2026; casos limítrofes e gatilhos reais continuam bloqueados até revisão jurídica e clínica | A distinção geral foi definida; nenhum caso limítrofe foi inventado como regra |
| C-06 — Localização/encaminhamento | Desenvolvimento concluído localmente após decisão da usuária em 02/11/2026 | Geolocalização com confirmação em modal e conversão local; revisão de privacidade/LGPD e segurança pendente |
| I-03/I-04 — Início e privacidade | Podem avançar com o texto registrado, sujeitos à revisão de privacidade antes de uso real | Aviso aprovado para o protótipo, mas revisão LGPD continua pendente |
| I-01 — Telefones de emergência | Pode avançar com destinos e números documentados; verificar os contatos antes de publicação | O protótipo não valida disponibilidade ou atendimento real |
| I-05 — Questionário | Desenvolvimento concluído localmente com perguntas provisórias aprovadas pela usuária em 02/11/2026 | O instrumento validado (perguntas, escala e classificação) continua sem aprovação; nenhuma pergunta clínica foi inventada |
| L-01 — Cadastro/login | Desenvolvimento concluído localmente com regras aprovadas pela usuária em 02/11/2026 | Contas só em memória do processo; não protegem dados reais; revisão de segurança pendente |
| L-02 — Migração/histórico/exclusão | Desenvolvimento concluído localmente com decisões da usuária de 02/11/2026 | Armazenamento só em memória; não é persistência real |
| L-03 — Módulos | Desenvolvimento concluído localmente com decisões da usuária de 02/11/2026 | Conteúdo educativo continua sem aprovação; só o módulo com citações legais tem texto |
| L-04 — Diário | Desenvolvimento concluído localmente com decisões da usuária de 02/11/2026 | Anexos reais e PDF protegido continuam fora; revisão jurídica/segurança pendente |
| L-05 — Guia/plano de segurança | Desenvolvimento concluído localmente com decisões da usuária de 02/11/2026 | Conteúdo do guia e critérios reais de oferta continuam sem aprovação de especialistas |

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
**Estado:** Concluída — publicação e validação humana confirmadas em 31/10/2026. A aprovação do time de produto está pendente.
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
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado confirmada em 31/10/2026. A revisão de segurança permanece pendente para uso real. A aprovação do time de produto está pendente.
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
- A usuária confirmou a validação de I-02 em ambiente publicado em 31/10/2026.
- Pré-carregamento verificado antes da saída para `/receitas`; em viewport de 320 px a página não apresentou overflow horizontal.
- Latência local de Escape medida em 30 execuções a partir do início: p95 47 ms, p99 48 ms, máximo 48 ms. Esta amostra local não certifica as metas em produção nem substitui medição AWS.
- `npm run check`, `npm run build` e `git diff --check` passaram.
- A revisão de segurança e a revisão do texto e das ilustrações permanecem pendentes; a conclusão de implementação/publicação não substitui essas revisões para uso real.

### I-03 — Início anônimo e sugestões

**Prioridade:** P1
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado confirmada em 31/10/2026. A revisão profissional de privacidade permanece pendente para uso real. A aprovação do time de produto está pendente.
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
- A usuária confirmou a validação de I-03 em ambiente publicado em 31/10/2026.
- O aviso e a implementação ainda requerem revisão profissional de privacidade antes de uso real.

### I-04 — Privacidade e contatos úteis

**Prioridade:** P1
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado confirmada em 31/10/2026. As revisões profissionais de privacidade e acessibilidade permanecem pendentes para uso real. A aprovação do time de produto está pendente.
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
- A usuária confirmou a validação de I-04 em ambiente publicado em 31/10/2026.
- Revisão profissional de privacidade/acessibilidade permanece pendente para uso real.

## 8. Jornada anônima dependente

### C-01 — Conversa anônima, mensagens e contexto em memória

**Prioridade:** P1
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado confirmada em 31/10/2026. A validação profissional de privacidade permanece pendente para uso real. A aprovação do time de produto está pendente.
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
- A usuária confirmou a validação de C-01 em ambiente publicado em 31/10/2026.
- A validação profissional de privacidade antes de uso real permanece pendente.

### C-02 — Triagem de risco agudo antes de resposta informativa

**Prioridade:** P0 de segurança
**Estado:** Concluída — a versão inicial foi validada pela usuária em 31/10/2026; o ajuste da regra de fixtures em `TriageService`, feito durante C-03, foi publicado com C-03 e validado em AWS em 02/11/2026. A revisão profissional de segurança e conteúdo permanece pendente. A aprovação do time de produto está pendente.
**Dependências:** C-01, J-00
**Jornada-base:** toda mensagem deve passar pela regra de urgência antes do fluxo informativo.

**Escopo:** o handler de envio orquestra `TriageService` antes de `ChatResponseService`. A porta de triagem devolve status, sinais identificados e orientação de fluxo. As frases exatas de risco agudo interrompem o fluxo informativo; a frase exata **“frase incerta”** apresenta o resultado incerto e também interrompe; toda mensagem que não corresponder a esses casos segue ao serviço de resposta. A avaliação fica exclusivamente em `TriageService`, não no frontend, router ou handler. Os serviços têm nomes e responsabilidades que serão mantidos em produção; atualmente usam fixtures e respostas estáticas para o protótipo. Quando provedores reais forem integrados, substituir esses dados internos pela lógica/conexão real, mantendo os contratos públicos e a orquestração. A implementação não conecta um LLM real nem afirma detectar risco real.

**Fixtures de teste aprovadas pela usuária para o protótipo em 31/10/2026 — revisão profissional de segurança e conteúdo ainda pendente:**

| Sinal simulado | Frases de teste que acionam o mock |
|---|---|
| Ideação suicida | “Estou pensando em me matar”; “Quero tirar minha vida” |
| Agressão em curso | “Ele está me agredindo agora”; “Estou sendo atacada neste momento” |
| Ameaça de morte | “Ele disse que vai me matar”; “Recebi uma ameaça de morte” |
| Presença de arma | “Ele está com uma arma aqui”; “Há uma arma no local agora” |
| Resultado incerto | “frase incerta” |
| Fluxo normal sem risco agudo | “Quero informações sobre serviços de apoio na minha cidade”; qualquer outra mensagem que não corresponda a uma fixture de risco ou à frase incerta |

Atualmente, `TriageService` normaliza caixa, acentos, espaços e pontuação final e compara segmentos completos com as frases de risco. Uma ou mais frases de risco correspondentes resultam em **risco agudo**, registrando todos os sinais e devolvendo orientação sintética sem invocar `ChatResponseService`. A mensagem inteira **“frase incerta”** (com normalização de caixa/espaços e pontuação final) resulta em **indeterminado**, com orientação de incerteza, sem resposta informativa. Qualquer outra mensagem — inclusive frases negadas, hipotéticas, com contexto adicional ou não reconhecidas — resulta em **sem sinal agudo detectado no mock** e segue ao serviço de resposta. Isso é uma regra de demonstração e não uma avaliação segura de mensagens reais; não permite afirmar ausência de risco. A priorização final de canais é responsabilidade do fluxo C-03 e requer validação especializada.

Estas frases servem exclusivamente para demonstrar estados e testar a integração do protótipo. Mesmo com correspondência exata, fixtures não constituem triagem confiável de mensagens reais, não reconhecem variações/contexto e não satisfazem critérios clínicos ou de segurança. O frontend identifica os resultados como simulação; não usar o mock para orientar situações reais nem declarar que detecta risco.

**Critérios de aceite:** contrato distingue risco agudo, resultado incerto da frase configurada e fluxo normal de todas as demais mensagens. Falhas de transporte/servidor permanecem erros explícitos. O handler depende de portas de serviço, sem implementar classificação ou fixtures. `TriageService` retorna status, sinais e orientação; `ChatResponseService` só não é chamado para os resultados agudo e indeterminado. Risco agudo impede resposta informativa e retorna os sinais para C-03. O cliente apresenta o status devolvido pelo serviço. Testes cobrem frases de risco, múltiplos sinais, frase incerta exata, variações de texto incerto que devem seguir o fluxo normal, mensagens negadas/contextualizadas, falha e não invocação do serviço de chat somente para risco agudo/indeterminado. Não declarar o CA-02 atendido com dados estáticos de protótipo.

**Implementação e evidências locais (31/10/2026):**

- `TriageService` aplica fixtures e dados estáticos no protótipo, produzindo `TriageResult` com status, sinais e orientação; `ChatResponseService` fornece a resposta demonstrativa. Esses são os serviços do produto, sem classes paralelas prefixadas com `Mock`; suas implementações serão conectadas a provedores/dados reais no momento oportuno.
- Portas assíncronas `TriageEvaluator` e `ChatResponseGenerator` definem os contratos consumidos pelo handler. A composição injeta ambos serviços na feature. Handler valida entrada, chama primeiro a triagem e só invoca o serviço de resposta para o status da fixture de controle; o router traduz o resultado para o contrato HTTP (`triage_status`, `signals`, `guidance`, `reply`).
- Casos agudos e a frase exata **“frase incerta”** não recebem resposta informativa nem aguardam o atraso simulado de cinco segundos. Todas as demais mensagens seguem ao serviço de resposta e aguardam o atraso.
- Frontend exibe a orientação devolvida pela triagem, rotulada como simulação, e mantém visíveis os contatos úteis; não implementa nem duplica regras de classificação.
- Testes cobrem os oito exemplos de risco, normalização, mensagens negadas/contextualizadas que seguem o fluxo normal, dois sinais reconhecidos, frase incerta exata e variações com texto extra, payloads e atraso.
- A usuária confirmou a validação da versão publicada de C-02 em 31/10/2026 e, com C-03, a do refinamento das fixtures em 02/11/2026; nenhuma versão deve ser usada para orientar situações reais nem ser considerada triagem confiável.

**Skills:** [Triagem determinística de risco agudo e avaliação de segurança](../../skills/triagem-risco-agudo-avaliacao-seguranca.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md).

### C-03 — Tela de risco agudo, canais e retorno

**Prioridade:** P0 de segurança
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado (AWS) confirmada pela usuária em 02/11/2026. A revisão profissional de segurança/conteúdo e a revisão com leitor de tela permanecem pendentes para uso real. A aprovação do time de produto está pendente.
**Dependências:** I-01, I-02, C-02
**Jornada-base:** resultados de risco agudo e incerto.

**Escopo:** apresentar os resultados de risco agudo e incerto em modais sobre a conversa; oferecer ligações apenas após ação explícita da usuária; implementar **Voltar à conversa** fechando o modal, preservando a sessão ainda aberta e mantendo Saída Rápida acessível.

**Critérios de aceite:** resultados agudo e incerto aparecem em modais acessíveis sobre a conversa, visualmente separados do fundo e antes de conteúdo informativo; conversa e relato permanecem visíveis e preservados; modal recebe foco e impede interação com o fundo; conteúdo e ações cabem sem rolagem em viewport usual, com rolagem acessível como alternativa para telas baixas, zoom ou fontes ampliadas; ações para retornar e sair permanecem visíveis; falha de qualquer serviço externo simulado não oculta os números; links de telefone não iniciam automaticamente; **Voltar à conversa** fecha o modal e devolve foco sem duplicar nem perder o relato; **Saída rápida (Esc)** continua disponível dentro dos modais e pelo atalho Esc. Mensagens e avisos comuns, com ou sem ações, não devem abrir modais.

**Implementação e evidências locais (31/10/2026):**

- O resultado `acute` abre um modal sobre a conversa, com cópia do wireframe, canais de telefone, aviso de escolha da usuária e indicação explícita de que a triagem é demonstração e não avalia situações reais.
- Os resultados `acute` e `indeterminate` abrem apresentações dedicadas em modais bloqueantes sobre o chat. A frase exata **“frase incerta”** é a única que aciona o modal de resultado incerto; as demais mensagens não classificadas como risco agudo seguem o fluxo normal.
- No estado agudo, 190 é destacado para agressão em curso, ameaça de morte ou presença de arma; 188 é destacado para ideação suicida; 180 permanece disponível como orientação e 192 como urgência médica. O destaque é provisório, baseado na decisão de produto registrada, e requer aprovação de especialistas; nenhum canal é ocultado.
- Links `tel:` aparecem apenas como escolhas explícitas; nenhum telefone é acionado automaticamente. O modal mantém conversa e mensagens visíveis ao fundo; **Voltar à conversa** fecha o modal, não reenvia o relato e devolve foco à conversa. Como o fundo fica inerte durante o modal, **Saída rápida (Esc)** também está disponível dentro dele; o atalho Esc continua funcionando.
- Padrão geral documentado: avisos e mensagens não impeditivos permanecem no fluxo ou em tela não modal, com ou sem ações. Resultados de triagem aguda e incerta são exceções específicas.
- Refinamento visual: modal usa a largura disponível também no conteúdo interno (sem coluna estreita centralizada) para apresentar canais em duas colunas no desktop, reduz espaços redundantes e mantém a faixa de ações visível. Em celular, os canais ficam em linhas compactas; o modal pode rolar somente quando as dimensões da tela ou preferências de ampliação impedirem o ajuste sem corte.
- Corrigido o estado obsoleto da tela de risco: **Voltar à conversa** limpa o resultado anterior, e cada nova resposta da triagem substitui o estado exibido. Mensagens seguintes não ficam presas ao resultado antigo.
- Execução manual no navegador local: `dialog:modal` confirmou modal nativo aberto com `aria-modal="true"` e conversa ainda montada ao fundo; **Voltar à conversa** fechou o modal. **Saída rápida (Esc)** dentro do modal abriu `/receitas`. A caixa foi redimensionada para ocupar 70% da viewport em desktop e as ações foram separadas numa faixa fixa para continuarem visíveis durante a rolagem do conteúdo.

**Pendências para uso real:** revisão por profissionais da rede de proteção/saúde mental do mapeamento, ordem/destaque e textos; revisão de acessibilidade com leitor de tela. Esta tela não deve ser usada para orientar situações reais.

**Skills:** [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Triagem determinística de risco agudo e avaliação de segurança](../../skills/triagem-risco-agudo-avaliacao-seguranca.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [PWA, privacidade de dispositivo e Saída Rápida](../../skills/pwa-privacidade-dispositivo-saida-rapida.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

**Validações locais C-03 (31/10/2026):**

- [x] `npm run check` — passou (TypeScript sem erros), em 31/10/2026.
- [x] `npm run build` — passou (`vite build`, bundle de produção gerado), em 31/10/2026.
- [x] Regressão local do estado: o retorno limpa o resultado anterior; uma nova resposta `no_acute_signal` permanece na conversa e novos resultados `acute`/`indeterminate` são avaliados independentemente — verificada pela atualização do fluxo de estado e type check/build.
- [x] Regressão backend: `uv run python -m pytest` — 35 testes passaram; Ruff check e formatação passaram, em 31/10/2026.
- [x] Validação anterior no navegador local com respostas controladas: diálogo de risco agudo sobre a conversa, retorno, tela não modal para **“frase incerta”** e mensagem desconhecida com resposta normal, sem reabrir o modal antigo. A exibição não modal foi substituída pela mudança atual.
- [x] Modais de risco e **“frase incerta”** validados pela usuária no ambiente publicado (AWS), com a imagem reconstruída, em 02/11/2026.
- [ ] Revisar modal com leitor de tela e validar posicionamento mobile; o foco modal e a ação **Saída rápida (Esc)** foram verificados no navegador integrado.
- [x] Commits: `20cd68e`, `16a7b48`, `078553a` e `1b7234c` em `develop`/`origin/develop`.
- [x] Publicação e validação humana em AWS — confirmadas pela usuária em 02/11/2026.

### C-04 — Resposta informativa com fontes simuladas

**Prioridade:** P1
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado (AWS) confirmada pela usuária em 02/11/2026. A revisão jurídica e a curadoria formal das fontes permanecem pendentes para uso real. A aprovação do time de produto está pendente.
**Dependências:** C-02 (resultado sem risco agudo), J-00 (fontes aprovadas), J-01
**Jornada-base:** resposta psicoeducativa, fontes e continuação da conversa.

**Escopo:** representar recuperação de trechos e geração por adaptadores mockados, com resposta estruturada e fontes demonstrativas aprovadas. O estado sem fonte relevante declara a limitação; não usar placeholders como citações reais nem mostrar resposta sem fundamentação como informação verificada.

**Critérios de aceite:** resposta inclui fontes identificáveis como fixture de protótipo; estado sem resultado e falha do mock são distintos; LLM/RAG não decide risco nem encaminhamento; consulta posterior mantém contexto sem persistir a sessão anônima; limites do protótipo aparecem onde a pessoa possa confundir simulação com serviço real.

**Decisão da usuária (02/11/2026):** usar fixtures com leis reais, citadas literalmente e marcadas como demonstração; revisão jurídica e curadoria permanecem pendentes. Qualquer outra pergunta retorna o estado sem fonte.

**Fixtures de conhecimento aprovadas para o protótipo — revisão jurídica pendente:**

| Pergunta de teste (comparação exata, normalizada) | Trecho retornado | Fonte |
|---|---|---|
| “O que é violência psicológica?” | Texto literal do art. 7º, II (redação dada pela Lei nº 13.772/2018) | [Lei nº 11.340/2006 — Planalto](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11340.htm) |
| “Violência psicológica é crime?” | Texto literal do caput e da pena do art. 147-B (incluído pela Lei nº 14.188/2021) | [Decreto-Lei nº 2.848/1940 (Código Penal) — Planalto](https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm) |
| Qualquer outra mensagem sem sinal agudo | Nenhum | Estado `no_source` |

Os textos foram conferidos nas páginas do Planalto em 02/11/2026. A comparação usa a mesma normalização das fixtures de triagem (caixa, acentos, espaços e pontuação nas bordas); mensagens com texto adicional não correspondem. Isso não é recuperação semântica nem RAG.

**Implementação e evidências locais (02/11/2026):**

- Criado `KnowledgeService` (porta assíncrona `KnowledgeRetriever`) em `services/knowledge/`, com `KnowledgeResult` (`found`/`no_source`), `KnowledgePassage` e `SourceReference` (`id`, `title`, `locator`, `publisher`, `url`, `version`). `found` sem trecho e `no_source` com trecho são rejeitados pelo modelo. Falha técnica é `KnowledgeUnavailableError`, distinta de `no_source`.
- Normalização de frases-fixture extraída para `services/fixture_text.py` e reutilizada por `TriageService` e `KnowledgeService`, sem mudar a regra de triagem.
- O handler orquestra: triagem → (somente `no_acute_signal`) recuperação → (somente `found`) geração. `ChatResponseService.generate_reply(message, passages)` redige a resposta apenas com os trechos recebidos — no protótipo, frase introdutória “sem opinar sobre o seu caso” seguida da citação literal; recusa gerar sem trechos. O gerador não cria fontes, não decide risco nem encaminhamento. O texto aleatório anterior foi removido.
- Contrato HTTP evoluído de forma coordenada: `knowledge_status` (`found` | `no_source` | `null` quando a triagem bloqueia), `sources` e `demo`. Falha da recuperação retorna `503` sem resposta nem eco da mensagem.
- Frontend valida o novo contrato em runtime (combinações coerentes de `triage_status`, `knowledge_status`, `reply`, `guidance` e `sources`; URL `https://`), mostra o bloco **Fontes** com link para a fonte oficial (nova aba, `rel="noreferrer"`), órgão e versão, e o aviso de demonstração com revisão jurídica pendente. O estado sem fonte mostra “Não encontrei uma fonte confiável para responder a isso. Prefiro dizer que não sei a inventar uma resposta.” O aviso do wireframe “Toda resposta mostra de onde veio a informação…” foi incluído na lateral da conversa.
- Contexto: o histórico continua apenas no estado React em memória e o backend recebe só a mensagem atual (decisão J-01); nenhuma resposta, fonte ou mensagem é persistida ou registrada em log.
- Fora do escopo desta tarefa e não implementado: abertura “padrão que tem nome” e explicação interpretativa do wireframe (exigem conteúdo curado), botões **Onde buscar ajuda** (C-06) e **O que acontece no meu caso?** (frase tratada como limite em C-05), guardrail de saída e qualquer RAG/LLM real.

**Validações locais C-04 (02/11/2026):**

- [x] Backend: `pytest` — 48 testes passaram (fixtures de conhecimento, normalização, `no_source`, modelo rejeitando `found` sem trecho, gerador só com trechos recebidos, handler sem recuperação/geração para agudo/indeterminado, sem geração para `no_source`, falha → `503`, payload HTTP com fontes); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Integração local navegador → Vite → FastAPI: as duas perguntas de teste retornaram `found` com a fonte esperada em ~5 s; “Tenho dúvidas sobre meus direitos” retornou `no_source`; frase de risco retornou `acute` sem conhecimento nem atraso.
- [x] Navegador headless: bloco **Fontes** e aviso de demonstração exibidos; estado sem fonte exibido sem fontes e sem modal; viewport de 320 px sem overflow horizontal; `localStorage`/`sessionStorage` vazios. Único erro de console: `404` de `/favicon.ico`, anterior a esta tarefa.
- [ ] Revisão jurídica das citações e da frase introdutória; curadoria formal das fontes.
- [x] Commit: `1b7234c` em `develop`/`origin/develop` (mensagem do commit: “Resolução C-03”; contém a implementação e a documentação do C-04).
- [x] Publicação e validação humana em AWS — confirmadas pela usuária em 02/11/2026.

**Skills:** [Curadoria de conteúdo e engenharia de conhecimento RAG](../../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [Integração de LLM e engenharia de prompts](../../skills/integracao-llm-engenharia-prompts.md), [Guardrails, escopo ético e avaliação generativa](../../skills/guardrails-escopo-etico-avaliacao-generativa.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md).

### C-05 — Limite de escopo e alternativas seguras

**Prioridade:** P1
**Estado:** Concluída — implementação publicada e validação humana em ambiente publicado (AWS) confirmada pela usuária em 02/11/2026. A aprovação do time de produto e a revisão jurídica/clínica dos gatilhos permanecem pendentes.
**Dependências:** C-02, J-00 (regra e conteúdo aprovados)
**Jornada-base:** pedidos de diagnóstico ou parecer individualizado.

**Escopo:** apresentar o bloco **Fora do que eu posso fazer** nos casos aprovados, sem encerrar a conversa; permitir seguir para informação geral ou encaminhamento. Casos limítrofes não devem ser inventados como regra do mock.

**Critérios de aceite:** mensagem e alternativas correspondem ao texto aprovado; pedidos gerais sobre direitos continuam no fluxo informativo; nenhuma resposta simula diagnóstico, aconselhamento jurídico individual ou decisão pela usuária; testes cobrem limites e continuidade.

**Decisões da usuária (02/11/2026):**

- Usar uma frase de teste por categoria (duas para parecer jurídico individual), com comparação exata normalizada, como nas demais fixtures. Qualquer outra mensagem segue o fluxo informativo.
- **O que a lei diz** envia “O que é violência psicológica?” como nova mensagem da usuária, passando por triagem, escopo e fontes (C-04).
- **Defensoria Pública ou CRAM** leva ao painel de contatos úteis existente enquanto C-06 está bloqueado. Para não prometer o que o painel não lista, o bloco informa: “No protótipo, este botão leva aos contatos gerais desta tela. Opções de Defensoria Pública e CRAM entram com o encaminhamento por cidade.”

**Fixtures de limite de escopo aprovadas para o protótipo — revisão jurídica e clínica pendente:**

| Categoria | Frase de teste (comparação exata, normalizada) |
|---|---|
| Diagnóstico (`diagnosis`) | “Eu tenho depressão?” |
| Prescrição (`prescription`) | “Que remédio devo tomar?” |
| Parecer jurídico individual (`individual_legal_opinion`) | “O que acontece no meu caso?” (rótulo do wireframe); “Devo denunciar meu marido?” |
| Permanece no fluxo informativo | Perguntas gerais sobre direitos (ex.: “Quais são os direitos de uma mulher em situação de violência?”), as perguntas de C-04 e frases de teste com texto adicional |

**Implementação e evidências locais (02/11/2026):**

- Criado `GuardrailService` (porta assíncrona `ScopeGuardrail`) em `services/guardrail/`, com `GuardrailResult` (`allow` | `out_of_scope` + categoria); o modelo rejeita `out_of_scope` sem categoria e `allow` com categoria. Indisponibilidade é `GuardrailUnavailableError` e falha fechada (HTTP `503`, sem resposta).
- Ordem no handler: triagem → (somente `no_acute_signal`) limite de escopo → (somente `allow`) recuperação de fontes → (somente `found`) geração. Pedido fora do escopo não consulta fontes nem gera texto e não aguarda o atraso simulado. A triagem sempre precede o guardrail: frase de risco abre o modal de C-03 mesmo que também pareça pedido fora do escopo.
- Contrato HTTP evoluído: `scope_status` (`allowed` | `out_of_scope` | `null` quando a triagem bloqueia) e `out_of_scope_category`. O frontend valida as combinações em runtime.
- Frontend: o limite aparece como mensagem da Aurora no fluxo (sem modal), com título **Fora do que eu posso fazer**, texto do wireframe, ações **O que a lei diz** e **Defensoria Pública ou CRAM**, nota sobre o destino do botão no protótipo, aviso de autonomia do wireframe e aviso de demonstração. O campo de mensagem continua disponível; a conversa não é encerrada.
- O texto do wireframe é usado para as três categorias, conforme decisão de J-00; a resposta não simula diagnóstico, prescrição, parecer individual nem decisão pela usuária.

**Validações locais C-05 (02/11/2026):**

- [x] Backend: `pytest` — 69 testes passaram (quatro fixtures e categorias, normalização, perguntas gerais e frases com texto adicional permitidas, modelo de resultado, handler sem fontes/geração quando fora do escopo, triagem antes do guardrail, falha fechada → `503`, payload HTTP sem resposta/fontes/atraso, `scope_status: "allowed"` no fluxo informativo); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador local (Vite → FastAPI): “O que acontece no meu caso?” exibiu o bloco em ~130 ms, sem modal e com campo ativo; **Defensoria Pública ou CRAM** levou o foco ao título dos contatos úteis; **O que a lei diz** enviou “O que é violência psicológica?” e recebeu resposta com **Fontes**; “Que remédio devo tomar?” exibiu o limite; pergunta geral sobre direitos seguiu o fluxo informativo (estado sem fonte); viewport de 320 px sem overflow horizontal. Único erro de console: `404` de `/favicon.ico`, anterior.
- [ ] Revisão jurídica, clínica e de produto dos gatilhos, de exemplos limítrofes e da aplicação do texto do wireframe à categoria prescrição.
- [x] Commit: `21d0a86` (“resolucao C-05”) em `develop`.
- [x] Publicação e validação humana em AWS — confirmadas pela usuária em 02/11/2026.
- [ ] Aprovação do time de produto — pendente.

**Skills:** [Guardrails, escopo ético e avaliação generativa](../../skills/guardrails-escopo-etico-avaliacao-generativa.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### C-06 — Localização opcional e encaminhamento simulado

**Prioridade:** P1
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam commit, publicação, validação humana na AWS, revisão de privacidade/LGPD e segurança da geolocalização e aprovação do time de produto.
**Dependências:** C-04, J-00 (política de localização e fallback aprovados), I-01
**Jornada-base:** informar Cidade/UF e ver até três opções priorizadas.

**Escopo:** aceitar município/UF informado voluntariamente; consultar catálogo mockado; apresentar cartões no formato do wireframe e retorno à conversa. Não solicitar geolocalização precisa, não encaminhar o relato e não apresentar fixture como contato real/verificado.

**Bloqueio anterior resolvido em 02/11/2026:** Decisão da usuária (responsável de produto do protótipo) em 02/11/2026: ao abrir **Onde buscar ajuda**, pedir a localização do aparelho e confirmar a cidade sugerida em modal. As coordenadas são convertidas em cidade/UF somente no aparelho (capital mais próxima em até 40 km) e descartadas; apenas a cidade/UF confirmada vai ao backend. O campo manual opcional continua disponível e é o caminho quando a permissão é negada, a localização não está disponível ou não há capital próxima. RNF01 foi atualizado com essa alteração. A revisão de privacidade/LGPD e segurança continua pendente; ela deve avaliar, entre outros pontos, que o navegador guarda a permissão de localização do site (rastro visível no aparelho, fora do controle do Aurora).

**Critérios de aceite:** localização pode ser omitida sem bloquear canais gerais; resultados simulados mostram indicação de protótipo; lista tem no máximo três itens e segue a ordem definida pelo requisito/matriz aprovada; cidade sem resultado, ambígua, indisponibilidade e contato desatualizado têm estados definidos; retorno preserva conversa em memória.

**Decisões da usuária (02/11/2026):** geolocalização com confirmação em modal (acima); catálogo com serviços **fictícios** em duas cidades de teste, sem contato, horário, custo nem data de verificação inventados; texto de cidade não encontrada conforme a proposta da jornada; entrada pela ação fixa **Onde buscar ajuda** na lateral da conversa. O botão **Defensoria Pública ou CRAM** do C-05 continua levando aos contatos úteis.

**Fixtures do catálogo — demonstração, sem dados reais:**

| Cidade de teste | Opções (ordem pela hierarquia jurídica) |
|---|---|
| Recife / PE | 1 · Órgão público — Defensoria Pública do Estado — exemplo; 2 · Serviço especializado — Centro de Referência de Atendimento à Mulher — exemplo; 3 · Sociedade civil — Organização da sociedade civil — exemplo |
| São Paulo / SP | Mesmas três opções fictícias |
| Qualquer outra cidade/UF válida | `no_verified_result` |

**Implementação e evidências locais (02/11/2026):**

- Novo bounded context `referral` com a feature `recommend_services` (`POST /api/referral/recommendations`, corpo `{city, state}`) e `CatalogService` (porta assíncrona `ServiceCatalog`). O serviço ordena pela hierarquia (`ServiceTier`: órgão público → serviço especializado → sociedade civil → voluntariado) e o modelo rejeita mais de três opções. UF inválida ou cidade vazia → `422`; falha do catálogo (`CatalogUnavailableError`) → `503`; cidade fora do catálogo → `no_verified_result`. Os registros vêm propositalmente fora de ordem para o teste comprovar a priorização.
- A normalização de frases-fixture foi movida para `aurora_backend/shared/fixture_text.py`, usada pelos dois contextos sem acoplamento entre eles.
- Frontend `features/referral/`: `ReferralPanel` substitui a área da conversa enquanto aberto; a conversa fica apenas oculta (mensagens e rascunho preservados) e **← Voltar à conversa** devolve o foco. Ao abrir, pede a localização (`enableHighAccuracy: false`, `maximumAge: 0`, 10 s); `location.ts` encontra a capital mais próxima em até 40 km e descarta as coordenadas. Com cidade sugerida, abre o modal **Confirmar sua cidade** (**Usar esta cidade**, **Digitar outra cidade**, **Saída rápida (Esc)**). Sem permissão, sem suporte ou sem capital próxima, mostra mensagem de estado e mantém o campo manual.
- Campo **Cidade / UF (opcional)** com o texto e o placeholder do wireframe; formato inválido mostra “Informe a cidade e a UF, por exemplo: Recife / PE.”. Resultados: título “Onde buscar ajuda em Cidade / UF”, introdução do wireframe, cartões com posição, categoria, **O que faz**, **Contato**, **Horário** e **Custo** (“Não incluído na demonstração”) e a nota “Demonstração: serviços fictícios, sem contatos verificados. Nada desta busca fica salvo.”. Sem resultado: texto aprovado, **Ver canais nacionais**, **Tentar outra cidade** e **Voltar à conversa**. Erro técnico: alerta com **Tentar novamente**.
- O botão **Ver contato** do wireframe não é exibido porque nenhum contato fictício é mostrado. A regra de frescor do CA-05 não é exercitada: não há datas de verificação nas fixtures.

**Validações locais C-06 (02/11/2026):**

- [x] Backend: `pytest` — 86 testes passaram (17 novos: hierarquia e limite de três, normalização da cidade, cidade/UF fora do catálogo, `422` para cidade vazia/UF inválida, coordenadas ignoradas e nunca devolvidas, falha → `503` sem ecoar a cidade); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless com geolocalização simulada: perto de Recife → modal “Encontramos: Recife / PE” → três cartões na ordem 1 · Órgão público, 2 · Serviço especializado, 3 · Sociedade civil; **← Voltar à conversa** reexibiu a conversa com o rascunho preservado. Permissão negada → mensagem de localização indisponível; “Recife” sem UF → erro de formato; “Olinda / PE” → estado sem resultado; **Tentar outra cidade** focou o campo. Coordenada longe das capitais → mensagem sem modal; busca manual “São Paulo / SP” funcionou; viewport de 320 px sem overflow horizontal; Esc abriu `/receitas`. As requisições enviaram apenas `{"city","state"}`, nunca coordenadas. Único erro de console: `404` de `/favicon.ico`, anterior.
- [ ] Revisão de privacidade/LGPD e segurança da geolocalização (incluindo a permissão guardada pelo navegador) e aprovação do time de produto.
- [x] Teste local visto e aprovado pela usuária em 02/11/2026 (demonstração em janela do navegador).
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes; não marcar a tarefa como concluída sem confirmação. Observação: na AWS, a geolocalização só funciona em HTTPS, e fora de uma capital o fluxo cai para a digitação manual.

**Skills:** [Catálogo de serviços e motor de encaminhamento](../../skills/catalogo-servicos-motor-encaminhamento.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### I-05 — Entrada independente para questionário e resultado simulado

**Prioridade:** após a jornada anônima de segurança
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam commit, publicação, validação humana na AWS, aprovação do instrumento por especialistas e aprovação do time de produto.
**Dependências:** C-02, C-06 e J-00 (perguntas, escalas e apresentação aprovadas)
**Jornada-base:** questionário de reconhecimento e triagem.

**Escopo:** construir o percurso guiado conforme instrumento e conteúdo aprovados, com opção de interromper e caminho de emergência. O plano não autoriza criar perguntas, opções, pesos ou classificações clínicas por inferência. A demonstração de resultado deve ser identificada como simulada.

**Critérios de aceite:** cada pergunta/alternativa tem rastreabilidade e aprovação; progresso, retorno/edição, interrupção e resultado correspondem à especificação aprovada; risco agudo interrompe o percurso e oferece canais; estado anônimo não grava respostas.

**Decisões da usuária (02/11/2026):**

- Perguntas de reconhecimento: dois placeholders explícitos, sem conteúdo clínico (“Pergunta de demonstração 1/2”, alternativas “Opção de demonstração A/B” e “Prefiro não responder”), até a aprovação do instrumento validado (E4-US1).
- Terceira pergunta: tipo de ajuda do backlog E4-US4 — Denúncia, Orientação jurídica, Apoio psicológico, Apoio entre pares, Prefiro não responder.
- Resultado com **faixa simulada**: “Faixa de demonstração A/B/C”, calculada pelo número de respostas “Opção de demonstração A” nas perguntas 1 e 2 (2 → A, 1 → B, 0 → C). A tela informa que a faixa é fictícia e não indica padrão de violência, risco nem diagnóstico.
- Entrada: botão **Responder questionário** na lateral da conversa.

**Implementação e evidências locais (02/11/2026):**

- Novo bounded context `questionnaire` com a feature `take_questionnaire`: `GET /api/questionnaire/questions` (perguntas servidas pelo backend, substituíveis pelo instrumento aprovado) e `POST /api/questionnaire/results` com `{answers}` → `{band, help_type, demo}`. `QuestionnaireService` (porta `Questionnaire`) valida que todas as perguntas foram respondidas com alternativas válidas (`422` caso contrário). Nada é persistido nem registrado.
- Frontend `features/questionnaire/QuestionnairePanel`: uma pergunta por tela com progresso “Passo X de 3”, **Continuar** desativado até haver resposta, **Voltar** preservando respostas, **Parar questionário** (descarta as respostas e volta à conversa) e **Estou em perigo agora** visível em todas as etapas. Esse botão interrompe o questionário e abre o modal de risco agudo do C-03 com todos os canais (E4-US6). Resultado: faixa, aviso de demonstração, tipo de ajuda escolhido, **Onde buscar ajuda** (C-06) e **Conversar com a Aurora**.
- Como no C-06, a conversa fica oculta enquanto o questionário está aberto e é reexibida intacta.
- Limites: as perguntas de demonstração não exercitam a regra de risco agudo por resposta; a interrupção por risco é feita pelo botão explícito. A pergunta de urgência (E4-US3) e o histórico logado (E4-US7) não foram implementados.

**Validações locais I-05 (02/11/2026):**

- [x] Backend: `pytest` — 99 testes passaram (13 novos: perguntas e alternativas servidas, cálculo das faixas, “Prefiro não responder”, respostas incompletas/extras/inválidas → `422`, endpoint de resultado); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless: passo 1 de 3 com foco no título e **Continuar** desativado; **Voltar** manteve as respostas; resultado “Faixa de demonstração B” para A + “Prefiro não responder”, com “Orientação jurídica”; **Onde buscar ajuda** abriu o C-06; reabrir o questionário começou sem respostas; **Estou em perigo agora** abriu o modal “Você pode estar em perigo agora.” e **Voltar à conversa** reexibiu a conversa; **Parar questionário** voltou à conversa; 320 px sem overflow horizontal; `localStorage`/`sessionStorage` vazios.
- [x] Teste local visto e aprovado pela usuária em 02/11/2026 (demonstração em janela do navegador).
- [ ] Aprovação do instrumento validado (perguntas, escala, classificação e textos) por especialistas e aprovação do time de produto.
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes.

**Skills:** [Análise de requisitos, backlog e rastreabilidade](../../skills/analise-requisitos-backlog-rastreabilidade.md), [Triagem determinística de risco agudo e avaliação de segurança](../../skills/triagem-risco-agudo-avaliacao-seguranca.md), [Domínio de violência psicológica e design informado por trauma](../../skills/dominio-violencia-psicologica-design-informado-trauma.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

## 9. Jornadas opcionais/logadas

### L-01 — Cadastro, login e saída da área logada (mock)

**Prioridade:** jornada futura, depois do fluxo anônimo
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam teste visto pela usuária, commit, publicação, validação humana na AWS, revisão de segurança/privacidade e aprovação do time de produto.
**Dependências:** J-00 (regras e mensagens aprovadas), J-01, jornada anônima estável.

**Escopo:** implementar telas e transições de cadastro por apelido/senha, login, tentativa inválida e saída, com autenticação simulada em memória. Não coletar e-mail/telefone real nem sugerir que o mock protege uma conta real.

**Critérios de aceite:** campos e validações vêm de decisão aprovada; estados de erro são explícitos; sessões demonstrativas não persistem como conta real; a área logada nunca é pré-requisito para emergência ou acesso anônimo.

**Decisões da usuária (02/11/2026):**

- Apelido: 3 a 30 caracteres (letras, números, ponto, hífen, sublinhado), único sem diferenciar maiúsculas. Senha forte: mínimo 10 caracteres com letras e números (máximo 128), com confirmação e **Mostrar senha**. Aviso: “Não use seu nome real nem uma senha que você usa em outro lugar. Não é preciso e-mail nem telefone.”
- Login inválido: “Apelido ou senha incorretos.” (não revela se o apelido existe). Sem recuperação de senha: “Sem e-mail, não é possível recuperar a senha. Guarde-a em lugar seguro.” Cinco tentativas erradas seguidas para o mesmo apelido bloqueiam por 1 minuto: “Muitas tentativas. Aguarde 1 minuto e tente novamente.”
- Entrada: link **Entrar** no rodapé da tela inicial (vira **Minha conta** com sessão ativa), tela `/conta` com **Entrar** / **Criar conta**; área logada mínima: “Olá, [apelido]”, **Ir para a conversa** e **Sair da conta**. Histórico, migração e exclusão ficam para o L-02.
- Armazenamento: contas e sessões na memória do processo do backend; token só na memória da página.

**Implementação e evidências locais (02/11/2026):**

- Novo bounded context `accounts`: `POST /api/accounts` (cadastro, `201`), `POST /api/sessions` (login), `GET /api/sessions/current` e `DELETE /api/sessions/current` (token `Bearer`). `AccountService` (porta `Accounts`) guarda senha com hash scrypt e sal aleatório, compara em tempo constante, calcula hash também para apelido inexistente e conta tentativas por apelido mesmo sem conta, para o bloqueio (`429`) não revelar cadastros. Sessões expiram em 30 minutos. Erros: `422` regras, `409` apelido em uso, `401` credenciais/sessão, `429` bloqueio.
- Frontend: `features/account/AccountPage` e `accountApi`. O token fica no estado do `App` (sem cookie, `localStorage` ou `sessionStorage`). **Sair da conta**, a Saída Rápida (botão e Esc) e o recarregamento encerram a sessão; a Saída Rápida chama `DELETE` com `keepalive` sem aguardar a rede. A conversa anônima continua acessível sem conta.
- Limites: contas somem quando o backend reinicia e não são compartilhadas entre instâncias (na AWS com mais de uma instância, o login pode falhar); o registro de tentativas cresce sem limite na memória; o hash scrypt roda no laço de eventos. Nada disso é adequado para uso real.

**Validações locais L-01 (02/11/2026):**

- [x] Backend: `pytest` — 118 testes passaram (19 novos: regras de apelido e senha, unicidade sem diferenciar maiúsculas, senha não armazenada em texto, erro genérico igual para senha errada e apelido inexistente, bloqueio após 5 erros com e sem conta, liberação após 1 minuto, reinício da contagem após login, logout e expiração, fluxo HTTP e códigos `201/409/422/401/429`); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless: **Entrar** no rodapé abriu `/conta`; senha fraca e senhas diferentes mostraram os erros; **Mostrar senha** funcionou; cadastro levou a “Olá, [apelido]”; **Sair da conta** voltou ao formulário; senha errada → “Apelido ou senha incorretos.”; login → **Ir para a conversa** → Esc abriu `/receitas` e encerrou a sessão no servidor (`DELETE` `204`), e o rodapé voltou a mostrar **Entrar**; cinco erros → mensagem de bloqueio; 320 px sem overflow; sem cookies nem armazenamento local. Corrigido durante o teste: campos com altura excessiva no formulário.
- [x] Teste local visto e aprovado pela usuária em 02/11/2026 (demonstração em janela do navegador).
- [ ] Revisão de segurança/privacidade e aprovação do time de produto.
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes.

**Skills:** [Autenticação, autorização e área logada pseudonimizada](../../skills/autenticacao-autorizacao-area-logada.md), [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-02 — Migração, histórico e exclusão de conta (mock)

**Prioridade:** jornada futura
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam teste visto pela usuária, commit, publicação, validação humana na AWS, revisão de segurança/privacidade e aprovação do time de produto.
**Dependências:** C-01, L-01, J-00.

**Escopo:** demonstrar migração voluntária da sessão anônima, visualização/continuação de conversas anteriores e exclusão de conta/dados com estados e confirmações aprovados. Toda persistência é simulada e não sobrevive como armazenamento de conta real.

**Critérios de aceite:** migração exige confirmação explícita; o protótipo mostra claramente o limite do armazenamento simulado; exclusão tem confirmação e feedback; falhas não são apresentadas como exclusão concluída; os dados anônimos não são migrados automaticamente.

**Decisões da usuária (02/11/2026):**

- Migração: botão **Salvar conversa na conta** na lateral da conversa. Sem sessão, o formulário Entrar/Criar conta abre dentro da área da conversa, sem perder as mensagens. Em seguida, confirmação explícita: “Isto vai guardar N mensagens desta conversa na conta [apelido]. Salvar?” com **Salvar** / **Cancelar**.
- Histórico em **Minha conta**: lista (data, início da primeira mensagem, número de mensagens) com **Ver** (somente leitura) e **Excluir** por conversa.
- Armazenamento: memória do servidor, cifrado com AES-GCM usando chave derivada da senha (scrypt, sal próprio) no login; a chave existe só enquanto a sessão está aberta.
- Exclusão da conta: **Excluir conta e todos os dados** → confirmação na própria tela, sem modal (“Isto apaga a conta e N conversas salvas. Não dá para desfazer.”, **Excluir agora** / **Cancelar**) → “Conta e dados excluídos.”. Em falha, a mensagem diz que nada foi apagado.

**Implementação e evidências locais (02/11/2026):**

- Contexto `accounts` ampliado: `POST/GET /api/account/conversations`, `GET/DELETE /api/account/conversations/{id}` e `DELETE /api/accounts/current`, todos com token `Bearer`. `AccountService` cifra cada conversa (papel e texto das mensagens) com AES-GCM, nonce aleatório e dados associados `conta:id`; o servidor não guarda a chave fora da sessão. Limites: até 50 conversas por conta, 200 mensagens por conversa, 4.000 caracteres por mensagem e papéis `user`/`assistant`. Excluir a conta remove conta, conversas, contagem de tentativas e todas as sessões dela.
- Nova dependência do backend: `cryptography` (registrada em `pyproject.toml` e `uv.lock`; o Dockerfile instala pelo lock).
- Frontend: `AccountForm` reutilizável (página de conta e painel de salvar); `SaveConversationPanel` na conversa, com **Ver em Minha conta** após salvar (navegação interna, sem recarregar e perder a sessão); `AccountPage` com histórico, visualização somente leitura, exclusão por conversa e exclusão da conta, todas com confirmação na tela. Sessão expirada (`401`) volta ao formulário com “Sua sessão terminou. Entre de novo para continuar.”.
- Limites: só papel e texto são guardados (fontes, blocos de limite e encaminhamentos reaparecem como texto); a conversa não pode ser continuada a partir do histórico; os dados somem quando o backend reinicia; a cifra protege contra leitura do armazenamento, não contra o próprio processo enquanto a sessão está aberta.

**Validações locais L-02 (02/11/2026):**

- [x] Backend: `pytest` — 130 testes passaram (12 novos: salvar/listar/ler, texto cifrado em repouso, nova sessão com a senha lê conversas anteriores, isolamento entre contas, mensagens inválidas e limites, exclusão de conversa, exclusão da conta com todas as sessões, fluxo HTTP `201/200/204/401/404/422`); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless: conversa anônima → **Salvar conversa na conta** → criar conta dentro da conversa → confirmação com “2 mensagens” (nenhum envio antes de **Salvar**) → salva, conversa preservada → **Ver em Minha conta** → histórico com 2 itens → **Ver** mostrou a transcrição → exclusão de uma conversa com confirmação → falha simulada (`500`) da exclusão da conta mostrou “Não foi possível excluir a conta. Nada foi apagado; tente novamente.” e manteve a sessão → exclusão real mostrou “Conta e dados excluídos.” → login com o apelido excluído falhou. 320 px sem overflow; sem cookies nem armazenamento local. Corrigidos durante o teste: falta de caminho da conversa para **Minha conta** sem recarregar e mensagem genérica em falha de exclusão.
- [x] Teste local visto e aprovado pela usuária em 02/11/2026 (demonstração em janela do navegador).
- [ ] Revisão de segurança/privacidade (cifra, chave em memória, exclusão verificável) e aprovação do time de produto.
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes.

**Skills:** [Autenticação, autorização e área logada pseudonimizada](../../skills/autenticacao-autorizacao-area-logada.md), [Persistência, criptografia e diário seguro](../../skills/persistencia-criptografia-diario-seguro.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-03 — Módulos de psicoeducação (mock)

**Prioridade:** jornada futura
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam teste visto pela usuária, commit, publicação, validação humana na AWS, conteúdo aprovado por especialistas e aprovação do time de produto.
**Dependências:** L-01, J-00 (catálogo e conteúdo aprovados).

**Escopo:** demonstrar navegação de catálogo → detalhe → consumo → retomar/concluir, com conteúdo de exemplo aprovado e controles de acessibilidade. Áudio/vídeo não deve parecer conteúdo publicado se for fixture.

**Critérios de aceite:** conteúdo, transcrição/legenda, reprodução, progresso e retomada têm estados rastreáveis; conteúdo simulado está identificado; a usuária pode sair sem pressão ou perda de autonomia.

**Decisões da usuária (02/11/2026):**

- Catálogo com os temas do backlog E6-US1/US2. O módulo **O que é violência psicológica** reaproveita as citações literais aprovadas no C-04 (Lei nº 11.340/2006, art. 7º, II; Código Penal, art. 147-B); os outros sete trazem só “Conteúdo em preparação — demonstração. Este módulo ainda não tem texto aprovado por especialistas.”.
- Somente texto: aviso “Áudio e vídeo com legenda e transcrição: ainda não disponíveis nesta demonstração.”; nenhum player simulado.
- Progresso por seção salvo na conta, com **Continuar de onde parei**; ao concluir, “Você concluiu este módulo. Você decide o que fazer com o que leu.”, sem pontuação (E6-US5).
- Entrada: seção **Módulos** em **Minha conta**; sem conta, não aparece.

**Implementação e evidências locais (02/11/2026):**

- Novo bounded context `learning` com a feature `browse_modules`: `GET /api/learning/modules` e `GET /api/learning/modules/{id}`; `ModuleCatalogService` (porta `ModuleCatalog`) mantém o catálogo estático, a ser substituído pelo painel de conteúdo (E11). As citações legais passaram para `aurora_backend/shared/legal_sources.py`, usadas pelo C-04 e pelos módulos sem acoplar os contextos.
- Progresso no contexto `accounts`: `GET /api/account/module-progress` e `PUT /api/account/module-progress/{module_id}` com `{section, completed}`; rever um módulo concluído não desfaz a conclusão; o progresso é apagado com a conta. O progresso não é cifrado (não contém relato); limites de 100 módulos e 50 seções.
- Frontend `features/learning/LearningArea`: lista com tema, situação (“Não iniciado”, “Parte X de N”, “Concluído”) e “em preparação”; ações **Começar**, **Continuar de onde parei** e **Rever**; leitor com “Parte X de N”, **Anterior**, **Próxima**, **Concluir módulo**, fonte com link para o Planalto, aviso de mídia e de demonstração. Falha ao salvar o progresso aparece no fluxo sem impedir a leitura.
- Fora do escopo: sugestões personalizadas a partir do chat (E6-US4) e qualquer conteúdo educativo próprio.

**Validações locais L-03 (02/11/2026):**

- [x] Backend: `pytest` — 139 testes passaram (9 novos: catálogo com um módulo pronto, citações literais, placeholders sem afirmações, progresso salvo e conclusão mantida, progresso inválido, progresso apagado com a conta, fluxo HTTP `200/401/404/422`); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless: sem conta, a tela inicial não mostra módulos; com conta, oito módulos “Não iniciado”; leitor abriu com foco no título e a citação da Lei Maria da Penha com fonte; Parte 2 mostrou a fonte do Código Penal; ao sair e voltar, “Parte 2 de 2” e **Continuar de onde parei** retomou na Parte 2; **Concluir módulo** mostrou a mensagem de conclusão e a lista passou a “Concluído” / **Rever**; módulo em preparação exibiu apenas o placeholder; 320 px sem overflow.
- [x] Teste local visto e aprovado pela usuária em 02/11/2026 (demonstração em janela do navegador).
- [ ] Conteúdo dos módulos aprovado por especialistas e aprovação do time de produto.
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes.

**Skills:** [Conteúdo multimídia e aprendizagem acessível](../../skills/conteudo-multimidia-aprendizagem-acessivel.md), [Curadoria de conteúdo e engenharia de conhecimento RAG](../../skills/curadoria-conteudo-engenharia-conhecimento-rag.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Acessibilidade, inclusão e linguagem simples](../../skills/acessibilidade-inclusao-linguagem-simples.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-04 — Diário de incidentes e exportação demonstrativa

**Prioridade:** jornada futura
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam teste visto pela usuária, commit, publicação, validação humana na AWS, revisões de segurança, privacidade e jurídica e aprovação do time de produto.
**Dependências:** L-01, J-00 (campos, avisos e ações aprovados).

**Escopo:** demonstrar criação/edição de registro com data, hora e descrição; anexos e exportação protegida só podem ser simulados depois de definir as interações. Não armazenar dados reais nem gerar arquivo que se apresente como evidência jurídica garantida.

**Critérios de aceite:** criação, cancelamento, edição, exclusão e exportação têm estados explícitos; aviso de privacidade precede armazenamento/exportação simulados; nenhuma informação é enviada ou persistida fora do mock em memória; não há promessa de segurança em dispositivo monitorado.

**Decisões da usuária (02/11/2026):**

- Seção **Diário** em **Minha conta**. Campos: Data (obrigatória, não futura), Hora (opcional, HH:MM), Descrição (obrigatória, até 4.000 caracteres). Ações: **Novo registro**, **Editar**, **Excluir** (confirmação na tela) e **Cancelar** sem salvar. Registros cifrados com a chave derivada da senha, como as conversas salvas.
- Anexo **simulado**: a usuária pode escolher uma imagem ou áudio; só nome e tamanho aparecem, e o arquivo é descartado sem ir ao servidor.
- Exportação: **Exportar (demonstração)** mostra antes o aviso de que um arquivo baixado pode ficar no aparelho e ser visto, e de que a exportação não garante valor jurídico; depois exibe uma prévia na tela, sem criar arquivo. O PDF protegido (E7-US4) fica para a persistência real.

**Implementação e evidências locais (02/11/2026):**

- Contexto `accounts`: `GET/POST /api/account/journal` e `PUT/DELETE /api/account/journal/{id}`. `AccountService` valida data (ISO, não futura), hora e descrição, cifra data, hora e descrição de cada registro com AES-GCM (dados associados `conta:journal:id`), limita a 200 registros, ordena do mais recente para o mais antigo e apaga o diário com a conta.
- Frontend `features/journal/JournalArea`: aviso de privacidade no formulário antes de salvar (“Antes de salvar: … Não escreva dados reais. O Aurora não garante segurança se o aparelho for monitorado.”), contador de caracteres, anexo simulado com **Remover anexo**, mensagens “Registro salvo.”, “Registro atualizado.”, “Registro excluído.” e “Nada foi salvo.”; falhas informam que nada foi salvo ou apagado. A exportação fica desativada sem registros.
- Limites: sem anexos reais (validação, remoção de metadados como localização da foto e armazenamento seguro pendentes), sem PDF; dados somem quando o backend reinicia; não há proteção contra quem acessa o aparelho com a sessão aberta.

**Validações locais L-04 (02/11/2026):**

- [x] Backend: `pytest` — 151 testes passaram (12 novos: criar, editar, listar em ordem e excluir; cifra em repouso de data e texto; data futura, formato inválido, data inexistente, hora inválida, descrição vazia ou longa; edição de registro inexistente; diário apagado com a conta; fluxo HTTP `201/200/204/401/404/422`); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless: exportação desativada sem registros; **Cancelar** mostrou “Nada foi salvo.”; formulário com foco no título e aviso de privacidade; descrição vazia → erro; anexo simulado mostrou “anexo-teste.png (2 KB)… não foi enviado nem será guardado” e nenhuma requisição levou o arquivo; criar, editar e criar um segundo registro (lista do mais recente ao mais antigo); exportação mostrou o aviso e depois a prévia com 2 registros, sem nenhum download; exclusão com confirmação; 320 px sem overflow.
- [x] Teste local visto e aprovado pela usuária em 02/11/2026 (demonstração em janela do navegador).
- [ ] Revisões de segurança, privacidade e jurídica (inclusive riscos de exportação) e aprovação do time de produto.
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes.

**Skills:** [Persistência, criptografia e diário seguro](../../skills/persistencia-criptografia-diario-seguro.md), [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md), [Segurança de aplicação e modelagem de ameaças](../../skills/seguranca-aplicacao-modelagem-ameacas.md), [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md), [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md), [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md).

### L-05 — Guia/plano de segurança demonstrativo

**Prioridade:** jornada futura
**Estado:** Desenvolvimento concluído localmente — implementação e validações locais registradas; aguardam teste visto pela usuária, commit, publicação, validação humana na AWS, conteúdo aprovado por especialistas e aprovação do time de produto.
**Dependências:** J-00 (modo de acesso, conteúdo e regras de salvamento aprovados); L-01 somente se o escopo aprovado exigir conta.

**Escopo:** demonstrar conteúdo informativo, contatos e anotações opcionais conforme a jornada validada. A interface não presume que a usuária deve deixar o relacionamento ou a residência e não substitui atendimento especializado.

**Critérios de aceite:** uso é voluntário; saída sem salvar está disponível; conteúdos e sugestões têm aprovação de domínio; qualquer salvamento aparece como mock; não há ação automática de contato ou compartilhamento.

**Decisões da usuária (02/11/2026):**

- Guia com três seções de títulos neutros (“Pensar na sua segurança”, “Documentos e itens importantes”, “Pessoas e serviços de apoio”), todas com “Conteúdo em preparação — demonstração…”; o único conteúdo real são os canais 190/180/192/188. Aviso: “Este guia é opcional e informativo. Ele não presume que você deva sair de casa ou do relacionamento e não substitui atendimento especializado. Você decide o que usar.”
- Plano pessoal com contatos de confiança (até 5, nome ou apelido e telefone; o telefone só vira ligação se a usuária tocar) e anotações (até 4.000 caracteres).
- Acesso pela área logada (seção **Guia de segurança** em **Minha conta**), cifrado com a chave da senha; **Salvar plano** e **Sair sem salvar**; aviso de privacidade antes de salvar.
- Oferta pela conversa (E8-US4) com a frase de teste exata “Quero pensar na minha segurança”: a resposta traz um convite opcional com **Abrir guia de segurança**.

**Implementação e evidências locais (02/11/2026):**

- Contexto `learning`: `GET /api/learning/safety-guide` (`SafetyGuideService`, porta `SafetyGuide`) com as seções-placeholder.
- Contexto `accounts`: `GET/PUT /api/account/safety-plan`; contatos e anotações cifrados com AES-GCM como um único registro, validados (até 5 contatos, telefone com 8 a 20 caracteres e pelo menos 8 dígitos, anotações até 4.000) e apagados com a conta.
- Contexto `conversation`: `ContentOfferService` (porta `ContentOfferProvider`) consultado depois da triagem e do limite de escopo. Com a frase de teste, a API devolve `offer: "safety_guide"` sem consultar fontes nem gerar texto (`knowledge_status: null`, `reply: null`). Frases de risco continuam abrindo o modal do C-03, sem oferta.
- Frontend: `SafetyGuide` (guia, canais, plano em modo leitura com links `tel:` e modo edição) reutilizado em **Minha conta** e no `SafetyGuidePanel` da conversa; sem sessão, o painel pede login ali mesmo e a conversa continua preservada. O cliente valida o campo `offer` em runtime.
- Limites: nenhum conteúdo de orientação de segurança foi escrito; a oferta só reage à frase de teste; o Aurora não envia mensagens nem compartilha o plano.

**Validações locais L-05 (02/11/2026):**

- [x] Backend: `pytest` — 166 testes passaram (15 novos: guia só com placeholders, plano vazio/salvo/lido, cifra em repouso, validação de contatos e anotações, plano apagado com a conta, oferta pela frase exata e normalizada, sem oferta para outras frases, handler sem consultar fontes, fluxo HTTP de oferta, guia e plano com `200/401/422`); Ruff check e formatação passaram.
- [x] Frontend: `npm run check` e `npm run build` passaram.
- [x] Navegador headless: “Quero pensar na minha segurança” trouxe o convite com **Abrir guia de segurança**; o painel pediu login dentro da conversa; o guia mostrou o aviso de não presunção, os três placeholders e os canais; **Sair sem salvar** mostrou “Nada foi salvo.” e manteve o plano vazio; telefone inválido mostrou erro; com dados válidos, “Plano salvo.” e o contato virou link `tel:81999990000` sem nenhuma ligação automática; **← Voltar à conversa** manteve as 2 mensagens; o mesmo plano apareceu em **Minha conta**; 320 px sem overflow.
- [ ] Teste visto pela usuária em janela do navegador.
- [ ] Conteúdo do guia e critérios de oferta aprovados por especialistas; aprovação do time de produto.
- [ ] Commit, reconstrução Docker, publicação e validação humana em AWS — pendentes.

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
