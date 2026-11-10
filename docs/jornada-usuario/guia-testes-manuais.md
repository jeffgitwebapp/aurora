# Guia de testes manuais — protótipo Aurora

**Para quem:** pessoas que vão testar o protótipo no navegador (localmente ou no ambiente publicado na AWS), sem precisar ler o código.
**Situação em 02/11/2026:** cobre I-01 a I-05, C-01 a C-06 e L-01 a L-05, conforme o [plano de implementação](./plano-implementacao-jornada-usuario.md).

> **Importante:** todo o conteúdo é de demonstração. As frases abaixo são **fixtures de teste**: o protótipo não entende linguagem real, não detecta risco real e não indica serviços reais. Não use relatos, nomes, telefones ou senhas reais.

## 1. Antes de começar

- **Endereço:** o ambiente publicado ou `http://localhost:5173` (backend em `:8000`).
- **Dados somem:** contas, conversas salvas, diário, progresso e plano ficam só na memória do servidor. Eles somem quando o backend reinicia ou é publicado de novo.
- **Mais de uma instância na AWS:** uma conta criada pode não ser encontrada no login seguinte se a requisição cair em outra instância.
- **Recarregar a página** encerra a conversa anônima e a sessão da conta.
- **Geolocalização** (C-06) só funciona em HTTPS ou em `localhost`.
- **Atraso proposital:** respostas que passam pelo serviço de informação levam **cerca de 5 segundos** ("Lendo com atenção…"). Risco, frase incerta, limite de escopo e convite do guia respondem na hora.

### Como as frases são reconhecidas

- Maiúsculas/minúsculas, acentos, espaços repetidos e pontuação no começo ou no fim **não fazem diferença**. "ELE ESTA COM UMA ARMA AQUI!" vale igual a "Ele está com uma arma aqui".
- **Frases de risco** valem dentro de uma mensagem maior, desde que apareçam como frase completa, separada por `.`, `!`, `?`, `;` ou quebra de linha. Exemplo: "Bom dia. Ele disse que vai me matar." aciona o risco.
- **Todas as outras fixtures** (frase incerta, limite de escopo, convite do guia e perguntas com fonte) precisam ser a **mensagem inteira**. Com texto a mais, a mensagem segue o fluxo comum.
- **Ordem de avaliação:** risco agudo → frase incerta → limite de escopo → convite do guia → pergunta com fonte → "sem fonte".

## 2. Tabela rápida de frases

| Digite na conversa | O que deve acontecer | Item |
|---|---|---|
| Estou pensando em me matar | Modal de risco; **188** destacado | C-02/C-03 |
| Quero tirar minha vida | Modal de risco; **188** destacado | C-02/C-03 |
| Ele está me agredindo agora | Modal de risco; **190** destacado | C-02/C-03 |
| Estou sendo atacada neste momento | Modal de risco; **190** destacado | C-02/C-03 |
| Ele disse que vai me matar | Modal de risco; **190** destacado | C-02/C-03 |
| Recebi uma ameaça de morte | Modal de risco; **190** destacado | C-02/C-03 |
| Ele está com uma arma aqui | Modal de risco; **190** destacado | C-02/C-03 |
| Há uma arma no local agora | Modal de risco; **190** destacado | C-02/C-03 |
| Ele está me agredindo agora. Há uma arma no local agora. | Modal de risco com dois sinais; **190** destacado | C-02/C-03 |
| frase incerta | Modal "Não foi possível avaliar esta mensagem." | C-02/C-03 |
| O que é violência psicológica? | Resposta com citação da Lei Maria da Penha (art. 7º, II) e link **Fontes (1)** | C-04 |
| Violência psicológica é crime? | Resposta com citação do Código Penal (art. 147-B) e link **Fontes (1)** | C-04 |
| Eu tenho depressão? | Bloco **Fora do que eu posso fazer** (diagnóstico) | C-05 |
| Que remédio devo tomar? | Bloco **Fora do que eu posso fazer** (prescrição) | C-05 |
| O que acontece no meu caso? | Bloco **Fora do que eu posso fazer** (parecer jurídico individual) | C-05 |
| Devo denunciar meu marido? | Bloco **Fora do que eu posso fazer** (parecer jurídico individual) | C-05 |
| Quero pensar na minha segurança | Convite opcional com **Abrir guia de segurança** | L-05 |
| Qualquer outra mensagem | Depois de ~5 s: "Não encontrei uma fonte confiável para responder a isso. Prefiro dizer que não sei a inventar uma resposta." | C-01/C-04 |

