# Skill: Triagem determinística de risco agudo e avaliação de segurança

## Finalidade

Projetar e validar a classificação de risco agudo com comportamento
determinístico, explícito e independente da geração por LLM.

## Conhecimentos necessários

- Regras classificatórias, precedência, explicabilidade, falsos
  positivos/negativos e fallbacks seguros.
- Construção e versionamento de casos-âncora e controles sintéticos.
- Recall, precisão, cobertura, regressão e mutation testing.
- Integração com classificador semântico sem retirar autoridade das regras
  determinísticas em emergências.

## Contexto específico do Aurora

- Sinais incluem ideação suicida, agressão em curso, ameaça de morte e
  presença de arma, inclusive formulações implícitas, coloquiais e regionais.
- RNF03/CA-02 exigem 100% de recall nos casos-âncora; falso negativo agudo é
  bloqueante.
- A tela de emergência deve ser exibida antes de conteúdo psicoeducativo e
  sem depender de inferência LLM.

## Limites e validação

Regras, perguntas e casos de teste precisam de curadoria por profissionais da
rede de proteção. Testes automatizados não demonstram segurança clínica e não
substituem validação humana.
