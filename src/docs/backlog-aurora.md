# Backlog — Plataforma Aurora

> Plataforma de psicoeducação e informação (PWA + LLM com RAG sobre literatura científica e jurídica) para ajudar mulheres a reconhecerem a violência psicológica, compreenderem seus direitos e encontrarem a rede de proteção adequada.  
> A plataforma opera em dois modos: **Anônimo** (acesso imediato, sem cadastro, sem rastros) e **Área Logada** (perfil persistente, histórico e módulos de psicoeducação).

---

## Épicos

| # | Épico | Descrição |
|---|-------|-----------|
| E1 | Acesso Seguro e Camuflagem | PWA sem instalação, Quick Exit, Dummy PIN e sessão anônima sem rastros |
| E2 | Cadastro e Autenticação | Conta por apelido/senha, migração de sessão anônima, deleção de dados |
| E3 | Chatbot de Psicoeducação e Informação (LLM + RAG) | Conversa livre ancorada em literatura citável para reconhecimento da violência |
| E4 | Reconhecimento e Triagem de Violência Psicológica | Questionário validado para identificar sinais de abuso e sugerir próximos passos |
| E5 | Orientação para Órgãos Públicos | Indicação dinâmica de delegacias, CRAM, CAPS e Ligue 180 com endereço e contato |
| E6 | Módulos de Psicoeducação | Conteúdo em áudio/vídeo sobre violência psicológica, ciclo do abuso e direitos legais |
| E7 | Diário e Registro de Incidentes | Registro criptografado de episódios com exportação como evidência jurídica |
| E8 | Informações sobre Segurança e Saída | Guia informativo para planejar saída segura, contatos de emergência pessoais |
| E9 | Acessibilidade e Inclusão | Linguagem simples, text-to-speech, WCAG 2.1, desempenho em dispositivos básicos |
| E10 | Integração com Ecossistema Externo | Encaminhamento para Meu SUS Digital, Projeto Justiceiras e base de órgãos públicos |
| E11 | Painel Administrativo | Gestão de conteúdo, métricas anonimizadas e configuração de diretrizes do LLM |
| E12 | Segurança, Privacidade e LGPD | Criptografia, deleção automática, conformidade LGPD e pentest pré-lançamento |
| E13 | Base de Conhecimento Citável e Guardrails | Curadoria da base RAG, rastreabilidade de fontes, versionamento e limites éticos do LLM |

---

## Legenda de Modos

- 🔓 **Anônimo** — disponível sem cadastro
- 🔐 **Logado** — requer conta ativa
- 🔓🔐 **Ambos** — disponível nos dois modos

---

## ÉPICO 1 — Acesso Seguro e Camuflagem

*Garantir que a vítima acesse a plataforma sem deixar rastros e possa ocultá-la rapidamente.*

| ID | User Story | Modo |
|----|-----------|------|
| E1-US1 | Como vítima, quero acessar a plataforma pelo navegador em modo incógnito, sem precisar instalar nenhum app, para não deixar rastros no celular. | 🔓🔐 |
| E1-US2 | Como vítima, quero que a plataforma pareça visualmente um site de notícias ou blog neutro para qualquer pessoa que a veja por cima do meu ombro. | 🔓🔐 |
| E1-US3 | Como vítima, quero pressionar um botão de "Saída Rápida" (Quick Exit) visível em todas as telas para fechar o site imediatamente e ser redirecionada para uma página inofensiva. | 🔓🔐 |
| E1-US4 | Como vítima, quero configurar um PIN de fachada (Dummy PIN) para que, se eu for coagida a abrir a plataforma, ela exiba uma interface falsa e oculte todo o meu histórico. | 🔐 |
| E1-US5 | Como vítima, quero que minhas sessões no modo anônimo não sejam armazenadas após o fechamento do navegador, garantindo que nenhuma informação fique salva no dispositivo. | 🔓 |
| E1-US6 | Como vítima, quero que a plataforma funcione mesmo com conexão de internet instável ou lenta, pois posso estar em área remota. | 🔓🔐 |

