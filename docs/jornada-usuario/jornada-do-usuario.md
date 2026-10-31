# Jornada do Usuário — Aurora

**Status:** rascunho para validação de produto e domínio
**Perfil priorizado:** mulher em situação de violência psicológica ou que
procura informação e apoio para compreender o que está vivendo
**Tipo de documento:** usabilidade e requisitos funcionais; não define
implementação técnica nem especificação visual

> **Atenção:** este documento organiza os comportamentos definidos e os
> comportamentos propostos. Tudo que estiver marcado como **SUGESTÃO — validar**
> ainda não é requisito aprovado. A jornada não deve ser tratada como validada
> até revisão do usuário e dos especialistas de domínio pertinentes.

## 1. Objetivo e escopo

Descrever por onde a usuária começa, quais ações pode fazer sem depender de
outras etapas, como percorre a conversa e os caminhos de emergência,
informação e encaminhamento, e o que acontece quando retorna, pausa ou encerra
o uso.

O documento foca a usuária final. Ações administrativas não fazem parte desta
jornada. Cadastro, diário, módulos e plano de segurança são registrados como
fluxos futuros porque aparecem no backlog, mas não estão detalhados como telas
completas nas especificações consultadas.

O Aurora é uma ferramenta de psicoeducação e informação. Não realiza
diagnóstico, psicoterapia, aconselhamento jurídico individualizado nem decide
ou age pela usuária. A escolha de procurar um serviço é sempre da própria
usuária.

### Legenda de origem

- **[REQUISITO]** — comportamento descrito em `requisitos-aurora.md` ou no
  backlog.
- **[WIREFRAME]** — rótulo, texto ou interação mostrada em
  `Aurora — Wireframe.html`.
- **[IMPLEMENTADO]** — comportamento observado nas features atuais do frontend.
- **[GAP]** — decisão necessária que as fontes não definem.
- **[SUGESTÃO — validar]** — proposta para preencher um gap; precisa de
  aprovação antes de ser considerada requisito.

## 2. Princípios que orientam todas as telas

1. **Segurança primeiro.** Acesso a emergência e Saída Rápida não devem
   depender de cadastro ou conclusão de outra etapa.
2. **Acesso anônimo.** A usuária deve poder iniciar sem fornecer nome,
   telefone, e-mail ou outro identificador.
3. **Autonomia.** Apresentar informação e opções sem instruir a usuária a
   denunciar, sair de casa ou tomar uma decisão específica.
4. **Linguagem simples e não julgadora.** A usuária não precisa conhecer
   termos técnicos nem usar uma descrição “correta”.
5. **Transparência sobre sessão.** No modo anônimo, a conversa é temporária e
   não pode ser retomada depois que a sessão for encerrada.
6. **Sem falsa promessa de segurança digital.** A aplicação pode descartar o
   conteúdo que mantém na sessão, mas não controla histórico, monitoramento ou
   registros mantidos pelo navegador, dispositivo, rede ou terceiros.
7. **Uma ação principal por etapa.** Manter as escolhas curtas e claras. A
   recomendação do wireframe indica áreas de toque de pelo menos 44 px e
   contraste mínimo de 4,5:1; o desenho visual detalhado continua sendo
   referência do próprio wireframe.

## 3. Ações independentes, priorizadas

Estas são ações que a usuária deve conseguir iniciar sem completar relato,
triagem ou cadastro. A ordem prioriza segurança.