**Controles negativos** (devem seguir o fluxo comum e mostrar "sem fonte"):

- Não estou pensando em me matar
- frase incerta. Preciso de ajuda.
- O que é violência psicológica? Ele faz isso comigo.
- Eu tenho depressão? Ou é só cansaço?
- Quero pensar na minha segurança agora mesmo
- Quais são os direitos de uma mulher em situação de violência?
- As três sugestões da tela inicial: "Quero entender o que estou sentindo", "Tenho dúvidas sobre meus direitos", "Onde encontrar apoio".

## 3. Roteiros por funcionalidade

Marque cada item ao conferir. Anote o que divergir, com o navegador e o tamanho de tela usados.

### 3.1 Tela inicial, privacidade e contatos (I-01, I-03, I-04)

- [ ] A tela inicial mostra os quatro canais com links de ligação: Polícia Militar **190**, Central de Atendimento à Mulher **180**, SAMU **192** e CVV **188**. O link **Emergência** do topo liga para 190.
- [ ] Tocar num número só abre o discador do aparelho; nada é ligado ou enviado sozinho.
- [ ] Campo vazio ou só com espaços não inicia a conversa (**Enviar** desativado).
- [ ] Texto digitado + **Enviar** abre a conversa com essa mensagem uma única vez.
- [ ] **Enter** também envia (na tela inicial e na conversa); **Shift+Enter** quebra a linha sem enviar.
- [ ] Cada uma das três sugestões abre a conversa com o próprio texto.
- [ ] **Privacidade** abre o aviso: "Esta conversa fica na memória enquanto esta página está aberta. Ao usar a Saída Rápida ou encerrar a página, o Aurora descarta o conteúdo da sessão que mantém. Isso não apaga possíveis registros do navegador, dispositivo, rede ou terceiros." **Fechar** volta ao início.
- [ ] **Contatos úteis** leva aos canais.

### 3.2 Saída Rápida (I-02)

- [ ] Na tela inicial: **Sair** abre `/receitas`.
- [ ] Na conversa: **Saída rápida (Esc)** e a tecla **Esc** abrem `/receitas`, inclusive com o cursor dentro do campo de texto e durante "Lendo com atenção…".
- [ ] Dentro dos modais (risco, frase incerta, confirmação de cidade), **Saída rápida (Esc)** e **Esc** também funcionam.
- [ ] A página mostra uma única receita (Pudim de leite, Pão de forno ou Frango assado), com título da aba "Receitas" e sem a marca Aurora.
- [ ] Acionar de novo mostra uma receita **diferente** da anterior.
- [ ] Voltar ao endereço da conversa não mostra as mensagens anteriores.
- [ ] Com uma conta aberta, a Saída Rápida também encerra a sessão: ao voltar ao início, o rodapé mostra **Entrar**.

### 3.3 Conversa, erros e reenvio (C-01)

- [ ] Uma mensagem comum mostra "Lendo com atenção…" e responde em cerca de 5 s.
- [ ] Mensagens seguintes se acumulam; recarregar a página apaga tudo.
- [ ] **Falha simulada (só local):** pare o backend e envie uma mensagem. Aparece uma mensagem de erro com **Tentar novamente**, sem duplicar a sua mensagem. Ligue o backend e use **Tentar novamente**.

### 3.4 Risco agudo e frase incerta (C-02, C-03)

Use as frases da seção 2.

- [ ] Abre um modal sobre a conversa com o título "Você pode estar em perigo agora.", com a conversa visível ao fundo.
- [ ] O canal destacado corresponde à frase (190 ou 188); os quatro canais continuam visíveis.
- [ ] Aparecem as frases "O Aurora não liga para ninguém por você. Você decide se e quando ligar." e o aviso de demonstração.
- [ ] Não há resposta informativa nem espera de 5 s.
- [ ] **Voltar à conversa** fecha o modal sem duplicar a mensagem; uma nova mensagem comum não reabre o modal.
- [ ] "frase incerta" abre o modal "Não foi possível avaliar esta mensagem.", com "Isso não significa que não exista risco…".

