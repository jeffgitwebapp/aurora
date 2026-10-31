# Contratos de Integração e Padrão de Mocks — Aurora

**Status:** contrato técnico aprovado pela usuária para o protótipo em 31/10/2026; conteúdo e comportamento de domínio continuam sujeitos às validações profissionais registradas em J-00
**Escopo:** contratos do protótipo funcional com frontend React/TypeScript e backend FastAPI; sem integrações reais, persistência ou alegação de segurança para uso real
**Rastreabilidade:** [Plano de implementação — J-01](./plano-implementacao-jornada-usuario.md), [Jornada do Usuário](./jornada-do-usuario.md), [Requisitos Aurora](../requisitos-aurora.md), [Backlog Aurora](../backlog-aurora.md), [Arquitetura operacionalizada](../arquitetura_operacionalizada_aurora.md)

## 1. Objetivo

Definir a fronteira entre a interface, os casos de uso do backend e os adaptadores simulados, mantendo contratos tipados, erros previsíveis e possibilidade de substituir mocks por integrações futuras.

Esta proposta não implementa triagem, RAG, guardrails, catálogo, contas ou persistência. Ela especifica a forma de comunicação e os dados que cada capacidade poderá trocar, respeitando o que está aprovado e deixando explícitas as decisões pendentes.

## 2. Princípios obrigatórios

1. **Preservar o padrão existente:** monólito modular, bounded context e organização por feature/vertical slice. A API HTTP é um adaptador; regras de domínio não importam FastAPI nem SDK de provedor.
2. **Orquestrar segurança antes de conteúdo:** o caso de uso conversacional consulta a triagem antes de recuperação/geração. Resultado de risco agudo ou indeterminado não pode cair no caminho informativo por sucesso-shaped fallback.
3. **Sem estado persistente anônimo no servidor:** nenhuma conversa, relato, sessão, classificação ou resposta fica em banco, arquivo, cache durável ou log. O histórico é mantido somente no estado em memória do frontend; o backend recebe somente a mensagem atual. Nenhum `session_id` é necessário neste protótipo.
4. **Sem conteúdo livre em logs ou erros:** logs técnicos podem registrar nome do caso de uso, duração e resultado técnico agregado, nunca mensagem, contexto, localização ou fontes derivadas do relato.
5. **Mocks não inferem segurança:** mocks não analisam texto livre para determinar risco, saúde, direitos ou necessidade. Os cenários são escolhidos por fixtures de teste/injeção do adaptador, nunca por palavras mágicas em mensagens de usuárias.
6. **Sem chamadas externas:** mock não acessa LLM, RAG, banco, geolocalização, catálogo remoto ou serviço de emergência.
7. **Dados demonstrativos identificados:** fixtures de conteúdo e serviços indicam `demo: true` e devem ser visualmente apresentadas como demonstração. Um mock não comprova acurácia, atualidade, disponibilidade ou validade clínica/jurídica.
8. **Falha explícita:** timeout, indisponibilidade, ausência de fonte, incerteza e falha de formato são estados distintos. Nunca converter erro em resposta informativa ou ausência de risco.
9. **Evolução sem contratos especulativos de conta:** os contratos de autenticação e persistência não são definidos aqui; devem ser detalhados quando L-01/L-02 forem priorizados e suas regras aprovadas.

## 3. Fronteiras e direção das chamadas

```text
React / TypeScript
  ├─ HTTP client: valida status, JSON e formato; não contém regra de domínio
  └─ FastAPI HTTP (mesma origem /api)
       └─ caso de uso / vertical slice
            ├─ porta de triagem → mock injetável
            ├─ porta de guardrail → mock injetável
            ├─ porta de recuperação/conteúdo → mock injetável
            └─ porta de catálogo → mock injetável
```

- O frontend chama somente rotas de aplicação documentadas; não chama adaptadores internos ou provedores.
- A triagem e o guardrail são capacidades internas do backend, não endpoints que o cliente possa contornar no fluxo da conversa.
- O adaptador de catálogo é chamado apenas após uma ação explícita de encaminhamento. A localização é município/UF digitado voluntariamente; não há localização automática.
- Cada capacidade possui tipos de entrada/saída próprios. O caso de uso coordena a sequência e mapeia o resultado para uma resposta de API.
- O estado de conversa existe apenas no frontend enquanto a página está aberta. O backend não recebe mensagens anteriores nem as usa para construir respostas.

## 4. Contrato HTTP existente

O scaffold atual implementa `POST /api/chat/messages`.

### Requisição atual

```json
{
  "message": "texto livre da usuária"
}
```

### Resposta atual

```json
{
  "reply": "texto simulado com aviso de protótipo"
}
```

