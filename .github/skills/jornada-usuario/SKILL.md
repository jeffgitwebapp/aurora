---
name: jornada-usuario
description: "Use when creating or revising the Aurora user journey, screen navigation, usability requirements, screen-by-screen behavior, labels, messages, fields, user return/resume/exit flows, or functional prototypes based on the project's docs, wireframe, and frontend features."
argument-hint: "Describe the user profile or journey to document"
---

# Jornada de Usuário do Aurora

## Objetivo

Produzir ou revisar documentação funcional da jornada de uma pessoa usuária do
Aurora, descrevendo telas, ações e navegação em linguagem clara para produto,
engenharia e pessoas usuárias. O artefato padrão é
`docs/jornada-usuario/jornada-do-usuario.md`.

Esta definição operacional complementa a especificação de competência em
[`skills/jornada-usuario.md`](../../../skills/jornada-usuario.md), que é o
detalhamento canônico associado ao índice `skills/lista_skills.md`.

Esta skill trata de usabilidade e requisitos observáveis. Não implementa
funcionalidades nem escolhe tecnologia, arquitetura, cores, fontes, dimensões
ou animações. Para a linguagem visual, consulte o wireframe existente como
referência, sem confundir estilo com comportamento.

## Quando usar

- Criar ou atualizar a jornada da usuária vítima no Aurora.
- Descrever início, navegação independente, fluxos com dependências,
  continuação, retorno, pausa e encerramento.
- Especificar o que a pessoa clica, digita, vê, ouve ou pode escolher em cada
  etapa.
- Identificar decisões ainda ausentes nas especificações e registrar propostas
  para validação.

## Referências a consultar

1. Leia, quando disponíveis:
   - `docs/requisitos-aurora.md`;
   - `docs/backlog-aurora.md`;
   - `docs/Requisitos Aurora.pdf`;
   - `docs/Solução Tecnológica para Vítimas de Abuso.pdf`;
   - `docs/arquitetura_operacionalizada_aurora.md`;
   - `docs/aurora-criacao-projeto.md`.
2. Consulte `src/frontend/src/wireframe/Aurora — Wireframe.html` para
   identificar as telas, nomes, mensagens, campos, botões e regras que o
   wireframe realmente apresenta. Se o arquivo for empacotado, use a página
   renderizada/acessível no browser para ler as telas; não presuma que o HTML
   bruto contém o texto visível.
3. Consulte as features existentes em `src/frontend/src/features/` e a
   navegação em `src/frontend/src/app/` para separar comportamento atual de
   comportamento futuro.
4. Se um PDF ou recurso não puder ser lido, registre essa limitação e use
   somente informações confirmadas em outras fontes. Não alegue que revisou
   conteúdo não acessível.

## Procedimento

1. Delimite o perfil e o escopo. Para o documento principal do Aurora, priorize
   a pessoa vítima/usuária final; não misture fluxos administrativos, salvo se
   solicitado.
2. Separe claramente:
   - requisitos documentados;
   - conteúdo ou navegação presente no wireframe;
   - comportamento observado no frontend já implementado;
   - lacunas e propostas ainda não aprovadas.
3. Identifique primeiro as ações independentes, disponíveis após acessar o
   produto sem exigir que outra etapa do fluxo tenha sido concluída. Ordene-as
   por prioridade, colocando segurança e emergência antes dos caminhos
   informativos. Depois documente os percursos com pré-condições e
   dependências.
4. Para cada tela/etapa, descreva:
   - objetivo e condição de entrada;
   - elementos interativos pelo nome visível;
   - onde clicar, o que digitar/selecionar e se o campo é obrigatório;
   - mensagem ou estado que aparece depois da ação;
   - destinos possíveis, retorno e preservação ou descarte do que foi
     preenchido;
   - alternativas relevantes: vazio, cancelamento, sem resultado, erro,
     indisponibilidade, ausência de fonte e situação de risco.
5. Reproduza literalmente rótulos e mensagens existentes nas especificações ou
   wireframe, mantendo acentos e pontuação. Identifique placeholders como
   exemplo, não como texto definitivo.
6. Quando faltar uma decisão necessária, use **GAP** para explicar o que não
   está definido e **SUGESTÃO — validar** para a proposta. Não apresente
   conteúdo inventado como requisito aprovado.
7. Preserve os limites de produto: informar e oferecer opções; não diagnosticar,
   fazer psicoterapia, dar parecer jurídico individualizado, pressionar a
   usuária ou agir por ela.
8. Inclua um diagrama simples do percurso quando ajudar a explicar ramificações.
   O diagrama deve refletir as dependências descritas, não criar novas regras.
9. Termine o documento como uma revisão pendente e peça validação explícita ao
   usuário usando a ferramenta de elicitação disponível. Pergunte se aprova ou
   deseja corrigir os fluxos, textos e sugestões antes de tratar a jornada como
   validada.

## Regras para o conteúdo

- Fale com respeito, sem culpabilização e em linguagem simples.
- Priorize a segurança imediata; a Saída Rápida e os canais de emergência não
  dependem de concluir cadastro, relato, questionário ou conversa.
- Não afirme que fechar uma página apaga rastros fora do controle do produto.
  Especifique apenas o que a aplicação promete e ressalve limites quando
  necessário.
- Diferencie sessão anônima volátil de histórico persistente de conta. Não
  presuma que uma sessão anônima pode ser retomada após fechar o navegador.
- Não invente opções de questionário, validações de senha, destinos de Quick
  Exit, mensagens de erro, critérios de triagem ou ações para botões quando as
  fontes não os definem.
- Requisitos de fases futuras podem ser registrados como jornadas futuras, com
  dependências e lacunas, sem tratá-los como telas já existentes.
- O documento não substitui revisão humana de profissionais de psicologia,
  direito, proteção às mulheres, privacidade ou acessibilidade.

## Estrutura recomendada para `docs/jornada-usuario/jornada-do-usuario.md`

1. Objetivo, público, escopo e legenda de status.
2. Princípios de experiência e limites éticos.
3. Ações independentes priorizadas.
4. Mapa geral da jornada e ramificações.
5. Etapas detalhadas por tela, com ações, textos, estados, retorno e
   encerramento.
6. Jornadas opcionais/logadas e funcionalidades futuras, se aplicáveis.
7. Gaps e sugestões aguardando validação.
8. Rastreabilidade para requisito/história/wireframe.
9. Status de revisão e pedido explícito de validação.
