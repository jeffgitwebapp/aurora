# Skill: Gestão de conteúdo e painel administrativo

## Finalidade

Permitir manutenção segura e rastreável de catálogo, módulos educativos,
fontes RAG e diretrizes do sistema.

## Conhecimentos necessários

- CMS/painel editorial, papéis, autenticação administrativa, revisão,
  aprovação, versionamento, auditoria e rollback.
- Publicação sem downtime e gestão de índices/cache.
- Métricas agregadas com privacidade por padrão e limiares contra
  reidentificação.

## Contexto específico do Aurora

- Administradores devem manter serviços, materiais psicoeducativos e fontes
  sem intervenção de engenharia, conforme o backlog.
- Conteúdo deve passar por revisão especializada antes da publicação.
- Não expor conversas individuais nem permitir inferência de identidade pelas
  métricas administrativas.
- Mudanças de prompts/guardrails precisam de histórico e possibilidade de
  rollback.

## Resultado esperado

Fluxo editorial com estados e responsáveis, trilha de auditoria e publicação
verificável, sem métricas que revelem conteúdo individual.
