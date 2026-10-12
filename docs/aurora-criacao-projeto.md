# Plano de Implementação — Projeto Aurora

**Status:** plano aprovado para execução local; nenhum código do projeto foi criado por este documento.  
**Escopo:** scaffold local de frontend React e backend Python, conectados por HTTP, com uma única funcionalidade: enviar uma mensagem e receber sempre a resposta fixa definida abaixo.

## 1. Resultado esperado

Criar o projeto em:

```text
C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Projeto Mestrado\src
```

O diretório `src` será a raiz do projeto Aurora e conterá `backend/` e `frontend/`. Ao final, ambos poderão ser iniciados localmente em processos separados, e a interface React enviará mensagens ao backend FastAPI.

Para toda mensagem não vazia, o backend responderá exatamente:

```text
Este chatbot está em desenvolvimento.
```

O frontend exibirá a mensagem enviada e a resposta recebida. O histórico existirá apenas no estado em memória da página e desaparecerá ao recarregá-la ou fechá-la.

## 2. Decisões de implementação

- **Backend:** Python 3.12 ou superior, FastAPI, Uvicorn e `uv` para ambiente, dependências e lockfile.
- **Frontend:** React, Vite, TypeScript e `npm`; versões resolvidas no momento da execução serão registradas em `package-lock.json`.
- **Integração local:** REST/JSON. O endpoint será `POST /api/chat/messages`; o servidor Vite encaminhará `/api` ao backend em `127.0.0.1:8000`.
- **Bounded context:** `Conversa`, representado pelo módulo Python `contexts/conversation`.
- **Vertical Slice:** `EnviarMensagem`, responsável pelo endpoint, schemas de entrada/saída e handler desta interação.
- **DDD tático:** não criar agregado, repositório ou banco de dados para uma resposta constante sem estado nem invariantes. A fronteira estratégica do contexto e o corte vertical da funcionalidade ficam explícitos; o modelo tático só deve surgir quando regras de negócio reais o justificarem.
- **Frontend modular:** composição da aplicação separada da feature `chat`; dentro da feature, separar chamada HTTP, tipos e componentes de apresentação.
- **Sem dependências externas de negócio:** não usar provedor de LLM, banco, serviço em nuvem, chave secreta ou integração de terceiros.

## 3. Contexto arquitetural e limites desta entrega

Os documentos `c4-aurora-mvp.md`, `arquitetura_operacionalizada_aurora.md`, `aurora-arquitetura-4mais1.drawio`, `requisitos-aurora.md` e `analise-comparativa-solucoes.md` descrevem o propósito do Aurora, seus limites éticos, anonimato e uma arquitetura alvo mais ampla. Os diagramas também registram PWA, arquitetura hexagonal, LLM/RAG, triagem, guardrails, catálogo e operação em nuvem.

A instrução atual reduz deliberadamente a implementação a um chatbot de demonstração com resposta fixa e define React no frontend e monólito modular Vertical Slice + DDD no backend. Portanto, para esta entrega:

- O princípio de módulos/contexto e a organização por feature são preservados, mas não se implementam os fluxos futuros dos documentos.
- Não implementar PWA, service worker, camuflagem, Saída Rápida, funcionamento offline, triagem, classificador de emergência, encaminhamento, catálogo, RAG, LLM, guardrails funcionais, painel administrativo, autenticação, persistência ou deploy em nuvem.
- Não registrar conteúdo de mensagens em logs, banco, arquivos, cookies, `localStorage`, `sessionStorage` ou telemetria. O corpo só transita entre navegador e API local para produzir a resposta fixa.
- A resposta de demonstração não oferece orientação ou proteção. Este scaffold não deve ser exposto a usuárias reais nem apresentado como implementação segura ou funcional do Aurora descrito nos documentos.
- Não alterar os documentos de arquitetura, requisitos, backlog ou skills existentes. Não criar nenhuma feature além de `EnviarMensagem`.

## 4. Contrato HTTP

**Requisição**

```http
POST /api/chat/messages
Content-Type: application/json
```

```json
{"message":"mensagem enviada pela pessoa usuária"}
```

**Resposta para mensagem não vazia**

```http
200 OK
Content-Type: application/json
```

```json
{"reply":"Este chatbot está em desenvolvimento."}
```

Mensagens vazias ou compostas apenas por espaços serão rejeitadas com `422 Unprocessable Entity`; a interface impedirá o envio nesses casos. Nenhuma resposta depende do conteúdo da mensagem. Não adicionar ID de sessão, autenticação ou histórico no servidor.

## 5. Manifesto de arquivos do projeto

Criar somente os arquivos abaixo dentro de `src/`. `uv.lock` e `package-lock.json` são gerados pelos respectivos gerenciadores e devem ser versionados. `node_modules`, ambientes virtuais, caches e bundles são artefatos locais ignorados pelo Git.