O campo `message` é obrigatório e não pode ser vazio ou só conter espaços. A API atual usa `422` para entrada inválida e `200` para entrada válida. O frontend atual valida `reply` como string. Esse contrato descreve o scaffold, não o contrato funcional completo de conversa definido nas seções seguintes. Não se deve presumir que a resposta simulada atual implementa triagem, fontes ou guardrails.

### Compatibilidade aprovada

No protótipo, evoluir `POST /api/chat/messages` de forma coordenada no backend e no frontend quando a tarefa C-01 implementar o fluxo completo. Não há compatibilidade externa a preservar e não serão mantidas duas rotas para o mesmo caso de uso. Atualizar schemas, cliente, documentação OpenAPI e testes no mesmo conjunto de alterações.

## 5. Contratos internos de domínio

Os exemplos são formas conceituais em JSON/TypeScript. Nomes de enum e campos ainda precisam ser alinhados com as decisões de produto e revisão especializada antes da implementação.

### 5.1 Entrada de mensagem conversacional

Decisão aprovada: o frontend envia somente a mensagem atual. As mensagens anteriores permanecem no estado React em memória para apresentação e retorno, mas não são transmitidas ao backend neste contrato.

```json
{
  "message": "mensagem atual"
}
```

Restrições:

- `message` é obrigatória e não vazia após `strip`.
- O backend processa cada mensagem sem contexto de mensagens anteriores; respostas contextuais não são prometidas nesta etapa.
- O cliente não envia `history`, `session_id`, identificador de pessoa ou outros metadados de sessão.
- Corpos HTTP não devem ser incluídos em logs, traces ou métricas.
- A UI não deve mandar localização dentro do texto de histórico se a usuária não a forneceu.

Se uma integração futura exigir contexto acumulado no backend/provedor, será necessário revisar este contrato e sua análise de privacidade antes de transmitir histórico. Não alterar esta regra implicitamente durante C-01.

### 5.2 Resultado de triagem

```ts
type TriageStatus = "acute" | "indeterminate" | "no_acute_signal";

interface TriageResult {
  status: TriageStatus;
  signals: Array<"suicidal_ideation" | "ongoing_assault" | "death_threat" | "weapon" | "injury" | "imminent_act">;
}
```

`no_acute_signal` significa apenas que o classificador não sinalizou os casos cobertos; não deve ser apresentado como garantia de segurança. A implementação real do classificador, perguntas complementares e comportamento de incerteza dependem de validação de domínio. Um mock não pode ser usado para declarar o CA-02 atendido.

### 5.3 Recuperação e fontes

```ts
interface SourceReference {
  id: string;
  title: string;
  publisher: string;
  publishedAt?: string;
  version?: string;
  url?: string;
}

type KnowledgeResult =
  | { status: "found"; answer: string; sources: SourceReference[]; demo: boolean }
  | { status: "no_source"; demo: boolean };
```

- `found` exige ao menos uma fonte identificável e aprovada; o gerador não cria metadados de fonte.
- `no_source` é distinto de erro técnico e nunca libera geração sem fundamentação.
- Placeholder como `[Lei nº, artigo]` ou fixture inventada não é fonte válida.
- Se `demo` for verdadeiro, a interface identifica o conteúdo como demonstração; ele não é apresentado como resposta validada do Aurora.

### 5.4 Decisão de guardrail

```ts
type GuardrailResult =
  | { decision: "allow" }
  | { decision: "out_of_scope"; category: "diagnosis" | "prescription" | "individual_legal_opinion" }
  | { decision: "block"; reason: "guardrail_unavailable" | "unsafe_output" };
```

- Perguntas gerais sobre direitos não são automaticamente classificadas como parecer individual.
- Falha/indisponibilidade do guardrail é `block`, não `allow`.
- O texto de resposta ao usuário vem do conteúdo aprovado, não de uma mensagem improvisada pelo adaptador.
- Categorias e gatilhos dependem de revisão jurídica/clínica antes de implementação.

### 5.5 Catálogo e encaminhamento

```ts
interface ServiceRecommendationRequest {
  city?: string;
  state?: string;
  need?: "emergency" | "legal" | "psychological_support" | "general";
  urgency?: "acute" | "ongoing" | "no_immediate_signal" | "indeterminate";
}

interface ServiceOption {
  id: string;
  name: string;
  category: string;
  description: string;
  contact?: string;
  hours?: string;
  cost?: string;
  lastVerifiedAt?: string;
  demo: boolean;
}

interface ServiceRecommendationResult {
  status: "found" | "no_verified_result";
  services: ServiceOption[];
}
```

