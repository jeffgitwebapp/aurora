# Skill: Autenticação, autorização e área logada pseudonimizada

## Finalidade

Implementar contas opcionais e seguras, mantendo o acesso anônimo disponível
sem exigir identificação real.

## Conhecimentos necessários

- Autenticação por apelido/senha, armazenamento seguro de credenciais,
  sessões, autorização e mitigação de abuso.
- Identidade pseudonimizada e separação de dados por conta.
- Migração voluntária de sessão anônima e exclusão definitiva de conta/dados.
- Fluxos de recuperação e tratamento de falha de autenticação.

## Contexto específico do Aurora

- O backlog requer apelido e senha, sem exigir e-mail ou telefone real.
- Cadastro e persistência são opt-in; não degradar o caminho anônimo.
- A migração do relato precisa ser voluntária e transparente.
- Exclusão deve remover dados associados de forma verificável.

## Resultado esperado

Fluxos documentados para cadastro, login, erro, recuperação, migração e
exclusão, com análise de privacidade e segurança.