```text
src/
├── .gitignore
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock                         # Gerado por uv lock/sync
│   ├── src/
│   │   └── aurora_backend/
│   │       ├── __init__.py
│   │       ├── main.py                 # Cria FastAPI e registra a slice
│   │       └── contexts/
│   │           └── conversation/
│   │               ├── __init__.py     # Fronteira do bounded context
│   │               └── features/
│   │                   └── send_message/
│   │                       ├── __init__.py
│   │                       ├── router.py   # Adaptador HTTP da feature
│   │                       ├── schemas.py  # Contratos Pydantic da API
│   │                       └── handler.py  # Retorno fixo e validação da entrada
│   └── tests/
│       └── test_send_message.py        # Testes da API e resposta fixa
└── frontend/
    ├── package.json
    ├── package-lock.json               # Gerado por npm install
    ├── index.html
    ├── vite.config.ts                  # Proxy local /api -> FastAPI
    ├── tsconfig.json
    └── src/
        ├── main.tsx                    # Inicialização React
        ├── app/
        │   └── App.tsx                 # Composição da aplicação
        ├── features/
        │   └── chat/
        │       ├── ChatPage.tsx         # Estado efêmero e fluxo da tela
        │       ├── types.ts            # Tipos da feature
        │       ├── api/
        │       │   └── chatApi.ts       # Cliente HTTP do backend
        │       └── components/
        │           ├── MessageList.tsx  # Exibição de mensagens/estados
        │           └── MessageComposer.tsx # Campo e ação de envio
        └── styles.css                  # Estilos responsivos e acessíveis
```

Não manter arquivos de demonstração padrão do Vite, como logos, contadores ou componentes de exemplo. Não criar pastas vazias de domínio, aplicação ou infraestrutura. Caso o template utilizado gere arquivos adicionais, removê-los se não forem necessários ao manifesto e às verificações definidas aqui.

## 6. Plano de execução

Executar as etapas em ordem. O executor deve fazer alterações somente no diretório `src/`, além deste próprio plano que já existe na raiz.

### Etapa 1 — Pré-requisitos e proteção contra sobrescrita

1. Confirmar Windows PowerShell, Python 3.12+, `uv`, Node.js LTS e `npm` disponíveis:

```powershell
python --version
uv --version
node --version
npm --version
```

2. Definir o destino e verificar seu estado:

```powershell
$ProjectRoot = "C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Projeto Mestrado\src"
Test-Path $ProjectRoot
```

3. Se `src` já existir e contiver arquivos, **parar antes de escrever** e solicitar orientação. Não apagar, substituir ou reorganizar conteúdo existente. Se não existir, criá-lo e continuar.

**Validação:** os comandos de ferramentas retornam versões; o destino está ausente ou vazio; nada fora do destino será alterado.

### Etapa 2 — Backend Python e estrutura arquitetural

1. Criar a estrutura `backend/src/aurora_backend/contexts/conversation/features/send_message` e `backend/tests`.
2. Criar `backend/pyproject.toml` com:
   - projeto `aurora-backend` e requisito Python `>=3.12`;
   - dependências de execução `fastapi` e `uvicorn[standard]`;
   - dependências de desenvolvimento `pytest`, `httpx` e `ruff`;
   - configuração mínima do pytest para descobrir `tests/` e importar o pacote de `src/`;
   - configuração Ruff para Python 3.12, sem ignores amplos.
3. Implementar a slice `send_message`:
   - `schemas.py`: request com campo `message` e response com campo `reply`;
   - `handler.py`: rejeitar entrada vazia após `strip()` e devolver sempre a resposta fixa para entrada válida;
   - `router.py`: endpoint `POST /api/chat/messages`, delegando ao handler e traduzindo entrada inválida para erro HTTP 422;
   - `main.py`: criar a aplicação FastAPI e incluir o router da feature.
4. Não criar conexão de banco, persistência, LLM, logs de corpo de requisição, autenticação ou middleware não exigidos.
5. Resolver dependências e gerar o lockfile:

```powershell
Set-Location "$ProjectRoot\backend"
uv lock
uv sync
```

