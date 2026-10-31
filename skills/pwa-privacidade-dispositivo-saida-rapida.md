# Skill: PWA, privacidade de dispositivo e Saída Rápida

## Finalidade

Especificar e implementar o acesso móvel e os controles de saída considerando
que o dispositivo pode ser compartilhado ou monitorado.

## Conhecimentos necessários

- PWA, manifestos, service workers, cache, instalação e estratégias offline.
- Threat modeling para shoulder surfing, histórico, cache, notificações e
  estados em memória.
- Navegação para destino neutro e limpeza do estado controlado pela aplicação.
- Testes de usabilidade e desempenho em dispositivos móveis e conexão lenta.

## Contexto específico do Aurora

- A Saída Rápida deve ser independente de rede e inferência; metas
  documentadas: p95 ≤ 200 ms e p99 ≤ 300 ms.
- O wireframe indica destino neutro, encerramento da sessão e substituição
  da navegação; destino ainda precisa ser definido pelo produto.
- Não prometer apagar histórico do navegador, registros do sistema operacional,
  rede ou monitoramento externo.
- Camuflagem e PIN de fachada são recursos de alto risco e exigem revisão de
  segurança e validação especializada.

## Resultado esperado

Comportamento e limites de privacidade explícitos, requisitos offline
verificáveis e plano de teste; registrar os riscos que o navegador não permite
controlar.