### 3.5 Resposta com fontes (C-04)

- [ ] "O que é violência psicológica?" mostra a citação literal da Lei nº 11.340/2006, art. 7º, II, o link **Fontes (1)** e o aviso "Resposta baseada nas fontes indicadas…".
- [ ] **Fontes (1)** abre um modal com a lista numerada; o marcador `[1]` do texto abre o mesmo modal com a fonte destacada.
- [ ] **Voltar à conversa** fecha o modal; Esc com o modal aberto aciona a Saída Rápida.
- [ ] "Violência psicológica é crime?" mostra a citação do Código Penal, art. 147-B.
- [ ] O link da fonte, dentro do modal, abre o site do Planalto em outra aba.
- [ ] A lateral mostra "Toda resposta mostra de onde veio a informação. Se não houver fonte confiável, o Aurora diz que não sabe."

### 3.6 Limite de escopo (C-05)

- [ ] As quatro frases do C-05 mostram o bloco **Fora do que eu posso fazer**, no fluxo e sem modal, na hora.
- [ ] O texto diz: "Não posso dar um diagnóstico nem um parecer sobre o seu caso. Isso precisa de uma profissional que te escute com calma." e "Posso explicar o que a lei diz sobre isso e indicar quem pode te orientar de graça."
- [ ] Aparece o aviso de autonomia: "O Aurora informa sobre a lei, mas não diz o que você deve fazer. A decisão é sempre sua."
- [ ] **O que a lei diz** envia "O que é violência psicológica?" e traz a resposta com fontes.
- [ ] **Defensoria Pública ou CRAM** leva aos contatos úteis da lateral (no protótipo, os contatos gerais; a nota abaixo do botão explica isso).

### 3.7 Onde buscar ajuda (C-06)

Abra pelo botão **Onde buscar ajuda** na lateral da conversa.

| Situação | Como provocar | Resultado esperado |
|---|---|---|
| Localização perto de uma capital | Permitir a localização estando a até ~40 km de uma capital | Modal "Confirmar sua cidade" com "Encontramos: [Capital] / [UF]" |
| Localização negada ou indisponível | Bloquear a permissão ou usar navegador sem HTTPS | "A localização do aparelho não está disponível. Se quiser, digite sua cidade abaixo." |
| Longe de qualquer capital | Permitir a localização longe das capitais | "Não consegui identificar sua cidade pela localização. Se quiser, digite abaixo." (sem modal) |
| Cidade com serviços | Digitar `Recife / PE` ou `São Paulo / SP` | Título "Onde buscar ajuda em Recife / PE" e três cartões: 1 · Órgão público, 2 · Serviço especializado, 3 · Sociedade civil |
| Cidade sem serviços | Digitar `Olinda / PE` (ou outra cidade/UF válida) | "Não consegui confirmar serviços perto de você nesta demonstração. Os canais nacionais continuam disponíveis." com **Ver canais nacionais**, **Tentar outra cidade** e **Voltar à conversa** |
| Sem UF | Digitar `Recife` | "Informe a cidade e a UF, por exemplo: Recife / PE." |
| UF inexistente | Digitar `Recife / XX` | Mensagem de erro com **Tentar novamente** |

- [ ] Também são aceitos os separadores `-` e `,` (`Recife - PE`, `Recife, PE`), e a busca ignora maiúsculas e acentos (`sao paulo / sp`).
- [ ] No modal: **Usar esta cidade** faz a busca; **Digitar outra cidade** leva ao campo.
- [ ] Os cartões mostram "Não incluído na demonstração" em Contato, Horário e Custo, e a nota "Demonstração: serviços fictícios, sem contatos verificados. Nada desta busca fica salvo."
- [ ] **← Voltar à conversa** reabre a conversa com as mensagens e o rascunho preservados.
- [ ] Atenção: o catálogo só tem Recife/PE e São Paulo/SP. Perto de outra capital, o modal aparece, mas a busca dá "sem resultado".

### 3.8 Questionário (I-05)

Abra por **Responder questionário** na lateral da conversa.

