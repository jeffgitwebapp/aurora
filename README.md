# Projeto Aurora

Plataforma de psicoeducação e informação para mulheres em situação de violência psicológica.

> [!WARNING]
> **Aviso ético e de segurança:** Este projeto é um protótipo de demonstração técnica: triagem de risco por padrões, limite de escopo e respostas informativas geradas por LLM a partir de uma base curada (RAG), com fontes citadas. As listas de triagem e escopo são provisórias e a base ainda está em revisão especializada. **Não é seguro nem validado para uso com pessoas em situação de violência.** Não substitui atendimento profissional, apoio emergencial nem oferece garantias de proteção.

---

## 1. Visão Geral e Estrutura Arquitetural

O projeto segue os princípios de monólito modular, Bounded Context (DDD Estratégico) e Vertical Slice Architecture:

- **Bounded Contexts (backend):** cada contexto em `contexts/<nome>` tem `features/` (fatias verticais com `router.py`, `schemas.py` e `handler.py`) e `services/` (regras e adaptadores usados pelas fatias, atrás de portas `port.py`). `main.py` é a raiz de composição: cria os serviços e registra os routers de cada contexto.

  | Contexto | Pasta | Features |
  |---|---|---|
  | Conversa | `contexts/conversation` | `send_message` (chat: triagem, escopo, RAG e resposta) |
  | Encaminhamento | `contexts/referral` | `recommend_services` (serviços por localização) |
  | Questionário | `contexts/questionnaire` | `take_questionnaire` |
  | Contas | `contexts/accounts` | `register_account`, `manage_session`, `delete_account`, `saved_conversations`, `journal`, `module_progress`, `safety_plan` |
  | Aprendizagem | `contexts/learning` | `browse_modules`, `read_safety_guide` |

- **Frontend Modular:** cada pasta de `features/` é uma fatia vertical independente e importa apenas `shared/` e o próprio código. Telas e estado usados por mais de uma feature ficam em `shared/`. A navegação entre features passa por `shared/redirectsManagement` (`redirect("account")`, `redirect("referral")`, `redirect("quickExit")`…), sem a feature de origem conhecer a de destino. `app/App.tsx` é a raiz de composição: o único lugar que liga cada destino ao componente que o atende.

### Estrutura do Repositório

