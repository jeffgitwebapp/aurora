# Skill: Arquitetura de software e integração ponta a ponta

## Finalidade

Definir fronteiras modulares e contratos que permitam evoluir o Aurora com
segurança, substituição de provedores e integração consistente entre
interfaces e serviços.

## Conhecimentos necessários

- Monólito modular, bounded contexts, arquitetura hexagonal, portas,
  adaptadores e separação de domínio/aplicação/infraestrutura.
- APIs HTTP, contratos, versionamento, validação, erros e compatibilidade.
- Integração entre frontend, backend, LLM/RAG, triagem e catálogo.
- Documentação com C4 e visões arquiteturais 4+1.

## Contexto específico do Aurora

- Manter fronteiras claras entre conversa/RAG, risco, encaminhamento,
  catálogo, contas, diário e administração.
- Isolar o provedor de LLM por adaptador; regras do domínio não dependem de
  fornecedor específico.
- Fluxos críticos determinísticos não podem aguardar inferência probabilística.
- Distinguir desenho alvo dos limites do scaffold inicial descrito em
  `docs/aurora-criacao-projeto.md`.

## Resultado esperado

Decisões arquiteturais justificadas, diagramas atualizados, contratos
coerentes e dependências explícitas; registrar riscos, trade-offs e impacto
nos requisitos.
