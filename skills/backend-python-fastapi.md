# Skill: Backend Python e APIs com FastAPI

## Finalidade

Implementar serviços e APIs do Aurora com contratos claros, módulos testáveis e
tratamento explícito de falhas sem expor conteúdo sensível.

## Conhecimentos necessários

- Python moderno e typing; FastAPI, Pydantic, ASGI e concorrência assíncrona.
- OpenAPI, validação de entrada/saída, códigos de erro e compatibilidade.
- Organização por contexto/feature e regras de domínio independentes do
  framework e de provedores externos.
- Timeouts, cancelamento, limites de payload e falhas de dependências.
- Testes pytest unitários/integração, lint e formatação existentes no projeto.

## Contexto específico do Aurora

- Nunca registrar o relato em logs, traces ou mensagens de erro.
- Caminho de emergência não pode depender de chamada ao LLM.
- Contratos da API devem suportar citações, estado de triagem, encaminhamento
  e erros sem retornar conteúdo fictício como sucesso.
- Respeitar retenção volátil no modo anônimo e persistência apenas nos fluxos
  explicitamente logados.

## Resultado esperado

Endpoints tipados, comportamento verificável com testes, erros explícitos e
observabilidade sem conteúdo livre de usuárias.
