# Projeto Aurora

Plataforma de psicoeducação e informação para mulheres em situação de violência psicológica.

> [!WARNING]
> **Aviso ético e de segurança:** Este projeto contém um protótipo estritamente local de demonstração técnica com resposta constante. **Não é seguro nem funcional para uso com pessoas em situação de violência.** Não oferece orientação, apoio emergencial, camuflagem ou garantias de proteção.

---

## 1. Visão Geral e Estrutura Arquitetural

O projeto segue os princípios de monólito modular, Bounded Context (DDD Estratégico) e Vertical Slice Architecture:

- **Bounded Context:** `Conversa` (`contexts/conversation`).
- **Vertical Slice:** `EnviarMensagem` (`features/send_message`), concentrando rotas, validação e lógica da funcionalidade.
- **Frontend Modular:** Separação entre composição (`app/App.tsx`), regras e estado de tela (`features/chat/ChatPage.tsx`), cliente de API (`api/chatApi.ts`) e componentes de apresentação desacoplados.

### Estrutura do Repositório

```text
aurora/
├── docs/                               # Documentação e Engenharia de Requisitos / Arquitetura
│   ├── analise-comparativa-solucoes.md # Comparativo com 13 iniciativas existentes
│   ├── arquitetura_operacionalizada_aurora.md # Fitness functions e gates de qualidade
│   ├── aurora-arquitetura-4mais1.drawio       # Visões arquiteturais 4+1
│   ├── aurora-criacao-projeto.md       # Plano de scaffold inicial
│   ├── backlog-aurora.md               # Backlog de épicos (E1 a E13)
│   ├── c4-aurora-mvp.drawio            # Modelagem arquitetural C4
│   └── requisitos-aurora.md            # Requisitos Funcionais e Não-Funcionais (ISO 25010)
├── src/                                # Código-fonte da aplicação
│   ├── .gitignore
│   ├── backend/                        # FastAPI + uv (Python 3.12+)
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   ├── src/aurora_backend/
│   │   │   ├── main.py                 # Cria aplicação FastAPI e registra slices
│   │   │   └── contexts/
│   │   │       └── conversation/       # Bounded Context: Conversa
│   │   │           └── features/
│   │   │               └── send_message/ # Vertical Slice: EnviarMensagem
│   │   │                   ├── router.py   # Adaptador de entrada HTTP
│   │   │                   ├── schemas.py  # Contratos Pydantic de entrada e saída
│   │   │                   └── handler.py  # Lógica de negócio / resposta fixa
│   │   └── tests/
│   │       └── test_send_message.py    # Suíte de testes automatizados
│   └── frontend/                       # React 19 + TypeScript + Vite
│       ├── package.json
│       ├── package-lock.json
│       ├── index.html
│       ├── vite.config.ts              # Proxy reverso local (/api -> :8000)
│       ├── tsconfig.json
│       └── src/
│           ├── main.tsx                # Ponto de entrada React
│           ├── app/
│           │   └── App.tsx             # Composição da aplicação
│           ├── features/
│           │   └── chat/               # Módulo da feature de chat
│           │       ├── ChatPage.tsx    # Gerenciamento de estado efêmero e fluxo
│           │       ├── types.ts        # Tipos de domínio e UI da feature
│           │       ├── api/
│           │       │   └── chatApi.ts  # Cliente HTTP REST
│           │       └── components/
│           │           ├── MessageList.tsx # Exibição acessível das mensagens
│           │           └── MessageComposer.tsx # Entrada e disparo de mensagem
│           └── styles.css              # Estilos acessíveis e responsivos
└── LICENSE                             # Licença do projeto
```

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

## 3. Como Executar Localmente

Abra **dois terminais distintos** (PowerShell ou Prompt de Comando) e mantenha-os em execução simultaneamente:

### Terminal 1 — Backend (FastAPI)

```powershell
# A partir da raiz do repositório (C:\Projetos\aurora):
Set-Location "src/backend"
# Ou especificando o caminho absoluto:
# Set-Location "C:\Projetos\aurora\src\backend"

uv sync
uv run python -m uvicorn aurora_backend.main:app --reload --host 127.0.0.1 --port 8000
```

- **Endpoint local:** `http://127.0.0.1:8000/api/chat/messages`
- **Documentação interativa OpenAPI / Swagger:** `http://127.0.0.1:8000/docs`

---

### Terminal 2 — Frontend (React + Vite)

```powershell
# A partir da raiz do repositório (C:\Projetos\aurora):
Set-Location "src/frontend"
# Ou especificando o caminho absoluto:
# Set-Location "C:\Projetos\aurora\src\frontend"

npm install
npm run dev -- --host 127.0.0.1
```

- **Interface web:** `http://127.0.0.1:5173`
- O Vite encaminha automaticamente as chamadas `/api/*` para o backend em `http://127.0.0.1:8000`.

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
  A API aguarda 10 segundos para simular o processamento antes de responder.
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"reply": "Este chatbot está em desenvolvimento."}
  ```
- **Resposta para mensagem vazia ou em branco (422 Unprocessable Entity):**
  ```http
  HTTP/1.1 422 Unprocessable Entity
  Content-Type: application/json

  {"detail": "A mensagem não pode ser vazia."}
  ```

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

1. **Estado puramente em memória:** As mensagens existem exclusivamente no estado React enquanto a aba estiver aberta. Ao recarregar (F5) ou fechar a página, todo o histórico é descartado.
2. **Zero persistência:** Nenhuma mensagem é registrada em banco de dados, arquivos de log, `localStorage`, `sessionStorage`, cookies ou telemetria.
3. **Sem dependências externas de negócio:** Sem provedores externos de LLM, serviços em nuvem ou bancos de dados externos.
4. **Resposta determinística:** O backend retorna estritamente a resposta constante `Este chatbot está em desenvolvimento.` para qualquer entrada válida.