| Pergunta 1 | Pergunta 2 | Faixa esperada |
|---|---|---|
| Opção de demonstração A | Opção de demonstração A | Faixa de demonstração **A** |
| Opção de demonstração A | Opção B ou "Prefiro não responder" | Faixa de demonstração **B** |
| Opção B ou "Prefiro não responder" | Opção de demonstração A | Faixa de demonstração **B** |
| Opção B ou "Prefiro não responder" | Opção B ou "Prefiro não responder" | Faixa de demonstração **C** |

- [ ] A pergunta 3 é "Que tipo de ajuda você procura?" (Denúncia, Orientação jurídica, Apoio psicológico, Apoio entre pares, Prefiro não responder), e o resultado repete a escolha.
- [ ] **Continuar** fica desativado até escolher uma opção; **Voltar** mantém as respostas.
- [ ] O resultado avisa que a faixa é fictícia e não indica padrão, risco nem diagnóstico; **Onde buscar ajuda** abre o C-06.
- [ ] **Estou em perigo agora**, em qualquer etapa, fecha o questionário e abre o modal de risco.
- [ ] **Parar questionário** volta à conversa; ao reabrir, as respostas começam vazias.

### 3.9 Conta: criar, entrar e sair (L-01)

Abra pelo link **Entrar** no rodapé da tela inicial.

| Teste | Dado de exemplo | Resultado esperado |
|---|---|---|
| Apelido válido | `lua_azul_01` | Aceito |
| Apelido inválido | `ab`, `com espaço`, `acentuação` | "Apelido inválido. De 3 a 30 caracteres: letras, números, ponto, hífen ou sublinhado." |
| Senha válida | `senhaforte1` | Aceita (10+ caracteres, letras e números) |
| Senha fraca | `curta1`, `somenteletras`, `1234567890` | "Senha fraca. Pelo menos 10 caracteres, com letras e números." |
| Confirmação diferente | `senhaforte1` / `senhaforte2` | "As senhas não são iguais." |
| Apelido repetido | Criar de novo o mesmo apelido (também com outras maiúsculas) | "Este apelido já está em uso. Escolha outro." |
| Login errado | Senha errada ou apelido inexistente | "Apelido ou senha incorretos." (a mesma mensagem nos dois casos) |
| Bloqueio | 5 erros seguidos com o mesmo apelido | "Muitas tentativas. Aguarde 1 minuto e tente novamente." |

- [ ] **Mostrar senha** exibe o texto digitado.
- [ ] Na aba **Entrar** aparece: "Sem e-mail, não é possível recuperar a senha. Guarde-a em lugar seguro."
- [ ] Depois de entrar: "Olá, [apelido]", **Ir para a conversa** e **Sair da conta**; no início, o rodapé mostra **Minha conta**.
- [ ] Recarregar a página encerra a sessão. A sessão também expira após 30 minutos.

### 3.10 Salvar conversa, histórico e excluir conta (L-02)

- [ ] Na conversa, **Salvar conversa na conta** sem estar logada abre Entrar/Criar conta dentro da conversa, sem perder as mensagens.
- [ ] Sem mensagens: "Ainda não há mensagens para salvar."
- [ ] A confirmação diz "Isto vai guardar N mensagens desta conversa na conta [apelido]. Salvar?"; nada é salvo antes de **Salvar**. **Cancelar** volta sem salvar.
- [ ] Depois de salvar: **Voltar à conversa** e **Ver em Minha conta**.
- [ ] Em **Minha conta → Conversas salvas**: data, início da primeira mensagem e número de mensagens; **Ver** abre a conversa só para leitura; **Excluir** pede confirmação e mostra "Conversa excluída."
- [ ] **Excluir conta e todos os dados** mostra na tela "Isto apaga a conta e N conversas salvas. Não dá para desfazer."; **Excluir agora** mostra "Conta e dados excluídos.", e um novo login com o mesmo apelido falha.

### 3.11 Módulos (L-03)

Em **Minha conta → Módulos**.