- A entrada de localização continua manual e opcional, como definido nos requisitos. Geolocalização automática permanece bloqueada para revisão de produto.
- O retorno contém no máximo três opções; prioridade e hierarquia jurídica seguem os requisitos e a matriz aprovados.
- `no_verified_result`, cidade ambígua, falha técnica e resultado vazio não são intercambiáveis.
- Registro desatualizado não é promovido a recomendação prioritária. `demo: true` impede que fixture seja confundida com contato real.
- O serviço recomendado não recebe relato nem dados pessoais; o contato é ação da usuária.
- O fallback textual e as opções para entrada vazia/ambígua ainda dependem de decisão de produto.

## 6. Mapeamento de resposta da API conversacional (proposta)

O caso de uso conversacional deve retornar uma união discriminada para que o frontend não infira o estado pelo texto da resposta:

```ts
type ConversationOutcome =
  | { outcome: "acute_risk"; triage: TriageResult; channels: EmergencyChannel[] }
  | { outcome: "indeterminate"; triage: TriageResult; channels: EmergencyChannel[] }
  | { outcome: "informational"; answer: string; sources: SourceReference[]; demo: boolean }
  | { outcome: "no_source"; message: string; demo: boolean }
  | {
      outcome: "out_of_scope";
      category: "diagnosis" | "prescription" | "individual_legal_opinion";
      message: string;
      actions: Array<"general_rights" | "service_recommendation">;
    }
  | { outcome: "blocked"; reason: "guardrail_unavailable" | "unsafe_output" };
```

```ts
interface EmergencyChannel {
  number: "190" | "180" | "192" | "188";
  label: string;
  href: "tel:190" | "tel:180" | "tel:192" | "tel:188";
}
```

`EmergencyChannel` representa somente canais registrados no backlog. Os rótulos e a seleção contextual ainda precisam de revisão profissional; o destino `tel:` não inicia a ligação por si só.

**Ordem obrigatória no backend:** validar entrada → executar triagem → se risco agudo/indeterminado, retornar o resultado correspondente sem recuperação/geração informativa → recuperar fontes → aplicar guardrail ao pedido/saída → gerar/validar resposta ancorada → retornar conteúdo com fontes. Uma falha em qualquer dependência é um erro explícito ou resultado `blocked`; nunca uma resposta fictícia de sucesso.

**Atenção:** este contrato é uma proposta técnica para suportar decisões já registradas no J-00. A classificação de risco indeterminada, os textos de UI e os campos de ação ainda dependem de revisão humana e não devem ser implementados com conteúdo final antes dela.

## 7. Erros HTTP e comportamento do cliente

Decisão aprovada: manter respostas JSON e status HTTP explícitos no formato FastAPI `{"detail": ...}`; `detail` pode ser texto ou lista de erros de validação. Não criar um envelope proprietário comum nesta etapa.

| Situação | Status esperado | Tratamento no frontend |
|---|---:|---|
| JSON inválido, campo ausente, tipo incorreto ou texto vazio | 422 | Não acrescentar resposta de assistente; preservar rascunho e mensagens em memória; mostrar erro de entrada compreensível |
| Corpo acima do limite definido pelo endpoint | 413 | Mostrar erro de tamanho sem repetir o conteúdo enviado |
| Limite temporário de chamadas, se configurado | 429 | Informar indisponibilidade temporária e permitir tentar novamente |
| Adaptador mock/serviço indisponível ou timeout | 503 ou 504 | Apresentar erro técnico seguro; não converter em resposta, ausência de risco ou ausência de fonte |
| Erro interno inesperado | 500 | Mensagem genérica ao usuário; detalhe técnico somente em log sanitizado sem dados livres |
| HTTP sem sucesso, JSON ilegível ou resposta fora do schema | status recebido / erro de protocolo | Tratar como falha, sem sucesso-shaped fallback; preservar sessão para recuperação |

`413`, `429` e `504` são estados previstos para integração resiliente; não significam que rate limiting ou limites de corpo estejam implementados atualmente. Os valores de limite e textos visíveis devem ser definidos na tarefa que introduzir esses controles.

O frontend deve validar a estrutura da resposta em runtime. Não considerar `response.ok` suficiente. Para erros de rede, formato inesperado e indisponibilidade, exibir estado de erro distinto de resposta de conteúdo. O texto livre e o objeto completo de erro não devem ser interpolados em mensagens de erro, logs ou telemetria.

## 8. Estrutura sugerida para mocks e fixtures

