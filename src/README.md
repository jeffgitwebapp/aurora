# Projeto Aurora — Protótipo Local

Scaffold e protótipo local do projeto Aurora com frontend em React e backend em Python/FastAPI, conectados via HTTP REST local.

> [!WARNING]
> **Aviso ético e de segurança:** Este projeto é um protótipo estritamente local de demonstração técnica com resposta constante. **Não é seguro nem funcional para uso com pessoas em situação de violência.** Não oferece orientação, apoio emergencial, camuflagem ou garantias de proteção.

---

## 1. Pré-requisitos e Como Instalá-los

Para executar e testar o projeto localmente, são necessárias as seguintes ferramentas instaladas na sua máquina (as instruções abaixo são focadas em Windows):

### 1.1. Python (3.12 ou superior)
O backend foi construído para Python 3.12+.
* **Opção A (Instalador Oficial - Recomendado):**
  1. Acesse o site oficial: [python.org/downloads](https://www.python.org/downloads/).
  2. Baixe o instalador da versão mais recente do Python 3.12+.
  3. **Muito importante:** Na primeira tela do instalador, marque a caixa de seleção **"Add python.exe to PATH"** antes de clicar em "Install Now".
* **Opção B (Via Terminal PowerShell / winget):**
  ```powershell
  winget install Python.Python.3.12
  ```
* **Como verificar se foi instalado:**
  ```powershell
  python --version
  ```

---

### 1.2. uv (Gerenciador de Dependências e Ambientes Python)
O `uv` é uma ferramenta extremamente rápida para resolução de dependências, geração de lockfile e ambientes virtuais.
* **Instalação via PowerShell (Recomendado pela Astral):**
  Abra o PowerShell e execute o comando:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
* **Opção alternativa via winget:**
  ```powershell
  winget install --id=astral-sh.uv -e
  ```
* **Como verificar se foi instalado:**
  ```powershell
  uv --version
  ```
  *(Nota: Se o comando `uv` não for reconhecido imediatamente, feche e reabra o terminal para atualizar as variáveis de ambiente).*

---

### 1.3. Node.js (Versão LTS v20+) e npm (v10+)
O frontend em React com Vite utiliza o ecossistema Node.js e o gerenciador de pacotes `npm`.
* **Opção A (Instalador Oficial - Recomendado):**
  1. Acesse: [nodejs.org](https://nodejs.org/).
  2. Baixe a versão com o selo **LTS** (Long Term Support).
  3. Execute o instalador mantendo as opções padrão e conclua o processo. O `npm` já é instalado automaticamente junto com o Node.js.
* **Opção B (Via Terminal PowerShell / winget):**
  ```powershell
  winget install OpenJS.NodeJS.LTS
  ```
* **Como verificar se foram instalados:**
  ```powershell
  node --version
  npm --version
  ```

---

### 1.4. Verificação Rápida de Todos os Pré-requisitos
Para garantir que seu ambiente está 100% pronto antes de rodar os projetos, execute o comando abaixo no PowerShell:

```powershell
python --version; uv --version; node --version; npm --version
```
Se todos retornarem seus respectivos números de versão sem erros, você pode prosseguir para a execução!

---

## 2. Estrutura Arquitetural

O projeto segue os princípios de monólito modular, Bounded Context (DDD Estratégico) e Vertical Slice Architecture:

```text
src/
├── .gitignore
├── README.md
├── backend/                            # FastAPI + uv
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── src/
│   │   └── aurora_backend/
│   │       ├── main.py                 # Cria aplicação FastAPI e registra slices
│   │       └── contexts/
│   │           └── conversation/       # Bounded Context: Conversa
│   │               └── features/
│   │                   └── send_message/ # Vertical Slice: EnviarMensagem
│   │                       ├── router.py   # Adaptador de entrada HTTP
│   │                       ├── schemas.py  # Contratos Pydantic de entrada e saída
│   │                       └── handler.py  # Lógica de negócio / resposta fixa
│   └── tests/
│       └── test_send_message.py        # Suíte de testes automatizados
└── frontend/                           # React + Vite + TypeScript
    ├── package.json
    ├── package-lock.json
    ├── index.html
    ├── vite.config.ts                  # Proxy reverso local (/api -> :8000)
    ├── tsconfig.json
    └── src/
        ├── main.tsx                    # Ponto de entrada React
        ├── app/
        │   └── App.tsx                 # Composição da aplicação
        ├── features/
        │   └── chat/                   # Módulo da feature de chat
        │       ├── ChatPage.tsx        # Gerenciamento de estado efêmero e fluxo
        │       ├── types.ts            # Tipos de domínio e UI da feature
        │       ├── api/
        │       │   └── chatApi.ts      # Cliente HTTP REST
        │       └── components/
        │           ├── MessageList.tsx # Exibição acessível das mensagens
        │           └── MessageComposer.tsx # Entrada e disparo de mensagem
        └── styles.css                  # Estilos acessíveis e responsivos
```

---

## 3. Contrato da API

### `POST /api/chat/messages`

**Requisição:**
```http
POST /api/chat/messages
Content-Type: application/json

{"message": "mensagem enviada pela pessoa usuária"}
```

**Resposta para mensagem válida (200 OK):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"reply": "Este chatbot está em desenvolvimento."}
```

**Resposta para mensagem vazia ou em branco (422 Unprocessable Entity):**
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{"detail": "A mensagem não pode ser vazia."}
```

---

## 4. Como Executar Localmente

> [!IMPORTANT]
> **Atenção:** Você precisará abrir **dois terminais distintos** (duas janelas ou abas separadas do PowerShell ou Prompt de Comando - CMD) e mantê-los abertos ao mesmo tempo:
> 1. **Terminal 1:** Executa o servidor backend Python / FastAPI (porta 8000).
> 2. **Terminal 2:** Executa o servidor de desenvolvimento frontend React / Vite (porta 5173).

---

### Terminal 1 — Backend (FastAPI)

Abra a primeira janela do PowerShell/CMD e execute:

```powershell
Set-Location "C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Projeto Mestrado\src\backend"
uv sync
uv run uvicorn aurora_backend.main:app --reload --host 127.0.0.1 --port 8000
```

- **Endpoint local:** `http://127.0.0.1:8000/api/chat/messages`
- **Documentação OpenAPI / Swagger:** `http://127.0.0.1:8000/docs`
- Mantenha este terminal aberto para que o servidor responda às requisições.

---

### Terminal 2 — Frontend (React + Vite)

Abra a segunda janela do PowerShell/CMD e execute:

```powershell
Set-Location "C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Projeto Mestrado\src\frontend"
npm install
npm run dev -- --host 127.0.0.1
```

- **Interface web:** `http://127.0.0.1:5173`
- O Vite encaminha automaticamente as chamadas `/api/*` para o backend em `http://127.0.0.1:8000`.

> [!TIP]
> **Resolução de problema no Windows / OneDrive:**  
> Caso o Vite apresente o erro `EPERM: operation not permitted, rmdir ...node_modules\.vite\deps`, isso ocorre pelo bloqueio temporário de arquivos pelo agente de sincronização do OneDrive. Para resolver, execute no terminal do frontend:
> ```powershell
> Remove-Item -Path "node_modules\.vite" -Recurse -Force -ErrorAction SilentlyContinue
> npm run dev -- --host 127.0.0.1
> ```

---

## 5. Validação e Qualidade do Código

### Validação do Backend

A partir de `src/backend`:

```powershell
# Execução da suíte de testes
uv run pytest

# Verificação estática de código (linter)
uv run ruff check .

# Verificação de formatação
uv run ruff format --check .

# Compilação de bytecode
uv run python -m compileall src
```

### Validação do Frontend

A partir de `src/frontend`:

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
3. **Sem dependências externas:** Não há integração com LLMs de terceiros, provedores em nuvem ou bancos de dados externos.
4. **Resposta determinística:** O backend retorna estritamente a resposta constante `Este chatbot está em desenvolvimento.` para qualquer entrada válida.