---

## ÉPICO 2 — Cadastro e Autenticação (Área Logada)

*Permitir que a vítima crie uma conta segura para persistir histórico e plano de segurança.*

| ID | User Story | Modo |
|----|-----------|------|
| E2-US1 | Como vítima, quero criar uma conta usando apenas um apelido e senha, sem precisar informar e-mail ou número de telefone real, para preservar minha identidade. | 🔐 |
| E2-US2 | Como vítima, quero fazer login com minha senha de forma segura e rápida. | 🔐 |
| E2-US3 | Como vítima, quero poder migrar minha sessão anônima atual para uma conta, salvando o histórico da conversa sem perder o contexto. | 🔐 |
| E2-US4 | Como vítima, quero poder deletar permanentemente minha conta e todos os meus dados com um único clique, para o caso de precisar apagar tudo rapidamente. | 🔐 |
| E2-US5 | Como vítima, quero que meus dados na conta sejam criptografados em repouso, de forma que ninguém além de mim possa lê-los. | 🔐 |

---

## ÉPICO 3 — Chatbot de Psicoeducação e Informação (LLM + RAG)

*O núcleo da plataforma: conversação livre com IA ancorada em literatura científica e jurídica para ajudar a mulher a reconhecer a violência e encontrar a rede de proteção.*

| ID | User Story | Modo |
|----|-----------|------|
| E3-US1 | Como mulher que não sabe se o que vive é violência, quero iniciar uma conversa com o chatbot sem precisar de cadastro para receber informações e orientação a qualquer hora. | 🔓🔐 |
| E3-US2 | Como usuária, quero que o chatbot responda com linguagem acessível, sem julgamentos e sem me pressionar a tomar decisões, respeitando meu ritmo. | 🔓🔐 |
| E3-US3 | Como usuária, quero que o chatbot explique o que é violência psicológica — com exemplos concretos baseados em literatura citável — para me ajudar a entender se o que vivo se encaixa nesse padrão. | 🔓🔐 |
| E3-US4 | Como usuária, quero que o chatbot baseie suas respostas em fontes científicas e jurídicas (ex: Lei Maria da Penha, DSM, estudos de prevalência), citando-as quando pertinente, para que eu confie na informação. | 🔓🔐 |
| E3-US5 | Como usuária, quero que o chatbot lembre o contexto da conversa durante toda a sessão para não precisar repetir informações a cada mensagem. | 🔓🔐 |
| E3-US6 | Como usuária logada, quero que o chatbot lembre o histórico de conversas anteriores para continuar de onde paramos. | 🔐 |
| E3-US7 | Como usuária, quero que o chatbot deixe claro desde o início que é uma ferramenta de informação e psicoeducação — não um psicólogo, não faz diagnóstico e não substitui atendimento profissional. | 🔓🔐 |
| E3-US8 | Como usuária, quero que o chatbot, ao identificar sinais de risco imediato na conversa, encaminhe imediatamente para o canal humano de emergência (190, 192 ou CVV 188) — sem tentar "resolver" a crise internamente. | 🔓🔐 |
| E3-US9 | Como usuária, quero que as respostas do chatbot que trazem informações sobre violência ou direitos indiquem a fonte em que se baseiam (ex: Lei Maria da Penha, art. X; estudo Y), para que eu possa confiar no que leio. | 🔓🔐 |
| E3-US10 | Como usuária, quero chegar à informação ou ao encaminhamento útil em no máximo 3 interações, para que o sistema não se torne cansativo em um momento de vulnerabilidade. | 🔓🔐 |

---

## ÉPICO 4 — Reconhecimento e Triagem de Violência Psicológica