```text
aurora/
├── .github/workflows/
│   ├── deploy.yml                      # Testes, build, imagens GHCR e deploy na EC2 (push em release)
│   └── eval-v1-2.yml                   # Avaliação essencial com o LLM real (PRs para release)
├── docs/                               # Documentação e Engenharia de Requisitos / Arquitetura
│   ├── analise-comparativa-solucoes.md # Comparativo com 13 iniciativas existentes
│   ├── arquitetura_operacionalizada_aurora.md # Fitness functions e gates de qualidade
│   ├── aurora-arquitetura-4mais1.drawio       # Visões arquiteturais 4+1
│   ├── aurora-base-rag/                # Base de conhecimento curada, versionada (v0.03…)
│   ├── aurora-criacao-projeto.md       # Plano de scaffold inicial
│   ├── backlog-aurora.md               # Backlog de épicos (E1 a E13)
│   ├── c4-aurora-mvp.drawio            # Modelagem arquitetural C4
│   ├── chat/                           # Processamento do diálogo e avaliação da v1.2
│   ├── jornada-usuario/                # Jornada, contratos, testes manuais e
│   │                                   # diagrama-sequencia-chat-front-back.drawio
│   ├── plano-implementacao-adicionando-agente-aurora.md # Plano e decisões da v1.2 (RAG + LLM)
│   └── requisitos-aurora.md            # Requisitos Funcionais e Não-Funcionais (ISO 25010)
├── skills/                             # Competências necessárias e especificações por skill
│   └── lista_skills.md                 # Índice das skills por fase do projeto
├── docker-compose.yml                  # Execução local (portas só em 127.0.0.1)
├── docker-compose.prod.yml             # Produção na EC2 (só o frontend na porta 80)
├── DEPLOY-EC2.md                       # Guia de deploy
├── src/                                # Código-fonte da aplicação
│   ├── backend/                        # FastAPI + uv (Python 3.12+)
│   │   ├── pyproject.toml / uv.lock / Dockerfile
│   │   ├── scripts/build_knowledge_snapshot.py # Gera o snapshot JSON da base vigente
│   │   ├── evals/v1_2/                 # Dataset e runner da avaliação com LLM
│   │   ├── src/aurora_backend/
│   │   │   ├── main.py                 # Raiz de composição: serviços, motor do chat e routers
│   │   │   ├── shared/                 # Normalização de texto e fontes legais compartilhadas
│   │   │   └── contexts/
│   │   │       ├── conversation/       # Bounded Context: Conversa
│   │   │       │   ├── engine.py       # Escolhe o motor do chat por ambiente (fixtures | base | llm)
│   │   │       │   ├── features/send_message/
│   │   │       │   │   ├── router.py   # POST /api/chat/messages; erros → 422/503
│   │   │       │   │   ├── schemas.py  # Contratos Pydantic de entrada e saída
│   │   │       │   │   ├── handler.py  # Orquestra as etapas do chat, em ordem fixa
│   │   │       │   │   └── replies.py  # Textos fixos dos desfechos sem redação
│   │   │       │   └── services/
│   │   │       │       ├── triage/            # Triagem de risco agudo por padrões (sem LLM)
│   │   │       │       ├── guardrail/         # Limite de escopo (diagnóstico, prescrição, parecer)
│   │   │       │       ├── small_talk/        # Saudação, agradecimento e despedida
│   │   │       │       ├── content_offer/     # Oferta do guia de segurança
│   │   │       │       ├── knowledge_base/    # Snapshot da base, BM25 e seletores de trechos via LLM
│   │   │       │       ├── language_model/    # Porta LLM e adaptadores Gemini e Claude
│   │   │       │       ├── grounded_answer/   # Redação ancorada nos trechos (prompt system_v1_2.md)
│   │   │       │       ├── answer_guardrail/  # Guardrail de saída determinístico
│   │   │       │       ├── disclosure/        # Relato pessoal sem fonte → acolhimento
│   │   │       │       ├── decision_trace/    # Log de decisão só com metadados
│   │   │       │       ├── knowledge/ e chat_response/ # Portas e implementações fixture/base
│   │   │       ├── referral/           # Encaminhamento: catálogo de serviços
│   │   │       ├── questionnaire/      # Questionário de reconhecimento
│   │   │       ├── accounts/           # Conta, sessão, conversas salvas, diário, plano de segurança
│   │   │       └── learning/           # Módulos de psicoeducação e guia de segurança
│   │   └── tests/                      # Pytest por feature e por serviço (offline, sem rede)
│   └── frontend/                       # React 19 + TypeScript + Vite
│       ├── package.json
│       ├── package-lock.json
│       ├── index.html
│       ├── vite.config.ts              # Proxy reverso local (/api -> :8000)
│       ├── tsconfig.json
│       └── src/
│           ├── main.tsx                # Ponto de entrada React
│           ├── app/
│           │   └── App.tsx             # Raiz de composição: providers, painéis e seções por destino
│           ├── shared/                 # Usado por várias features; nunca importa features/
│           │   ├── components/         # EmergencyContacts e RiskScreen (modal de risco)
│           │   ├── forms/              # Utilitários de formulário (Enter envia)
│           │   ├── session/            # Sessão da conta, cliente autenticado e AccountForm
│           │   ├── transcript/         # Cópia somente leitura da conversa aberta
│           │   └── redirectsManagement/ # Destinos (páginas, painéis, Saída Rápida) e redirect()
│           ├── features/               # Cada feature importa só shared/ e o próprio código
│           │   ├── welcome/            # Tela inicial
│           │   ├── chat/               # Conversa: envio, validação do contrato, tela de risco,
│           │   │                       # citações [n] e modal de fontes
│           │   ├── referral/           # Onde buscar ajuda (localização e catálogo)
│           │   ├── questionnaire/      # Questionário
│           │   ├── account/            # Minha conta, conversas salvas e exclusão
│           │   ├── learning/           # Módulos e progresso
│           │   ├── journal/            # Diário
│           │   ├── safety/             # Guia e plano de segurança
│           │   └── recipes/            # Página neutra da Saída Rápida
│           └── styles.css              # Estilos acessíveis e responsivos
└── LICENSE                             # Licença do projeto
```