| Prioridade | Ação independente | Onde começa | Ação da usuária | Resultado esperado | Origem |
|---|---|---|---|---|---|
| P0 | Sair rapidamente | Qualquer tela | Acionar **Saída rápida (Esc)** ou pressionar Esc | Abrir a página neutra definida para o produto e encerrar a sessão volátil, conforme o comportamento a validar | RF06, E1-US3, wireframe |
| P0 | Buscar ajuda por telefone | Início e telas de conversa; também há tela de risco agudo | Acionar o serviço desejado: Polícia Militar **190**, Central de Atendimento à Mulher **180**, SAMU **192** ou CVV **188** | O aparelho oferece a ação de ligação; o Aurora não liga pela usuária | Wireframe, E3-US8, E5-US1/2 |
| P1 | Iniciar com texto livre | Início | Digitar no campo **Escreva sua mensagem** e acionar **Enviar** | Abrir a conversa e encaminhar o texto como primeira mensagem | RF01, wireframe, implementação |
| P1 | Iniciar por uma sugestão | Início | Escolher uma das sugestões | Abrir a conversa e usar a frase selecionada para iniciar | Wireframe, implementação |
| P1 | Consultar privacidade | Início | Acionar **Privacidade** | Exibir explicação de dados e limites da sessão | Link previsto no wireframe; conteúdo/destino é lacuna |
| P1 | Ver contatos úteis | Início | Acionar **Contatos úteis** | Abrir os canais de contato disponíveis | Wireframe |

### 3.1 Tela inicial e começo anônimo

**Objetivo:** permitir que a usuária comece sem cadastro, escrevendo com as
próprias palavras ou escolhendo um ponto de partida.

**Elementos que o wireframe especifica:**

- Nome neutro no cabeçalho; o wireframe usa `Aurora` como rótulo de demonstração,
  mas também registra que o nome exibido à usuária deve ser neutro.
- Ação **Sair**.
- Título **Fale com a Aurora**.
- Campo rotulado **Escreva sua mensagem**, placeholder **Escreva o que
  quiser…**.
- Aviso **Sem cadastro. Nada fica salvo.**
- Ação **Enviar**.
- Sugestões:
  - **Quero entender o que estou sentindo**
  - **Tenho dúvidas sobre meus direitos**
  - **Onde encontrar apoio**
- Links **Privacidade** e **Contatos úteis**.
- Aviso **Tecla Esc fecha a página**.

**Regras de interação:**

1. Abrir o produto não deve exigir conta ou preenchimento de formulário.
2. Se a usuária enviar texto não vazio, a frase passa a ser a primeira mensagem
   da conversa; não deve ser necessário pressionar Enviar uma segunda vez.
3. Ao escolher uma sugestão, a frase escolhida inicia a conversa. A usuária
   poderá continuar com outras perguntas.
4. Campo vazio ou só com espaços não inicia uma conversa.
5. Não solicitar permissão de localização, não usar pop-up e não exibir
   notificações, conforme as regras do wireframe.

**Implementação observada:** o frontend atual permite enviar texto livre e
escolher sugestões para iniciar a conversa automaticamente. O aviso atual na
tela inicial diz **“Protótipo local · a conversa não é salva.”**; isso difere
do texto do wireframe **“Sem cadastro. Nada fica salvo.”** e precisa ser
consolidado antes da validação de produto.

### 3.2 Saída Rápida — disponibilidade independente

**Ação:** a usuária aciona **Saída rápida (Esc)** ou pressiona a tecla Esc em
qualquer tela.

**Resultado esperado no wireframe:** substituir a tela atual por uma página
neutra, sem exigir internet, descartar a sessão e substituir a entrada no
histórico de navegação. O alvo de latência documentado para a troca é p95 de
200 ms e p99 de 300 ms.

**[GAP]** O destino neutro exato ainda não foi escolhido. O wireframe usa
placeholders `[site neutro externo]` e `[conteúdo comum do site neutro]` e
registra que o destino deve ser definido pelo time.

**[SUGESTÃO — validar]** Definir uma página neutra estática, que não revele o
Aurora nem a ação de saída, e documentar claramente o que a aplicação descarta.
Não afirmar que a ação remove o histórico geral do navegador, dados do sistema
operacional, registros de rede ou monitoramento externo.

