# Skill: Catálogo de serviços e motor de encaminhamento

## Finalidade

Apresentar serviços adequados, priorizados e atualizados conforme necessidade,
urgência e município/UF informados pela usuária.

## Conhecimentos necessários

- Modelagem de natureza jurídica, escopo, abrangência, localização, canal,
  horário, cenário, proveniência e data de verificação.
- Busca por município/UF e necessidade; ordenação, hierarquia, validade,
  cache e expiração.
- Validação de formato de telefone/URL, sondagem de sites e revisão humana de
  contatos.
- Testes de completude, ordenação, cenários e frescor.

## Contexto específico do Aurora

- Exibir até três opções e preservar a escolha da usuária.
- Em necessidade jurídica, priorizar órgãos públicos formais antes de
  organizações voluntárias, conforme Matriz de Encaminhamento.
- Localização é fornecida pela usuária, sem geolocalização precisa.
- CA-05 define 95% dos registros verificados nos últimos 90 dias, 100% dos
  serviços de emergência nos últimos 30 dias e limite máximo de 180 dias para
  serviço prioritário.
- Não enviar relato ou dados pessoais ao serviço indicado.

## Resultado esperado

Opções com informação verificável, data de revisão, prioridade explicável e
tratamento seguro para dados ausentes ou vencidos.