### Fluxo do chat

O `handle_send_message` executa as etapas sempre nesta ordem; a primeira que decide encerra o fluxo:

1. **Triagem de risco** (sem LLM): sinal agudo ou dúvida → `reply: null` e o front abre a tela de risco.
2. **Limite de escopo** (sem LLM): diagnóstico, prescrição ou parecer individual → texto fixo de limite.
3. **Conversa social** (sem LLM): só saudação, agradecimento ou despedida → texto fixo.
4. **Oferta de conteúdo** (sem LLM): convite opcional ao guia de segurança.
5. **Recuperação (RAG):** BM25 traz até 30 candidatos da base curada; o LLM escolhe até 5 trechos (no modo agêntico, pode pedir até 2 buscas extras). Sem trecho → acolhimento se for relato pessoal, senão "não sei".
6. **Redação ancorada:** o LLM escreve segmentos citando os ids das fontes, que viram marcadores `[n]`.
7. **Guardrail de saída** (sem LLM): reprova a resposta inteira se faltar citação ou houver diagnóstico, prescrição, decisão pela usuária, contato ou link não autorizado → `503`.

O frontend valida o contrato da resposta e só exibe o desfecho decidido pelo backend. Os diagramas de sequência das duas pontas estão em [diagrama-sequencia-chat-front-back.drawio](./docs/jornada-usuario/diagrama-sequencia-chat-front-back.drawio) (abas **Backend** e **Frontend**).

### Competências necessárias para desenvolver o Aurora

O Aurora requer competências de produto, engenharia e domínio especializado. As principais áreas são:

- **Base do MVP:** análise de requisitos e rastreabilidade; jornada e usabilidade; arquitetura e integração ponta a ponta; desenvolvimento de APIs com Python/FastAPI e frontend React/TypeScript.
- **Segurança e responsabilidade:** domínio de violência psicológica e design informado por trauma; privacidade/LGPD; segurança de aplicação; triagem determinística de risco agudo; acessibilidade e linguagem simples.
- **Informação e encaminhamento:** curadoria de conteúdo e RAG; integração de LLM e engenharia de prompts; guardrails e avaliação generativa; catálogo de serviços e motor de encaminhamento.
- **Entrega e qualidade:** testes e fitness functions; DevOps, AWS, CI/CD e operação.
- **Evolução do produto:** autenticação e área logada; persistência, criptografia e diário; gestão de conteúdo; integrações externas; conteúdo multimídia acessível; observabilidade e desempenho.

Consulte o [índice de skills](./skills/lista_skills.md) para a relação completa, organizada por fase, e as especificações individuais de cada competência. O [plano de implementação da jornada](./docs/jornada-usuario/plano-implementacao-jornada-usuario.md) também indica quais skills consultar em cada tarefa.

> [!NOTE]
> Este inventário é um mapa de conhecimentos necessários para orientar o desenvolvimento; não significa que essas competências ou funcionalidades já estejam implementadas, nem que todas sejam necessárias em cada alteração. A especificação correspondente deve ser consultada conforme a tarefa. Skills técnicas não substituem validação humana especializada em saúde mental, direito, rede de proteção, privacidade, segurança e acessibilidade, especialmente antes de qualquer piloto com usuárias reais. O protótipo atual não é seguro nem funcional para esse uso.

---

## 2. Pré-requisitos e Instalação