**[GAP]** Confirmar se a tecla Esc sempre executa a saída imediata mesmo quando
o foco está em um campo de texto ou quando um diálogo de confirmação estiver
aberto. O requisito de rapidez sugere que a saída não deve depender de
confirmação, mas essa regra não está descrita como comportamento final aprovado.

### 3.3 Acesso a emergência sem passar pelo fluxo de conversa

Na tela inicial, a usuária pode abrir **Contatos úteis** ou um link de
**Emergência** sempre visível nas telas de conversa. A seção de contatos
apresenta:

- **Polícia Militar — 190**
- **Central de Atendimento à Mulher — 180**
- **SAMU — 192**
- **CVV — 188**

**[WIREFRAME]** Os links usam os destinos de ligação `tel:190`, `tel:180`,
`tel:192` e `tel:188`. A usuária escolhe se e quando ligar; o Aurora não aciona
serviços por ela.

## 4. Mapa geral da jornada dependente

```mermaid
flowchart TD
    A[Acessar sem cadastro] --> B{Escolher como começar}
    B -->|Digitar relato| C[Conversa: enviar primeira mensagem]
    B -->|Escolher sugestão| C
    B -->|Contatos úteis| E[Escolher canal telefônico]
    B -->|Saída rápida ou Esc| X[Página neutra e fim da sessão]
    C --> D{Triagem de urgência}
    D -->|Risco agudo| R[Tela de risco agudo]
    R -->|Ligar se desejar| E
    R -->|Voltar à conversa| C
    D -->|Sem risco agudo detectado| I[Resposta informativa com fonte]
    I -->|Perguntar mais| C
    I -->|Precisa de ajuda local| L[Informar Cidade / UF opcional]
    L --> M[Ver até 3 opções priorizadas]
    M -->|Ver contato| N[Acionar serviço se desejar]
    M -->|Voltar à conversa| C
    I -->|Pedido fora de escopo| G[Mensagem de limite e opções seguras]
    G -->|O que a lei diz| I
    G -->|Defensoria Pública ou CRAM| M
    C -->|Fechar ou saída rápida| X
```

O diagrama representa a intenção descrita no requisito e wireframe. A
triagem, as telas de risco, as fontes e os resultados de encaminhamento ainda
não estão implementados nas features atuais do frontend.

## 5. Etapas dependentes, em ordem de navegação

### Etapa 1 — Enviar o primeiro relato

**Pré-condição:** a usuária está na tela inicial e escolheu escrever ou tocar
em uma sugestão.

**Texto de acolhimento no wireframe da conversa:**

> Conte com as suas palavras o que está acontecendo. Não precisa usar termos
> certos, e você pode parar quando quiser.

**Texto sobre localização no wireframe:**

> Se quiser, diga sua cidade. Só uso isso para indicar serviços perto de você.

**Ações:**

1. Para texto livre, a usuária digita no campo inicial e seleciona **Enviar**.
2. Para sugestão, ela toca em uma frase e a conversa inicia com aquela frase.
3. A mensagem aparece no histórico como fala da usuária.
4. O sistema apresenta o estado de processamento **Lendo com atenção…** no
   wireframe.

**Campo para mensagem subsequente no wireframe:**

- Rótulo **Sua mensagem**.
- Placeholder **Escreva aqui…**.
- Ação **Enviar**.

**Aviso de sessão no wireframe:**

> Nada desta conversa fica salvo. Ao fechar a página ou usar a Saída rápida,
> tudo é apagado.

**Implementação observada:** o chat atual mostra um acolhimento com texto
similar, mantém as mensagens apenas enquanto a tela está aberta e apresenta
estado de envio. O campo está rotulado **Sua mensagem**, usa placeholder
**Escreva aqui…** e botão **Enviar**. A conversa não oferece ainda triagem,
RAG ou continuação persistente.

### Etapa 2 — Triar urgência antes de informar