6. Validar o backend:

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall src
```

**Critérios para avançar:** os testes passam; Ruff não encontra erros; formatação está correta; compilação não falha. Corrigir problemas antes de iniciar o frontend.

### Etapa 3 — Frontend React modular

1. Criar e inicializar `frontend/` com npm; instalar dependências React/Vite/TypeScript e gerar `package-lock.json`:

```powershell
New-Item -ItemType Directory -Force -Path "$ProjectRoot\frontend"
Set-Location "$ProjectRoot\frontend"
npm init -y
npm install react react-dom
npm install --save-dev vite typescript @vitejs/plugin-react @types/react @types/react-dom
```

2. Editar `package.json`: definir o nome `aurora-frontend`, `"type": "module"` e os scripts `"dev": "vite"`, `"check": "tsc --noEmit"` e `"build": "tsc --noEmit && vite build"`. Não adicionar dependências além das listadas neste plano.
3. Criar `vite.config.ts` para escutar em `127.0.0.1:5173`, falhar em vez de trocar silenciosamente de porta e encaminhar `/api` para `http://127.0.0.1:8000`.
4. Criar `tsconfig.json` com modo estrito, JSX React e verificação do código em `src/`.
5. Implementar os módulos do manifesto:
   - `main.tsx` monta `App`;
   - `App.tsx` compõe a página da feature de chat;
   - `ChatPage.tsx` mantém apenas estado React em memória, envia a mensagem e mostra estados de envio e erro de rede;
   - `chatApi.ts` envia JSON para `/api/chat/messages` e interpreta `{ reply }`;
   - `types.ts` define mensagem de interface com papel `user` ou `assistant`;
   - `MessageComposer.tsx` oferece campo rotulado e botão de envio, bloqueando texto vazio e envio duplicado enquanto aguarda;
   - `MessageList.tsx` apresenta mensagens sem interpretar o conteúdo como HTML;
   - `styles.css` mantém a interface mínima, responsiva, navegável por teclado e com rótulos acessíveis.
6. Não usar `localStorage`, `sessionStorage`, cookies, analytics, bibliotecas de UI ou chamadas para domínios externos.
7. Executar verificações:

```powershell
Set-Location "$ProjectRoot\frontend"
npm install
npm run check
npm run build
```

**Critérios para avançar:** instalação termina com lockfile, verificação TypeScript passa e o bundle de produção é criado sem erros.

### Etapa 4 — Integração ponta a ponta local

1. Criar `src/.gitignore` para ignorar ambientes Python, `__pycache__`, caches de teste/lint, `node_modules`, `dist`, arquivos `.env` e logs; não ignorar os lockfiles.
2. Criar `src/README.md` contendo pré-requisitos, comandos abaixo, endpoint/contrato, estrutura resumida e limitações do protótipo. Não incluir segredos.
3. Abrir um terminal PowerShell para o backend:

```powershell
Set-Location "$ProjectRoot\backend"
uv run uvicorn aurora_backend.main:app --reload --host 127.0.0.1 --port 8000
```

4. Em outro terminal, iniciar o frontend:

```powershell
Set-Location "$ProjectRoot\frontend"
npm run dev -- --host 127.0.0.1
```

5. Confirmar a API independentemente do navegador:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chat/messages" -Method Post -ContentType "application/json" -Body '{"message":"Olá"}'
```

O resultado deve conter `reply` igual a `Este chatbot está em desenvolvimento.`.

6. Abrir `http://127.0.0.1:5173`, enviar uma mensagem e confirmar que a interface exibe a mensagem do usuário e a resposta devolvida pelo backend. Repetir com outra mensagem: a resposta deve ser idêntica. Atualizar a página: a conversa anterior deve desaparecer.
7. Simular backend indisponível e confirmar mensagem de erro compreensível na interface, sem travamento ou conteúdo fictício apresentado como resposta do servidor.

**Critérios finais:** os dois processos iniciam localmente; proxy Vite/API funciona; a interação completa satisfaz o contrato; os estados vazio, aguardando e falha são utilizáveis; não há dependência de rede externa para instalar/rodar depois que dependências estiverem instaladas.

## 7. Como executar depois da implementação

Pré-requisitos: Python 3.12+, `uv`, Node.js LTS e `npm`.

**Terminal 1 — backend**

```powershell
Set-Location "C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Projeto Mestrado\src\backend"
uv sync
uv run uvicorn aurora_backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — frontend**

```powershell
Set-Location "C:\Users\jephe\OneDrive\Mestrado Eng. de Software\Disciplinas\Projeto Mestrado\src\frontend"
npm install
npm run dev -- --host 127.0.0.1
```

Acessar `http://127.0.0.1:5173`. Documentação OpenAPI local do FastAPI ficará disponível em `http://127.0.0.1:8000/docs`.

## 8. Critérios de aceite da entrega

- [ ] O projeto foi criado somente em `Projeto Mestrado/src/`, sem modificar documentos existentes.
- [ ] Existem somente o backend, o frontend e os arquivos listados neste plano; não há feature adicional.
- [ ] Backend é Python/FastAPI, organizado como monólito modular com bounded context `Conversa` e slice `EnviarMensagem`.
- [ ] Frontend é React/TypeScript/Vite, organizado em módulos da aplicação e da feature `chat`.
- [ ] Toda mensagem não vazia recebe exatamente `Este chatbot está em desenvolvimento.`.
- [ ] A comunicação frontend/backend ocorre por HTTP local e não depende de LLM, banco de dados ou serviços externos.
- [ ] Não há persistência de mensagens nem gravação deliberada do conteúdo em logs ou armazenamento do navegador.
- [ ] Testes backend, Ruff, verificação TypeScript e build frontend passam.
- [ ] O README do projeto explica instalação, execução, validação e limitações.
- [ ] O sistema é identificado como protótipo local, não pronto para uso com pessoas em situação de violência.