```text
src/backend/src/aurora_backend/
├── contexts/
│   ├── conversation/features/<caso_de_uso>/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── handler.py
│   ├── safety/                     # triagem e guardrail, sem dependência de LLM
│   ├── knowledge/                  # porta de recuperação/fontes
│   └── services/                   # catálogo/encaminhamento
└── adapters/
    └── demo/                       # implementações mock injetáveis
        └── fixtures/               # conteúdo sintético/aprovado e marcado demo
```

A estrutura é ilustrativa, não uma exigência de criar todas as pastas de uma vez. Criar cada contexto/feature somente quando a tarefa correspondente começar; não criar diretórios vazios ou abstrações sem consumidor.

Regras para cada adaptador:

- implementar o mesmo protocolo/contrato que a futura integração real;
- ser selecionável por injeção de dependência/configuração explícita, não por inspeção do texto da usuária;
- ter fixtures pequenas, versionadas, sem PII e com fonte/rastreabilidade quando afirmarem fatos;
- não chamar rede, gerar tokens aleatórios que pareçam evidência ou armazenar estado;
- falhas controladas podem ser injetadas em testes, nunca ativadas por conteúdo especial na mensagem da usuária;
- identificar fixtures para a UI como demonstração, quando forem exibidas.

## 9. Matriz de cenários e limites dos testes

| Capacidade | Teste automatizado de contrato | O que o mock não comprova |
|---|---|---|
| Conversa | Entrada válida/vazia, histórico, sequência e schema da resposta | Qualidade de conversa ou compreensão real de linguagem |
| Triagem | Estados agudo/indeterminado/não sinalizado injetados; precedência antes de conteúdo | Recall de 100%, precisão, representatividade cultural ou segurança clínica |
| Fontes | Resultado com referências completas, sem fonte e fixture marcada `demo` | Qualidade de RAG, cobertura ou validade científica/jurídica da base real |
| Guardrail | Permitir/bloquear/fora de escopo, falha fechada | Zero violações em produção ou robustez real contra casos limítrofes |
| Catálogo | Até três opções, ordem, vazio, ambíguo, indisponível e data de verificação | Correção do contato, atendimento, frescor real ou alcance de CA-05 |
| Privacidade | Verificar ausência de persistência e de conteúdo em logs/test fixtures | Ausência de rastros no navegador, SO, rede, infraestrutura ou terceiros |
| Cliente HTTP | Status não-2xx, timeout, JSON inválido e schema inesperado | Disponibilidade AWS, TLS real, latência sob carga ou falha de provedor real |

Os testes devem usar dados sintéticos e inspecionar logs/capturas. Os casos-âncora e controles formais do CA-02 precisam de curadoria especializada e execução contra a aplicação real; não substituir por mocks. CA-01, CA-03, CA-04 e CA-05 também exigem verificações além de testes unitários de adaptador, conforme [arquitetura operacionalizada](../arquitetura_operacionalizada_aurora.md).

## 10. Aceite técnico e pendências de domínio

Em 31/10/2026, a usuária aprovou o padrão técnico e confirmou:

1. Evoluir `POST /api/chat/messages` de forma coordenada entre backend e frontend, sem compatibilidade externa nem rota legada paralela.
2. Não enviar histórico: manter a conversa somente no frontend em memória; o backend recebe apenas a mensagem atual.
3. Manter erros JSON no formato FastAPI `{"detail": string|lista}` com status HTTP explícitos, validação de resposta no frontend e sem fallback em formato de sucesso.
4. Aprovar os contratos tipados, os adaptadores substituíveis e os limites de evidência dos mocks descritos neste documento.

Pendências que permanecem para as tarefas de implementação:

- Limites de tamanho, rate limiting e mensagens finais de erro são definidos quando os controles correspondentes forem implementados.
- Resposta do backend não tem contexto de mensagens anteriores; integração que exija histórico requer revisão do contrato e privacidade.
- Os contratos técnicos não aprovam sinais/classificação clínica, cópia de incerteza, exemplos de guardrail, conteúdo de fontes nem contatos reais. Permanecem as validações profissionais e bloqueios indicados em J-00.
- Localização manual opcional segue vigente; geolocalização automática permanece bloqueada para revisão de produto.
- Contratos de autenticação e persistência continuam fora de escopo até L-01/L-02.

## 11. Skills consultadas

- [Arquitetura de software e integração ponta a ponta](../../skills/arquitetura-software-integracao.md)
- [Backend Python e APIs com FastAPI](../../skills/backend-python-fastapi.md)
- [Frontend React, TypeScript e experiência conversacional](../../skills/frontend-react-typescript-chat.md)
- [Engenharia de qualidade, testes e fitness functions](../../skills/engenharia-qualidade-testes-fitness-functions.md)
- [Privacidade, LGPD e governança de dados](../../skills/privacidade-lgpd-governanca-dados.md)