**[REQUISITO]** Depois de receber o relato, o sistema verifica sinais agudos,
incluindo ideação suicida, agressão em curso, ameaça de morte e presença de
arma.

**Regra obrigatória:** se risco agudo for detectado, interromper o fluxo
informativo e exibir a sugestão de emergência antes de qualquer resposta
psicoeducativa. O caminho da sugestão não deve depender de geração de LLM.

**[GAP]** Os documentos não especificam todas as perguntas ou controles visíveis
da triagem (por exemplo, botões de escolha, perguntas complementares, opção de
não responder ou correção da resposta). O wireframe apresenta tela de risco
agudo como resultado, não um formulário de triagem completo.

**[SUGESTÃO — validar]** Quando a conversa não fornecer informação suficiente
para classificar urgência, fazer uma pergunta curta e opcional, sem atrasar a
exibição de canais de emergência sempre disponíveis. A redação e o conjunto de
opções precisam de revisão de profissionais de proteção e saúde mental antes de
serem aprovados.

### Etapa 3A — Exibir risco agudo

Se o sistema detectar sinal agudo, mostrar uma tela dedicada imediatamente,
antes de conteúdos informativos:

**Título do wireframe:**

> Você pode estar em perigo agora.

**Texto do wireframe:**

> Se puder, ligue para um destes números. As ligações são gratuitas e funcionam
> mesmo sem internet.

**Ações:**

- **190 — Polícia Militar — Ligar agora**
- **180 — Central de Atendimento à Mulher — Ligar agora**
- **192 — SAMU — Ligar agora**
- **188 — CVV · Centro de Valorização da Vida — Ligar agora**
- **Voltar à conversa**

**Aviso do wireframe:**

> O Aurora não liga para ninguém por você. Você decide se e quando ligar.

**Comportamento:** selecionar um número oferece a ligação correspondente; não
executa ligação automática. **Voltar à conversa** retorna ao ponto anterior
sem exigir que a usuária repita o relato. A seção também preserva acesso à
Saída Rápida.

**[GAP]** Os critérios exatos que escolhem quais números destacar para cada
sinal não estão completamente apresentados nas telas. O backlog menciona 190
em risco de morte/agressão em curso, 192 se houver lesão, CVV 188 em crise
emocional e 192 em risco de ato iminente. Confirmar a regra final e a ordem de
exibição com especialistas; não inferir que todos os canais são equivalentes
para todos os casos.

### Etapa 3B — Resposta informativa com fonte

Se não houver risco agudo que interrompa o fluxo, a conversa pode apresentar
conteúdo psicoeducativo fundamentado.

**Abertura de exemplo mostrada no wireframe:**

> Obrigada por contar. O que você descreveu se parece com um padrão que tem
> nome: **[nome do padrão, ex.: isolamento]**.

O wireframe reserva espaço para:

1. explicação curta, em 2 ou 3 frases, do que a fonte diz sobre o padrão;
2. explicação do que a lei garante, sem opinar sobre o caso individual;
3. bloco **Fontes**, com citações rastreáveis — os textos `[Lei nº, artigo]` e
   `[Cartilha oficial, órgão, ano]` são placeholders, não referências reais.

**Opções relacionadas no wireframe:**

- **Onde buscar ajuda**
- **Quais são meus direitos?**
- **O que acontece no meu caso?**
- Campo **Perguntar mais**, placeholder **Perguntar mais…**, ação **Enviar**.

**Aviso no wireframe:**

> Toda resposta mostra de onde veio a informação. Se não houver fonte
> confiável, o Aurora diz que não sabe.

**[REQUISITO]** Se não houver trecho relevante na base, declarar a limitação
em vez de gerar conteúdo sem fonte.

### Etapa 3C — Pedido fora do escopo

Quando a usuária pedir diagnóstico ou parecer sobre seu caso, exibir uma
resposta de limite sem encerrar a conversa.

**Título no wireframe:** **Fora do que eu posso fazer**