*Ajudar a usuária a identificar se o que vive pode ser caracterizado como violência psicológica e determinar o encaminhamento mais adequado a partir de três variáveis: urgência, tipo de necessidade e localização.*

| ID | User Story | Modo |
|----|-----------|------|
| E4-US1 | Como mulher que duvida se o que vive é violência, quero responder um questionário guiado — baseado em instrumentos validados como o violentômetro — para verificar se meu relacionamento tem sinais de abuso psicológico. | 🔓🔐 |
| E4-US2 | Como usuária, quero que ao final do questionário eu receba uma explicação clara sobre os padrões identificados, sem diagnóstico, sem alarmismo e com indicação de o que fazer a seguir. | 🔓🔐 |
| E4-US3 | Como usuária, quero que o resultado da triagem leve em conta a urgência da minha situação (risco agudo, risco contínuo ou sem risco imediato) para sugerir os próximos passos adequados a cada caso. | 🔓🔐 |
| E4-US4 | Como usuária, quero que a triagem pergunte que tipo de ajuda preciso (denúncia, orientação jurídica, apoio psicológico, apoio entre pares) para que o encaminhamento seja preciso e não genérico. | 🔓🔐 |
| E4-US5 | Como usuária, quero que a triagem considere minha localização (estado/cidade) para indicar os serviços disponíveis na minha região — ex: Chame a Frida se estou em MG, Conecta Recife se estou em Recife. | 🔓🔐 |
| E4-US6 | Como usuária em situação de risco agudo identificada durante a triagem, quero ser encaminhada imediatamente ao canal de emergência correspondente (190, 192 ou CVV 188) sem precisar concluir o questionário. | 🔓🔐 |
| E4-US7 | Como usuária logada, quero que meu histórico de triagens fique salvo para acompanhar a evolução da minha percepção sobre a situação ao longo do tempo. | 🔐 |

---

## ÉPICO 5 — Encaminhamento para a Rede de Proteção

*Direcionar a usuária para o serviço mais adequado à sua situação, seguindo a lógica e a hierarquia definidas na Matriz de Encaminhamento Aurora.*

| ID | User Story | Modo |
|----|-----------|------|
| E5-US1 | Como usuária em risco de morte iminente ou agressão em curso, quero ser encaminhada imediatamente ao 190 (Polícia Militar) e ao 192 (SAMU) se houver lesão física. | 🔓🔐 |
| E5-US2 | Como usuária com sinais de ideação suicida ou crise emocional aguda, quero ser encaminhada ao CVV (188) e, se houver risco de ato iminente, ao 192. | 🔓🔐 |
| E5-US3 | Como usuária que decidiu denunciar formalmente, quero ser indicada à DEAM da minha cidade com endereço, telefone e horário — ou ao Chame a Frida se estiver em Minas Gerais. | 🔓🔐 |
| E5-US4 | Como usuária que quer orientação jurídica gratuita, quero que o chatbot siga a hierarquia: Defensoria Pública (NUDEM) → CRAM ou Casa da Mulher Brasileira → OAB (plantão) → Projeto Justiceiras. | 🔓🔐 |
| E5-US5 | Como usuária que precisa de apoio psicológico estruturado, quero ser encaminhada ao CAPS da minha cidade ou ao teleatendimento do Meu SUS Digital. | 🔓🔐 |
| E5-US6 | Como usuária em Recife, quero que o Aurora me indique o Conecta Recife como porta local de acesso a serviços municipais de saúde e proteção. | 🔓🔐 |
| E5-US7 | Como usuária que quer denúncia anônima ou orientação imediata sem registro, quero ser direcionada ao Ligue 180 com o botão de discagem rápida. | 🔓🔐 |
| E5-US8 | Como usuária, quero que o chatbot me apresente múltiplas portas priorizadas — nunca apenas uma — para que eu escolha o caminho que me sinto pronta para dar. | 🔓🔐 |
| E5-US9 | Como usuária, quero receber orientação sobre como registrar um boletim de ocorrência, o que levar para a delegacia e o que esperar do processo de medida protetiva. | 🔓🔐 |
| E5-US10 | Como usuária, quero que o Aurora nunca transmita meus dados pessoais ao serviço indicado — ele me dá o contato e a decisão de acionar é minha. | 🔓🔐 |

