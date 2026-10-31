# Índice de skills necessárias — Projeto Aurora

Este arquivo lista as skills necessárias para orientar a implementação do
Aurora por prompts. A especificação e o contexto de cada skill estão no arquivo
individual indicado na coluna **Especificação**.

Os grupos refletem as fases documentadas no backlog. A presença de uma skill
em um grupo não significa que toda a funcionalidade já esteja implementada.

## Base do MVP

| # | Skill necessária | Escopo resumido | Especificação |
|---|---|---|---|
| 1 | Análise de requisitos, backlog e rastreabilidade | Converter fontes e épicos em requisitos, entregas e critérios verificáveis. | [analise-requisitos-backlog-rastreabilidade.md](./analise-requisitos-backlog-rastreabilidade.md) |
| 2 | Domínio de violência psicológica e design informado por trauma | Orientar conteúdo e interações respeitosas, sem julgamento ou coerção. | [dominio-violencia-psicologica-design-informado-trauma.md](./dominio-violencia-psicologica-design-informado-trauma.md) |
| 3 | Arquitetura de software e integração ponta a ponta | Estruturar módulos, fronteiras e contratos evolutivos do sistema. | [arquitetura-software-integracao.md](./arquitetura-software-integracao.md) |
| 4 | Backend Python e APIs com FastAPI | Desenvolver APIs tipadas, modulares, resilientes e sem logs de relatos. | [backend-python-fastapi.md](./backend-python-fastapi.md) |
| 5 | Frontend React, TypeScript e experiência conversacional | Construir interface de chat e fluxos em memória com estados claros. | [frontend-react-typescript-chat.md](./frontend-react-typescript-chat.md) |
| 6 | PWA, privacidade de dispositivo e Saída Rápida | Projetar operação móvel/offline e saída rápida dentro dos limites reais do navegador. | [pwa-privacidade-dispositivo-saida-rapida.md](./pwa-privacidade-dispositivo-saida-rapida.md) |
| 7 | Acessibilidade, inclusão e linguagem simples | Atender WCAG, leitores de tela, baixa conectividade e letramento diverso. | [acessibilidade-inclusao-linguagem-simples.md](./acessibilidade-inclusao-linguagem-simples.md) |
| 8 | Engenharia de privacidade, LGPD e governança de dados | Minimizar, mapear e governar dados sensíveis nos modos anônimo e logado. | [privacidade-lgpd-governanca-dados.md](./privacidade-lgpd-governanca-dados.md) |
| 9 | Segurança de aplicação e modelagem de ameaças | Avaliar ameaças web, API, infraestrutura e dispositivo monitorado. | [seguranca-aplicacao-modelagem-ameacas.md](./seguranca-aplicacao-modelagem-ameacas.md) |
| 10 | Triagem determinística de risco agudo e avaliação de segurança | Detectar risco crítico com regras testáveis e precedência sobre IA generativa. | [triagem-risco-agudo-avaliacao-seguranca.md](./triagem-risco-agudo-avaliacao-seguranca.md) |
| 11 | Curadoria de conteúdo e engenharia de conhecimento RAG | Criar e versionar fontes citáveis e recuperação fundamentada. | [curadoria-conteudo-engenharia-conhecimento-rag.md](./curadoria-conteudo-engenharia-conhecimento-rag.md) |
| 12 | Integração de LLM e engenharia de prompts | Integrar provedores com streaming, segurança, limites e fallback. | [integracao-llm-engenharia-prompts.md](./integracao-llm-engenharia-prompts.md) |
| 13 | Guardrails, escopo ético e avaliação generativa | Bloquear saídas indevidas e avaliar grounding, citações e limites éticos. | [guardrails-escopo-etico-avaliacao-generativa.md](./guardrails-escopo-etico-avaliacao-generativa.md) |
| 14 | Catálogo de serviços e motor de encaminhamento | Manter opções locais atualizadas, completas e priorizadas por regra. | [catalogo-servicos-motor-encaminhamento.md](./catalogo-servicos-motor-encaminhamento.md) |
| 15 | Engenharia de qualidade, testes e fitness functions | Automatizar métricas e gates CA-01 a CA-05 com evidências reproduzíveis. | [engenharia-qualidade-testes-fitness-functions.md](./engenharia-qualidade-testes-fitness-functions.md) |
| 16 | DevOps, AWS, CI/CD e operação | Construir, publicar, implantar e operar com segurança e resiliência. | [devops-aws-cicd-operacao.md](./devops-aws-cicd-operacao.md) |

## Skill transversal

| # | Skill necessária | Escopo resumido | Especificação |
|---|---|---|---|
| 23 | Jornada do usuário e especificação de usabilidade | Descrever telas, ações, textos, dependências, retorno e gaps funcionais. | [jornada-usuario.md](./jornada-usuario.md) |

## Evolução — V1 e V2

| # | Fase | Skill necessária | Escopo resumido | Especificação |
|---|---|---|---|---|
| 17 | V1 | Autenticação, autorização e área logada pseudonimizada | Contas opcionais, sessões seguras, migração voluntária e exclusão de dados. | [autenticacao-autorizacao-area-logada.md](./autenticacao-autorizacao-area-logada.md) |
| 18 | V1 | Persistência, criptografia e diário seguro | Persistir e excluir dados sensíveis, anexos e exportações protegidas. | [persistencia-criptografia-diario-seguro.md](./persistencia-criptografia-diario-seguro.md) |
| 19 | V1 | Gestão de conteúdo e painel administrativo | Administrar catálogo, módulos, base RAG, versões e métricas privadas. | [gestao-conteudo-painel-administrativo.md](./gestao-conteudo-painel-administrativo.md) |
| 20 | V1 | Integrações e interoperabilidade externa | Integrar fontes/serviços sem expor relatos ou dados pessoais. | [integracoes-interoperabilidade-externa.md](./integracoes-interoperabilidade-externa.md) |
| 21 | V2 | Conteúdo multimídia e aprendizagem acessível | Oferecer módulos curtos com áudio, vídeo, transcrição e progresso. | [conteudo-multimidia-aprendizagem-acessivel.md](./conteudo-multimidia-aprendizagem-acessivel.md) |
| 22 | Transversal | Observabilidade com privacidade e engenharia de desempenho | Medir disponibilidade, latência e capacidade sem registrar relatos. | [observabilidade-privacidade-desempenho.md](./observabilidade-privacidade-desempenho.md) |

## Validação humana necessária

As skills de domínio técnico não substituem revisão de especialistas. Antes de
piloto com usuárias, validar conteúdo e comportamento com profissionais de
psicologia/saúde mental, direito/políticas públicas, rede de proteção,
privacidade/LGPD, segurança e acessibilidade. As métricas automatizadas devem
ser acompanhadas das evidências e revisões humanas definidas nos documentos do
projeto.

## Referências do inventário

- [`requisitos-aurora.md`](../docs/requisitos-aurora.md)
- [`backlog-aurora.md`](../docs/backlog-aurora.md)
- [`arquitetura_operacionalizada_aurora.md`](../docs/arquitetura_operacionalizada_aurora.md)
- [`aurora-criacao-projeto.md`](../docs/aurora-criacao-projeto.md)
- [`analise-comparativa-solucoes.md`](../docs/analise-comparativa-solucoes.md)
- [`aurora-arquitetura-4mais1.drawio`](../docs/aurora-arquitetura-4mais1.drawio)
- [`c4-aurora-mvp.drawio`](../docs/c4-aurora-mvp.drawio)
