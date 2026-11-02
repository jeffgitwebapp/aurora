# Skill: DevOps, AWS, CI/CD e operação

## Finalidade

Empacotar, publicar, implantar e operar o Aurora com segurança, recuperação e
controle de custos.

## Conhecimentos necessários

- Docker/Compose, builds multi-stage, registry, GitHub Actions e deploy
  remoto seguro.
- AWS, redes, Security Groups, IAM, secrets, TLS, armazenamento e custos.
- Health checks, rollback, rolling/blue-green deployments, backup, recuperação
  e hardening de containers.
- Operação 24/7, SLI/SLO, alertas, incidentes e runbooks.

## Contexto específico do Aurora

- Alvo documentado: disponibilidade mensal de 99,5%, com orçamento limitado.
- SSH e credenciais não podem ser expostos; telemetria deve ser agregada e não
  identificável.
- A EC2/Docker atual é somente ponto de partida operacional; não demonstra
  que TLS, alta disponibilidade ou recuperação do alvo estejam atendidos.

## Resultado esperado

Pipeline reproduzível, implantação verificável, rollback e operação
documentados, sem segredos ou relatos em logs.