---

## ÉPICO 6 — Módulos de Psicoeducação

*Oferecer conteúdo informativo estruturado sobre violência psicológica, direitos e rede de proteção — sem exercer psicoterapia.*

| ID | User Story | Modo |
|----|-----------|------|
| E6-US1 | Como usuária logada, quero acessar módulos de conteúdo em formato de áudio e vídeo curtos sobre temas como: o que é violência psicológica, ciclo do abuso, gaslighting, isolamento como controle, e impactos na saúde mental — para aprender no meu próprio ritmo. | 🔐 |
| E6-US2 | Como usuária logada, quero acessar módulos sobre meus direitos legais: o que diz a Lei Maria da Penha, quais medidas protetivas existem, como funciona um boletim de ocorrência. | 🔐 |
| E6-US3 | Como usuária logada, quero que meu progresso nos módulos seja salvo para continuar de onde parei. | 🔐 |
| E6-US4 | Como usuária logada, quero receber sugestões personalizadas de módulos com base no que compartilhei no chat (ex: se mencionei controle financeiro, sugerir módulo sobre violência patrimonial). | 🔐 |
| E6-US5 | Como usuária logada, quero receber uma mensagem de reconhecimento ao completar um módulo, reforçando minha agência e autonomia. | 🔐 |

---

## ÉPICO 7 — Diário e Registro de Incidentes

*Permitir que a vítima registre e documente episódios de abuso com segurança.*

| ID | User Story | Modo |
|----|-----------|------|
| E7-US1 | Como vítima logada, quero escrever entradas no diário descrevendo episódios de violência com data, hora e descrição para manter um registro pessoal. | 🔐 |
| E7-US2 | Como vítima logada, quero anexar fotos ou áudios ao diário como evidência de agressões. | 🔐 |
| E7-US3 | Como vítima logada, quero que os registros do diário sejam armazenados de forma criptografada e jamais visíveis para terceiros. | 🔐 |
| E7-US4 | Como vítima logada, quero exportar meu diário em formato seguro (PDF criptografado) para apresentar como prova em um processo judicial se necessário. | 🔐 |

---

## ÉPICO 8 — Informações sobre Segurança e Saída

*Fornecer à usuária informações estruturadas sobre como pensar e planejar uma saída segura — sem que o chatbot tome a decisão por ela ou simule acompanhamento terapêutico.*

| ID | User Story | Modo |
|----|-----------|------|
| E8-US1 | Como usuária logada, quero acessar um guia informativo — baseado em referências como o Manual de Fuga do PenhaS e protocolos do myPlan — com os passos e considerações para planejar uma saída segura. | 🔐 |
| E8-US2 | Como usuária logada, quero registrar contatos de emergência pessoais (pessoas de confiança) para ter acesso rápido a eles quando precisar. | 🔐 |
| E8-US3 | Como usuária logada, quero fazer anotações no meu guia pessoal de saída para adaptar as informações gerais à minha realidade específica. | 🔐 |
| E8-US4 | Como usuária logada, quero que o chatbot me ofereça ativamente o conteúdo sobre segurança quando o contexto da conversa indicar que pode ser relevante — sem forçar ou pressionar. | 🔐 |

---

## ÉPICO 9 — Acessibilidade e Inclusão

*Garantir que a plataforma seja acessível para mulheres com diferentes níveis de letramento digital e educacional.*