- [ ] Aparecem oito módulos. Só "O que é violência psicológica" tem texto; os outros aparecem "em preparação".
- [ ] O módulo com texto tem 2 partes (Lei Maria da Penha e Código Penal), cada uma com fonte.
- [ ] Sair na Parte 2 e voltar mostra "Parte 2 de 2" e **Continuar de onde parei**.
- [ ] **Concluir módulo** mostra "Você concluiu este módulo. Você decide o que fazer com o que leu."; a lista passa a "Concluído" com **Rever**.
- [ ] Aparece o aviso "Áudio e vídeo com legenda e transcrição: ainda não disponíveis nesta demonstração."

### 3.12 Diário (L-04)

Em **Minha conta → Diário**.

| Teste | Como | Resultado esperado |
|---|---|---|
| Registro válido | Data de hoje ou passada, hora opcional, descrição | "Registro salvo." |
| Sem descrição | Deixar a descrição vazia | "Escreva uma descrição." |
| Data futura | O calendário não permite; se forçada, o servidor recusa | Erro e "Nada foi salvo." |
| Cancelar | **Cancelar** com o formulário preenchido | "Nada foi salvo." |
| Editar | **Editar** → alterar → **Salvar registro** | "Registro atualizado." |
| Excluir | **Excluir** → **Excluir registro** | "Registro excluído." |

- [ ] O aviso de privacidade aparece no formulário antes de salvar.
- [ ] **Anexo de foto ou áudio (simulado):** escolher um arquivo mostra só o nome e o tamanho ("…O arquivo não foi enviado nem será guardado."); **Remover anexo** limpa a escolha.
- [ ] A lista aparece do registro mais recente para o mais antigo.
- [ ] **Exportar (demonstração)** fica desativado sem registros. Com registros, mostra primeiro o aviso sobre arquivos no aparelho e sobre a falta de valor jurídico; depois de **Continuar**, mostra a prévia na tela. **Nenhum arquivo é baixado.**

### 3.13 Guia e plano de segurança (L-05)

Entradas: **Minha conta → Guia de segurança**, ou a frase "Quero pensar na minha segurança" na conversa e depois **Abrir guia de segurança**.

- [ ] Pela conversa, sem login, o painel pede para entrar ali mesmo; **← Voltar à conversa** mantém as mensagens.
- [ ] O guia mostra o aviso: "Este guia é opcional e informativo. Ele não presume que você deva sair de casa ou do relacionamento e não substitui atendimento especializado. Você decide o que usar."
- [ ] As três seções aparecem "em preparação"; **Canais de apoio** mostra os quatro números com link de ligação.
- [ ] **Começar meu plano** → **Adicionar contato** (até 5) → nome e telefone; e anotações (até 4.000 caracteres).

| Telefone digitado | Resultado esperado |
|---|---|
| `(81) 99999-0000` ou `81999990000` | Aceito; vira link de ligação "Amiga Ana · (81) 99999-0000" |
| `123` ou `abcdefghij` | "Informe um telefone válido para [nome]." |
| Contato sem nome | "Cada contato precisa de um nome ou apelido." |

- [ ] **Sair sem salvar** mostra "Nada foi salvo." e mantém o plano anterior.
- [ ] **Salvar plano** mostra "Plano salvo."; o plano aparece igual em **Minha conta**.
- [ ] Nenhuma mensagem é enviada aos contatos; a ligação só acontece se a pessoa tocar no número.

## 4. Verificações gerais

- [ ] **Celular ou janela estreita (320 px):** nenhuma tela com rolagem horizontal; botões com área de toque confortável.
- [ ] **Teclado:** é possível chegar a todos os botões e campos com Tab; modais recebem o foco ao abrir.
- [ ] **Avisos de demonstração:** aparecem nas respostas, no catálogo, no questionário, nos módulos, no diário e no guia.
- [ ] **Armazenamento local:** com as ferramentas do navegador, conferir que `localStorage`, `sessionStorage` e cookies continuam vazios.

## 5. Como registrar o resultado

Para cada item testado, anote:

- data, ambiente (AWS ou local), navegador e tamanho de tela;
- item do plano (ex.: C-06) e linha do roteiro;
- resultado: **OK** ou **divergente**, com o que apareceu e uma captura de tela, se possível.

Divergências devem voltar para o [plano de implementação](./plano-implementacao-jornada-usuario.md), no item correspondente. Este guia verifica o funcionamento do protótipo e **não substitui** a aprovação do time de produto nem as revisões de especialistas registradas em cada tarefa.