**Texto no wireframe:**

> Não posso dar um diagnóstico nem um parecer sobre o seu caso. Isso precisa
> de uma profissional que te escute com calma.
>
> Posso explicar o que a lei diz sobre isso e indicar quem pode te orientar de
> graça.

**Ações sugeridas no wireframe:**

- **O que a lei diz** — retorna ao conteúdo informativo.
- **Defensoria Pública ou CRAM** — abre opções de encaminhamento.
- Campo **Perguntar mais…** para continuar a conversa.

**Aviso de autonomia no wireframe:**

> O Aurora informa sobre a lei, mas não diz o que você deve fazer. A decisão é
> sempre sua.

**[GAP]** A resposta deve distinguir pedido de informação geral sobre a lei de
pedido de interpretação jurídica individual. Casos limítrofes e conteúdo
exato de bloqueio precisam de revisão jurídica e de produto.

### Etapa 4 — Informar localização para encontrar serviços

**Pré-condição:** a usuária escolhe **Onde buscar ajuda** ou uma ação de
encaminhamento.

**Campo no wireframe:**

- Rótulo **Cidade / UF (opcional)**.
- Placeholder **Ex.: Recife / PE**.
- O wireframe explica: **Se quiser, diga sua cidade. Só uso isso para indicar
  serviços perto de você.**

**Regras:**

- A localização é opcional e deve ser informada pela usuária como município/UF.
- Não solicitar geolocalização precisa.
- Se não quiser informar a localização, a usuária deve poder voltar à conversa
  ou acessar canais gerais sem ser bloqueada.

**[GAP]** Não está especificado o que mostrar se a localização não for
informada, for ambígua, não estiver no catálogo ou não tiver serviço válido.

**[SUGESTÃO — validar]** Para localização vazia ou sem resultado local, manter
os contatos nacionais disponíveis e explicar que não foi possível confirmar
opções locais; oferecer **Tentar outra cidade** e **Voltar à conversa**.

### Etapa 5 — Ver opções de encaminhamento

**Título no wireframe:**

> Onde buscar ajuda em [Cidade / UF]

**Introdução:**

> Até 3 opções, do serviço público à sociedade civil. Você escolhe se, quando e
> qual procurar.

Cada cartão de serviço deve apresentar, quando disponível:

- categoria/posição de prioridade;
- nome do serviço;
- **O que faz**;
- **Contato**;
- **Horário**;
- **Custo**;
- ação **Ver contato**.

O wireframe mostra exemplos de categoria: **1 · Órgão público**, **2 · Serviço
especializado** e **3 · Sociedade civil**. São exemplos de categorias, não uma
garantia de que sempre haverá três opções.

**Regras de priorização do requisito/backlog:**

- considerar urgência, tipo de necessidade e município/UF;
- exibir até três opções;
- para necessidade jurídica, priorizar serviços públicos formais: Defensoria
  Pública/NUDEM, depois CRAM/Casa da Mulher Brasileira, OAB e então
  organizações voluntárias, conforme o cenário e a matriz;
- nunca enviar o relato ou dados pessoais ao serviço indicado;
- deixar a escolha de contato com a usuária.

**Texto de atualização no wireframe:**

> Contatos conferidos em [data da última verificação]. Nada desta busca fica
> salvo.

`[data da última verificação]` é um campo dinâmico, não texto literal.

**Retorno:** link **← Voltar à conversa**. O retorno deve preservar a conversa
enquanto a sessão anônima estiver aberta.

**[GAP]** Se não houver serviços locais ativos ou verificados, a especificação
precisa determinar como explicar a ausência, quais contatos gerais mostrar e
como sinalizar informação desatualizada. O critério CA-05 impede serviço
vencido de aparecer como sugestão prioritária.

**[SUGESTÃO — validar]** Mostrar uma mensagem de ausência sem culpar a usuária,
manter canais nacionais e fornecer **Voltar à conversa**. Definir o texto
exato com produto e especialistas.