| ID | User Story | Modo |
|----|-----------|------|
| E9-US1 | Como vítima com baixa escolaridade, quero que o chatbot use linguagem simples, sem jargões clínicos ou jurídicos. | 🔓🔐 |
| E9-US2 | Como vítima com dificuldade de leitura, quero a opção de ouvir as respostas do chatbot em áudio (text-to-speech). | 🔓🔐 |
| E9-US3 | Como vítima, quero que a interface tenha botões grandes, ícones claros e navegação simples para reduzir a carga cognitiva em momentos de estresse. | 🔓🔐 |
| E9-US4 | Como vítima com deficiência visual, quero que a plataforma seja compatível com leitores de tela (acessibilidade WCAG 2.1). | 🔓🔐 |
| E9-US5 | Como vítima com celular de entrada (Android básico), quero que a plataforma carregue rapidamente mesmo com hardware limitado. | 🔓🔐 |

---

## ÉPICO 10 — Integração com Ecossistema Externo

*Conectar a plataforma a serviços já existentes no Brasil.*

| ID | User Story | Modo |
|----|-----------|------|
| E10-US1 | Como vítima, quero ser encaminhada para agendamento de teleconsulta no Meu SUS Digital quando o chatbot avaliar que preciso de acompanhamento profissional. | 🔓🔐 |
| E10-US2 | Como vítima, quero ser direcionada ao Projeto Justiceiras para suporte jurídico gratuito quando necessário. | 🔓🔐 |
| E10-US3 | Como administrador, quero integrar a base de dados de órgãos públicos com fontes governamentais (ex: API do Gov.br) para manter os endereços sempre atualizados. | — |

---

## ÉPICO 11 — Painel Administrativo

*Ferramentas de gestão de conteúdo, monitoramento e operação da plataforma.*

| ID | User Story | Modo |
|----|-----------|------|
| E11-US1 | Como administrador, quero visualizar métricas de uso anonimizadas (número de sessões, temas mais abordados, nível de risco médio) para entender o impacto da plataforma. | — |
| E11-US2 | Como administrador, quero cadastrar, editar e publicar módulos de psicoeducação (áudios, vídeos, textos) sem precisar de intervenção técnica. | — |
| E11-US3 | Como administrador, quero manter e atualizar o catálogo de serviços da Matriz de Encaminhamento (DEAM, CRAM, CAPS, Defensoria, Casa da Mulher Brasileira, serviços locais) por estado e cidade. | — |
| E11-US4 | Como administrador, quero configurar os prompts e diretrizes éticas do LLM — incluindo os limites do que o chatbot pode e não pode dizer — para garantir que ele opere estritamente no campo da psicoeducação e não simule atendimento clínico. | — |
| E11-US5 | Como administrador, quero receber alertas automáticos se o sistema detectar volume anormal de sessões de alto risco (ex: aumento repentino). | — |

---

## ÉPICO 13 — Base de Conhecimento Citável e Guardrails

*Construir, versionar e manter a base de conhecimento RAG que fundamenta as respostas do chatbot, garantindo rastreabilidade, precisão e conformidade ética.*

| ID | User Story | Modo |
|----|-----------|------|
| E13-US1 | Como equipe do projeto, precisamos curar a base de conhecimento inicial com fontes validadas — Lei Maria da Penha, DSM, literatura científica sobre violência psicológica, cartilhas do NUDEM, materiais do Ministério Público — para que o RAG responda com precisão. | — |
| E13-US2 | Como equipe do projeto, precisamos versionar a base de conhecimento para que toda alteração de fonte seja rastreável e auditável. | — |
| E13-US3 | Como equipe do projeto, precisamos implementar guardrails que recusem e reenquadrem respostas fora do escopo informacional — diagnóstico, psicoterapia, aconselhamento jurídico individualizado — antes que cheguem à usuária. | — |
| E13-US4 | Como equipe do projeto, precisamos garantir que ≥ 90% das respostas do chatbot tenham fonte rastreável e ≤ 5% fujam do escopo informacional em amostra avaliada (conforme meta do TAP). | — |
| E13-US5 | Como administrador, quero revisar e atualizar a base de conhecimento periodicamente com novas fontes ou legislações sem intervenção de engenharia. | — |
| E13-US6 | Como equipe do projeto, precisamos realizar revisão da base por especialista de domínio (psicólogo e defensor/advogado parceiro) antes de cada release, conforme critério de validação da Matriz de Encaminhamento. | — |

