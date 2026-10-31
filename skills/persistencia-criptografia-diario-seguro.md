# Skill: Persistência, criptografia e diário seguro

## Finalidade

Proteger dados persistentes da área logada e viabilizar diário e exportação
sem criar exposição adicional para a usuária.

## Conhecimentos necessários

- Modelagem, transações, retenção, criptografia em repouso, gestão/rotação de
  chaves, controle de acesso e exclusão verificável.
- Armazenamento seguro de anexos, validação, limites, varredura e minimização
  de metadados.
- Geração de PDF protegido e avaliação de riscos de exportar arquivos.

## Contexto específico do Aurora

- Histórico e diário contêm conteúdo de alto risco e pertencem ao modo logado.
- Backlog prevê data, hora, descrição, fotos/áudios e exportação de PDF
  criptografado.
- Não prometer valor ou efeito jurídico da exportação; avaliar risco de arquivo
  em dispositivo potencialmente monitorado.
- O modo anônimo permanece volátil.

## Resultado esperado

Políticas de armazenamento, acesso, exclusão e exportação documentadas e
testáveis, com análise de ameaça e revisão jurídica/de segurança.