## 6. Retornar, retomar, pausar e finalizar

| Situação | Comportamento especificado | O que acontece com o conteúdo | Lacuna/proposta |
|---|---|---|---|
| Voltar de risco agudo | **Voltar à conversa** | Preservar o relato e as mensagens enquanto a sessão estiver aberta | [WIREFRAME] define o retorno |
| Voltar de encaminhamento | **← Voltar à conversa** | Preservar conversa e permitir continuação | [WIREFRAME] define o retorno |
| Fazer outra pergunta | Usar **Perguntar mais…** ou **Escreva aqui…** e **Enviar** | A conversa mantém contexto durante a sessão anônima | [REQUISITO] E3-US5 |
| Acionar emergência | Tocar em um telefone | A aplicação não liga nem envia dados por conta própria | [WIREFRAME], E3-US8 |
| Acionar Saída Rápida | **Saída rápida (Esc)** ou Esc | Encerrar a sessão volátil e ir para página neutra | Destino neutro exato ainda é gap |
| Fechar a página anônima | Fechar navegador/aba | A conversa anônima é descartada ao encerrar a sessão; não se oferece retomada depois de fechada | RNF01 e texto do wireframe |
| Retornar pelo navegador/aba ainda aberta | Não há regra detalhada | O comportamento de retorno entre telas deve preservar o que está na sessão até encerrá-la | [GAP] definir se marcação/retorno em memória é necessária |
| Retomar depois de sair/fechar | Não especificado para o modo anônimo | Não recuperar relato anônimo encerrado | **[SUGESTÃO — validar]** Informar a diferença entre continuar na mesma sessão e retomar em outro momento |
| Continuar conversas anteriores com conta | E3-US6 prevê histórico para usuária logada | Retomada de conversa anterior deve existir para a área logada | **[GAP]** tela, lista, seleção, confirmação e exclusão não estão especificadas |
| Excluir conta | E2-US4 prevê exclusão permanente com um clique | Excluir conta e dados vinculados | **[GAP]** confirmação, feedback, prazo e falhas precisam ser especificados |

**[SUGESTÃO — validar]** No modo anônimo, manter uma ação de retorno explícita
nas telas internas, sem criar um botão que restaure uma sessão já encerrada. No
modo logado, definir uma lista de conversas com ação **Continuar** e
**Excluir**, protegida por autenticação; esses rótulos são propostas, não
textos aprovados.

## 7. Jornadas opcionais e futuras do backlog

Os seguintes percursos aparecem no backlog, mas não têm ainda especificação
completa de telas e mensagens. Devem ser refinados sem bloquear o acesso
anônimo.

### 7.1 Criar conta, entrar e migrar conversa

**Definido:** a conta usa apelido e senha, sem exigir e-mail ou telefone real;
login é protegido; a usuária pode migrar voluntariamente a sessão anônima e
excluir a conta/dados.

**[GAPS]** Não há fluxos de tela para cadastro, login, tentativa inválida,
esqueci a senha, bloqueio, migração, confirmação de exclusão ou saída da conta.
Regras de apelido e senha também não estão especificadas.

**[SUGESTÃO — validar]** Definir esses estados antes de construir a área
logada. No fluxo de migração, explicar o que será transferido e pedir
confirmação; não migrar silenciosamente relatos sensíveis.

### 7.2 Questionário de reconhecimento e triagem

**Definido:** questionário guiado baseado em instrumento validado, resultado
sem diagnóstico ou alarmismo e análise de urgência, tipo de necessidade e
localização. A usuária logada pode consultar histórico de triagens.

**[GAPS]** Faltam perguntas aprovadas, escala de respostas, opção de pular,
retorno para editar, apresentação do resultado, significado de cada categoria
e comportamento de interrupção ao detectar risco agudo.