---

## ÉPICO 12 — Segurança, Privacidade e LGPD

*Garantir conformidade legal e proteção real dos dados das usuárias.*

| ID | User Story | Modo |
|----|-----------|------|
| E12-US1 | Como vítima, quero ser informada de forma clara sobre quais dados são coletados, como são usados e por quanto tempo ficam armazenados, antes de qualquer cadastro. | 🔓🔐 |
| E12-US2 | Como vítima no modo anônimo, quero que nenhum dado identificável (IP, cookies persistentes) seja retido após o encerramento da sessão. | 🔓 |
| E12-US3 | Como vítima logada, quero solicitar a exclusão completa dos meus dados a qualquer momento (direito ao esquecimento — LGPD Art. 18). | 🔐 |
| E12-US4 | Como plataforma, precisamos garantir que todos os dados em trânsito utilizem criptografia TLS e que dados em repouso sejam criptografados. | — |
| E12-US5 | Como plataforma, precisamos de política de deleção automática de logs de conversas do modo anônimo após o fechamento da sessão. | — |
| E12-US6 | Como plataforma, precisamos realizar teste de penetração (pentest) antes do lançamento para identificar vulnerabilidades. | — |

---

## Resumo de Épicos por Prioridade e Marcos do TAP

| Prioridade | Marco TAP | Épico | Justificativa |
|---|---|---|---|
| 🔴 MVP | M1 — Jul/2026 | E13 — Base de Conhecimento e Guardrails | Fundação do RAG; sem ela o chatbot não tem base citável |
| 🔴 MVP | M2 — Ago/2026 | E12 — Segurança e LGPD | Arquitetura de guardrails e conformidade antes do MVP |
| 🔴 MVP | M3 — Set-Out/2026 | E1 — Acesso Seguro e Camuflagem | Segurança física da vítima é pré-requisito |
| 🔴 MVP | M3 — Set-Out/2026 | E3 — Chatbot de Psicoeducação (LLM + RAG) | Núcleo do produto; fluxo completo demonstrável no M3 |
| 🔴 MVP | M3 — Set-Out/2026 | E4 — Reconhecimento e Triagem | Diferencial central: nomear a violência e triar por urgência/necessidade/localização |
| 🔴 MVP | M3 — Set-Out/2026 | E5 — Encaminhamento para a Rede de Proteção | Diferencial estratégico; base para os 95% de acerto da Matriz |
| 🟡 V1 | M4 — Nov/2026 | E9 — Acessibilidade | Inclusão da base de usuárias; validação com intermediários (≥80% aprovação) |
| 🟡 V1 | M4 — Nov/2026 | E11 — Painel Administrativo | Framework de avaliação e métricas do TAP |
| 🟡 V1 | M5 — Dez/2026 | E2 — Cadastro e Autenticação | Habilita a área logada |
| 🟡 V1 | M5 — Dez/2026 | E10 — Integrações Externas | Encaminhamentos para SUS, Justiceiras e base de serviços |
| 🟢 V2 | M6 — Dez/2026–Jan/2027 | E6 — Módulos de Psicoeducação | Aprofundamento; conteúdo estruturado por tema |
| 🟢 V2 | M6 — Dez/2026–Jan/2027 | E7 — Diário e Registro | Evidência jurídica; valor para usuárias recorrentes |
| 🟢 V2 | M6 — Dez/2026–Jan/2027 | E8 — Informações sobre Segurança e Saída | Autonomia informada; referência ao piloto controlado |