Para executar e testar o projeto localmente no Windows:

### 2.1. Python (3.12 ou superior)
- **Instalador Oficial:** Baixe em [python.org/downloads](https://www.python.org/downloads/) e marque **"Add python.exe to PATH"**.
- **Via Terminal (winget):**
  ```powershell
  winget install Python.Python.3.12
  ```

### 2.2. uv (Gerenciador de Ambientes e Dependências Python)
- **Instalação via PowerShell:**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Via winget:**
  ```powershell
  winget install --id=astral-sh.uv -e
  ```

### 2.3. Node.js (Versão LTS v20+) e npm (v10+)
- **Instalador Oficial:** Baixe a versão LTS em [nodejs.org](https://nodejs.org/).
- **Via winget:**
  ```powershell
  winget install OpenJS.NodeJS.LTS
  ```

### 2.4. Verificação Rápida
Execute no terminal:
```powershell
python --version; uv --version; node --version; npm --version
```

---

## 3. Como Executar

Escolha uma das opções abaixo. As duas opções Docker iniciam o frontend e o backend; a opção local executa cada serviço em modo de desenvolvimento.

### Opção A — Docker Desktop

1. Instale e abra o Docker Desktop.
2. Em **Settings → Resources → WSL Integration**, habilite a distribuição Ubuntu caso use o backend WSL 2.
3. Abra um PowerShell na raiz do repositório e inicie os serviços:

   ```powershell
   docker compose up --build -d
   ```

4. Acompanhe os containers no painel **Containers** do Docker Desktop. O projeto aparece como `aurora`, com os serviços `frontend` e `backend`.

Para consultar logs e parar os serviços pelo terminal:

```powershell
docker compose logs -f
docker compose down
```

### Opção B — Docker pelo WSL

Use esta opção se o Docker CLI estiver instalado dentro de uma distribuição WSL, como no ambiente Ubuntu. No PowerShell do Windows, execute na raiz do repositório:

```powershell
wsl.exe -d Ubuntu -- sh -lc 'cd /mnt/c/Projetos/aurora && docker compose up --build -d'
```

Para acompanhar os logs ou parar os serviços:

```powershell
wsl.exe -d Ubuntu -- sh -lc 'cd /mnt/c/Projetos/aurora && docker compose logs -f'
wsl.exe -d Ubuntu -- sh -lc 'cd /mnt/c/Projetos/aurora && docker compose down'
```

Se o repositório estiver em outro local ou a distribuição tiver outro nome, ajuste `Ubuntu` e `/mnt/c/Projetos/aurora` para os valores correspondentes.

### Opção C — Execução local (sem Docker)

Pré-requisitos: Python 3.12+, `uv`, Node.js LTS 20+ e npm 10+. Abra **dois terminais** e mantenha ambos em execução.

No primeiro terminal, inicie o backend:

```powershell
Set-Location "C:\Projetos\aurora\src\backend"
uv sync
uv run python -m uvicorn aurora_backend.main:app --reload --host 127.0.0.1 --port 8000
```

No segundo terminal, inicie o frontend:

```powershell
Set-Location "C:\Projetos\aurora\src\frontend"
npm install
npm run dev -- --host 127.0.0.1
```

### Endereços locais

- **Interface web:** `http://127.0.0.1:5173`
- **API:** `http://127.0.0.1:8000/api/chat/messages`
- **Documentação interativa OpenAPI / Swagger:** `http://127.0.0.1:8000/docs`
- O frontend encaminha as chamadas `/api/*` ao backend. No Docker, isso ocorre pela rede interna do Compose; localmente, o Vite encaminha para `127.0.0.1:8000`.
- Nos dois modos Docker, as portas são publicadas somente em `127.0.0.1`.

### Publicar na EC2 com GitHub Actions

O workflow [deploy.yml](./.github/workflows/deploy.yml) testa o backend e compila o frontend em cada push para `develop` ou `release`, em cada PR para `release` e em cada tag `v*`. Pushes para `develop` e PRs só rodam essas verificações. No push para `release` (merge do PR `develop` → `release`) e nas tags `v*`, se os testes passarem, publica as imagens privadas `ghcr.io/jeffgitwebapp/aurora-backend` e `ghcr.io/jeffgitwebapp/aurora-frontend` no GHCR. Só o push para `release` implanta a versão na EC2; tags de release publicam as imagens sem implantar.

#### Preparar a instância Amazon Linux

- Instale e inicie Docker Engine e o plugin Docker Compose v2.
- Configure o Security Group para permitir HTTP TCP `80` de acordo com o público desejado. Restrinja SSH TCP `22`; runners hospedados pelo GitHub usam faixas de IP variáveis, então não abra SSH para `0.0.0.0/0` apenas para habilitar o deploy.
- O usuário `ec2-user` precisa conseguir executar Docker por `sudo`.
- O deploy publica HTTP sem TLS na porta 80. Antes de usar um domínio ou dados reais, configure HTTPS e revise os limites de segurança do protótipo. As respostas do chat são informação geral com fontes, não aconselhamento nem um serviço de atendimento.

#### Cadastrar secrets no GitHub

Crie o environment **`production`** em **Settings → Environments** e cadastre os valores abaixo em **Environment secrets** desse environment. O job de deploy do workflow usa `environment: production` para receber esses secrets:

| Secret | Valor |
|---|---|
| `EC2_HOST` | `ec2-3-137-205-13.us-east-2.compute.amazonaws.com` |
| `EC2_SSH_KEY` | Chave privada SSH autorizada para `ec2-user` |
| `EC2_KNOWN_HOSTS` | Chave de host SSH da EC2, previamente verificada |
| `GHCR_USERNAME` | Usuário GitHub que tem acesso de leitura aos pacotes |
| `GHCR_READ_TOKEN` | Personal Access Token (classic) com escopo `read:packages` |

Não coloque a chave SSH ou o token no repositório, no workflow ou em mensagens. Para obter a entrada de `EC2_KNOWN_HOSTS`, use `ssh-keyscan` e confirme a impressão digital da chave por um canal confiável antes de cadastrá-la. Se o SSH da instância não puder aceitar conexões dos runners do GitHub de forma restrita, use um runner com IP de saída fixo ou AWS Systems Manager em vez de abrir a porta 22 para a internet.

Depois de adicionar os secrets, faça o merge de um PR de `develop` para `release`. Acompanhe o workflow em **Actions**; após a publicação, a aplicação ficará em `http://ec2-3-137-205-13.us-east-2.compute.amazonaws.com`. O Compose de produção publica apenas o frontend na porta 80 e mantém o backend acessível pela rede interna. O arquivo [`docker-compose.prod.yml`](./docker-compose.prod.yml) é separado do Compose local para preservar a execução de desenvolvimento.

Para o passo a passo completo da instância, Docker/Compose, SSH, GHCR, secrets e publicação, consulte o [guia de deploy na EC2](./DEPLOY-EC2.md).

> [!TIP]
> **Resolução de problema no Windows / OneDrive:**  
> Caso o projeto seja clonado ou executado dentro de uma pasta sincronizada pelo OneDrive e o Vite apresente o erro `EPERM: operation not permitted, rmdir ...node_modules\.vite\deps`, isso ocorre pelo bloqueio temporário de arquivos pelo agente de sincronização. No diretório local padrão (`C:\Projetos\aurora`), esse bloqueio não ocorre. Se necessário em ambientes sincronizados, execute no terminal do frontend:
> ```powershell
> Remove-Item -Path "node_modules\.vite" -Recurse -Force -ErrorAction SilentlyContinue
> npm run dev -- --host 127.0.0.1
> ```
>
> **Erro `Port 5173 is already in use`:** já existe um processo escutando na porta usada pelo frontend. Antes de iniciar outro servidor, abra `http://127.0.0.1:5173` no navegador: o frontend pode já estar rodando. Se precisar reiniciá-lo, pare o servidor no terminal em que ele foi iniciado com `Ctrl+C`. Para identificar qual processo está usando a porta:
> ```powershell
> Get-NetTCPConnection -LocalPort 5173 -State Listen |
>   Select-Object LocalAddress, LocalPort, OwningProcess
> Get-Process -Id <PID>
> ```
> Se confirmar que é um processo antigo do frontend e não tiver acesso ao terminal original, encerre somente esse processo com `Stop-Process -Id <PID>`. Apagar `node_modules\.vite` ou executar `npm install` não libera uma porta ocupada.

---

## 4. Contrato da API

### `POST /api/chat/messages`

- **Requisição:**
  ```http
  POST /api/chat/messages
  Content-Type: application/json

  {"message": "mensagem enviada pela pessoa usuária"}
  ```
- **Resposta para mensagem válida (200 OK):**
  Exemplo de resposta com fonte (textos abreviados). Os demais desfechos usam os mesmos campos; veja [Motor de chat v1.2](#motor-de-chat-v12).
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "reply": "A Lei Maria da Penha ... [1]",
    "guidance": null,
    "triage_status": "no_acute_signal",
    "signals": [],
    "scope_status": "allowed",
    "out_of_scope_category": null,
    "offer": null,
    "conversation": null,
    "knowledge_status": "found",
    "sources": [
      {
        "id": "mmulheres-unfpa-2026-cartilha-lmp#causas",
        "title": "Lei Maria da Penha: Direitos das mulheres e meninas e como buscar ajuda (reedição)",
        "locator": "p. 7 (...)",
        "publisher": "Ministério das Mulheres ... e UNFPA",
        "url": "https://www.gov.br/mulheres/...",
        "version": "Reedição de fevereiro de 2026 ..."
      }
    ],
    "demo": true
  }
  ```

  | Desfecho | Campos que o identificam |
  |---|---|
  | Risco agudo ou indeterminado | `triage_status` ≠ `no_acute_signal`, `reply: null`, `guidance` e `signals` |
  | Fora do escopo | `scope_status: "out_of_scope"` e `out_of_scope_category` |
  | Conversa social | `conversation`: `greeting` \| `thanks` \| `farewell` |
  | Oferta do guia | `offer: "safety_guide"` |
  | Com fonte | `knowledge_status: "found"` e `sources` não vazio |
  | Sem fonte | `knowledge_status: "no_source"` e `sources: []` |

- **Resposta para mensagem vazia ou em branco (422 Unprocessable Entity):**
  ```http
  HTTP/1.1 422 Unprocessable Entity
  Content-Type: application/json

  {"detail": "A mensagem não pode estar vazia."}
  ```
- **Serviço indisponível (503):** falha do LLM, da seleção de trechos ou reprovação no guardrail de saída devolvem `{"detail": "O serviço de informações está indisponível no momento."}`.

### Motor de chat v1.2

O backend decide o que responder; o frontend só exibe o texto de `reply`, as fontes e os botões de navegação. A triagem de risco, o limite de escopo, a oferta do guia e as respostas de saudação continuam determinísticos e sem LLM em todos os motores. O motor é escolhido só por variável de ambiente (local: `src/backend/.env`, fora do git; EC2: `/opt/aurora/backend.env`, ver [DEPLOY-EC2.md](./DEPLOY-EC2.md)):

| Variável | Valores | Efeito |
|---|---|---|
| `AURORA_CHAT_ENGINE` | `fixtures` (padrão), `base`, `llm` | `fixtures`: frases de teste do protótipo; `base`: base curada com busca BM25, sem LLM; `llm`: BM25 + seleção de trechos e redação pelo LLM, com guardrail de saída |
| `AURORA_LLM_PROVIDER` | `gemini` (padrão), `claude` | Provedor do LLM no motor `llm`; trocar não exige mudança de código |
| `AURORA_LLM_MODEL` | padrão `gemini-3.5-flash-lite` | Modelo do provedor (ex.: `claude-opus-5-5`) |
| `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` | chave | Chave do provedor escolhido; nunca no repositório |
| `AURORA_AGENTIC_SEARCH` | `false` (padrão), `true` | Só no motor `llm`: o LLM pode pedir até 2 buscas extras com termos técnicos quando a mensagem usa palavras do dia a dia |

Valor inválido ou chave ausente impedem a subida do backend; não há troca silenciosa de motor. O log de subida mostra o motor ativo (`aurora.chat_engine: ...`).

**Base de conhecimento.** A versão vigente é a pasta `docs/aurora-base-rag/vX.YY` de maior número (ex.: `v0.03`). O backend lê um snapshot JSON gerado a partir dela; sempre que a base mudar ou uma nova versão for criada, regenere-o:

```powershell
cd src/backend
uv run python scripts/build_knowledge_snapshot.py
```

A CI falha se o snapshot não corresponder à versão vigente (`test_snapshot_matches_latest_base`).

**Respostas.** Com fonte, `reply` traz marcadores `[1]`, `[2]`… na ordem da lista `sources`. Sem fonte, fora do escopo, oferta do guia e saudação também trazem o texto em `reply`. Em risco agudo, `reply` é `null` e o frontend abre a tela de emergência. Falha do LLM ou do guardrail de saída devolve `503`, nunca uma resposta sem verificação.

**Avaliação.** Testes offline (sem rede) rodam na CI em todo push. O teste essencial com o LLM real ([eval-v1-2.yml](./.github/workflows/eval-v1-2.yml): 1 caso por categoria, menos de 2 minutos) roda nos PRs para `release` e sob demanda, e exige o secret `GEMINI_API_KEY` no repositório; sem ele, o job só emite um aviso. Localmente:

```powershell
cd src/backend
uv run --env-file .env python evals/v1_2/run_answer_eval.py --check
```

Plano e decisões: [plano-implementacao-adicionando-agente-aurora.md](./docs/plano-implementacao-adicionando-agente-aurora.md).

---

## 5. Validação e Qualidade do Código

### Validação do Backend (FastAPI)
A partir de `src/backend` (`Set-Location "C:\Projetos\aurora\src\backend"`):

```powershell
# Execução da suíte de testes
uv run python -m pytest

# Verificação estática de código (linter)
uv run python -m ruff check .

# Verificação de formatação
uv run python -m ruff format --check .

# Compilação de bytecode
uv run python -m compileall src
```

### Validação do Frontend (React + Vite)
A partir de `src/frontend` (`Set-Location "C:\Projetos\aurora\src\frontend"`):

```powershell
# Verificação estática de tipos TypeScript
npm run check

# Compilação e build de produção Vite
npm run build
```

---

## 6. Limitações e Privacidade

1. **Conversa anônima só em memória:** as mensagens existem apenas no estado React enquanto a aba estiver aberta. Ao recarregar (F5) ou fechar a página, o histórico é descartado. O frontend não grava a conversa em `localStorage`, `sessionStorage` ou cookies.
2. **Logs só com metadados:** o `decision_trace` registra motor, modelo, versão da base e do prompt, tokens, duração e ids das fontes. Mensagem, resposta e trechos nunca vão ao log.
3. **Provedor externo de LLM:** no motor `llm`, a mensagem e os trechos selecionados são enviados ao provedor configurado (Gemini ou Claude). Nos motores `fixtures` e `base` não há chamada externa. Triagem, escopo, small talk, oferta e guardrail de saída nunca usam LLM.
4. **Área logada em memória do processo:** contas, conversas salvas, diário e plano de segurança ficam na memória do backend (conteúdo cifrado com AES-GCM) e se perdem quando o processo reinicia. Não há banco de dados.
5. **Regras provisórias:** as listas de triagem, escopo, oferta e relato pessoal são provisórias e dependem de curadoria especializada; a base de conhecimento tem trechos ainda em revisão (por isso as respostas trazem `demo: true`).