**[SUGESTÃO — validar]** Mapear uma tela por pergunta, progresso compreensível,
opção de interromper e caminho direto para emergência. Conteúdo e classificação
devem ser validados com especialistas; não inventar perguntas ou pontuação.

### 7.3 Módulos de psicoeducação

**Definido:** área logada com módulos curtos em texto, áudio ou vídeo sobre
violência psicológica, ciclo do abuso, direitos e temas relacionados; salvar
progresso.

**[GAPS]** Faltam catálogo de módulos, tela de detalhe, controle de reprodução,
legendas/transcrições, retomada, conclusão, progresso e preferências de áudio.

**[SUGESTÃO — validar]** Especificar navegação de catálogo → detalhe → consumo
→ retomar/concluir, preservando controle da usuária e formatos acessíveis.

### 7.4 Diário de incidentes

**Definido:** na área logada, criar registro com data, hora e descrição,
adicionar fotos ou áudio e exportar PDF protegido.

**[GAPS]** Não há especificação dos campos editáveis, rascunho, salvamento,
confirmação, anexo, exclusão, exportação, senha do PDF ou avisos sobre riscos
de guardar material no dispositivo.

**[SUGESTÃO — validar]** Antes de uma ação irreversível ou exportação, explicar
o que será guardado/gerado e permitir cancelar. Não apresentar o arquivo como
prova garantida nem afirmar que sua posse é segura em dispositivo monitorado.

### 7.5 Guia de segurança e plano de saída

**Definido:** conteúdo informativo baseado em materiais de referência,
anotações pessoais, contatos de emergência e oferta contextual sem pressão.

**[GAPS]** Faltam início do guia, passos, formulário, edição, salvamento,
retomada, exclusão e definição de como sugeri-lo na conversa.

**[SUGESTÃO — validar]** Tornar explícito que o conteúdo é opcional e
informativo, permitir sair sem salvar e nunca presumir que a usuária deve
deixar o relacionamento ou a residência.

## 8. Mensagens e campos a validar

As frases abaixo são reproduzidas do wireframe ou dos requisitos e precisam
ser confirmadas como texto de produto. Frases com colchetes são placeholders.

| Tela | Texto/controle | Situação |
|---|---|---|
| Início | **Sem cadastro. Nada fica salvo.** | Texto do wireframe; conciliar com aviso atual de protótipo |
| Início | **Escreva sua mensagem** / **Escreva o que quiser…** | Rótulo/placeholder do wireframe |
| Início | **Enviar** | Botão do wireframe; o comportamento de envio em um toque está implementado |
| Sugestões | **Quero entender o que estou sentindo**; **Tenho dúvidas sobre meus direitos**; **Onde encontrar apoio** | Opções do wireframe e da implementação |
| Conversa | **Conte com as suas palavras o que está acontecendo. Não precisa usar termos certos, e você pode parar quando quiser.** | Acolhimento do wireframe |
| Conversa | **Se quiser, diga sua cidade. Só uso isso para indicar serviços perto de você.** | Orientação de localização do wireframe |
| Conversa | **Cidade / UF (opcional)**; **Ex.: Recife / PE** | Campo e exemplo do wireframe |
| Conversa | **Lendo com atenção…** | Estado do wireframe; texto final e duração não definidos |
| Emergência | **Você pode estar em perigo agora.** | Título do wireframe |
| Emergência | **Se puder, ligue para um destes números. As ligações são gratuitas e funcionam mesmo sem internet.** | Texto do wireframe; confirmar informação e adequação com especialistas |
| Emergência | **O Aurora não liga para ninguém por você. Você decide se e quando ligar.** | Aviso do wireframe |
| Resposta | **Toda resposta mostra de onde veio a informação. Se não houver fonte confiável, o Aurora diz que não sabe.** | Aviso do wireframe |
| Guardrail | **Fora do que eu posso fazer** | Título do wireframe |
| Guardrail | **Não posso dar um diagnóstico nem um parecer sobre o seu caso. Isso precisa de uma profissional que te escute com calma.** | Texto do wireframe |
| Encaminhamento | **Onde buscar ajuda em [Cidade / UF]** | Título com campo dinâmico |
| Encaminhamento | **Até 3 opções, do serviço público à sociedade civil. Você escolhe se, quando e qual procurar.** | Introdução do wireframe |
| Sessão | **Nada desta conversa fica salvo. Ao fechar a página ou usar a Saída rápida, tudo é apagado.** | Wireframe; validar redação para não prometer apagar rastros externos |

## 9. Gaps prioritários para decisão

1. **Saída Rápida:** qual página neutra será usada, o que exatamente é apagado
   pela aplicação e qual é o comportamento ao pressionar Esc durante edição?
2. **Retorno e retomada:** quais retornos mantêm conversa em memória; o que é
   retomável apenas com conta; como evitar sugerir que uma sessão anônima fechada
   pode ser recuperada?
3. **Triagem:** quais perguntas e respostas aparecem, em que ordem, quando
   interromper e quais canais são destacados para cada sinal?
4. **Ausência de serviço local:** que mensagem e alternativas apresentar se
   a cidade não tiver opção verificada?
5. **Textos de privacidade:** como explicar de forma correta a sessão volátil
   sem prometer apagar histórico do navegador ou do dispositivo?
6. **Conta e dados:** como funcionam cadastro, login, recuperação, migração,
   exclusão e erros associados?
7. **Conteúdo e diário:** quais são os avisos antes de salvar, anexar ou
   exportar conteúdos sensíveis?
8. **Diferença entre documentos e implementação:** validar o aviso de protótipo
   atualmente mostrado na tela inicial versus o texto de acesso anônimo do
   wireframe.

## 10. Referências e rastreabilidade

- `docs/requisitos-aurora.md`: RF01–RF07, RF10; RNF01, RNF03, RNF04, RNF06 e
  RNF07.
- `docs/backlog-aurora.md`: E1–E10 e E12–E13; modos anônimo/logado e fases MVP,
  V1 e V2.
- `docs/arquitetura_operacionalizada_aurora.md`: CA-01 a CA-05 e metas
  verificáveis de segurança, triagem, guardrails, latência e frescor do
  catálogo.
- `docs/aurora-criacao-projeto.md`: limites do scaffold inicial e distinção
  entre protótipo e produto completo.
- `docs/analise-comparativa-solucoes.md`: contexto de produto e lacunas que o
  Aurora pretende atender.
- `docs/Requisitos Aurora.pdf` e
  `docs/Solução Tecnológica para Vítimas de Abuso.pdf`: documentos de referência
  indicados para o projeto. Confirmar durante a revisão se há requisitos
  adicionais neles que não estejam refletidos nos documentos Markdown.
- `src/frontend/src/wireframe/Aurora — Wireframe.html`: telas de início,
  conversa, risco agudo, informação com fonte, limite/guardrail, indicação
  priorizada, Saída Rápida e guia de estilo.
- `src/frontend/src/features/welcome/WelcomePage.tsx`,
  `src/frontend/src/features/chat/ChatPage.tsx`,
  `src/frontend/src/features/chat/components/MessageComposer.tsx` e
  `src/frontend/src/features/chat/components/MessageList.tsx`: comportamento
  atualmente implementado de início e conversa.

## 11. Validação pendente

Este documento está em **rascunho**. Validar:

- a ordem das ações independentes;
- os percursos de risco agudo, resposta com fonte, guardrail e encaminhamento;
- os textos, campos e nomes de ações;
- as propostas marcadas **SUGESTÃO — validar**;
- a separação entre modo anônimo, modo logado e funcionalidades futuras.

Após revisão, registrar as alterações aprovadas e atualizar o status do
documento. Não tratar uma sugestão como requisito aprovado sem essa confirmação.
