# Base de conhecimento do Aurora — Legislação (v0.2, validada em 04/11/2026)

Levantamento original: 01/11/2026 (v0.1). Validação de vigência e redação: **04/11/2026**. Status de todos os trechos: **pendente de aprovação jurídica** (a validação conferiu se a norma está em vigor e se o texto é o atual; a aprovação para entrar na base continua sendo da advogada parceira e, quando indicado, da psicóloga).

## O que mudou em relação à v0.1

- **Texto oficial preenchido.** Os campos `[colar]` foram substituídos pela redação vigente, extraída do texto compilado da Câmara dos Deputados (CEDI) e conferida com o compilado do Planalto em 04/11/2026. As anotações entre parênteses ("Redação dada pela Lei…") são do próprio compilado. A Lei 14.188/2021 (arts. 2º e 3º) veio da publicação do Planalto.
- **Correções:** art. 12-D da Lei Maria da Penha ("será imediatamente submetido", não "pode"); art. 12-C com as integridades da Lei 15.411/2026; art. 11 com o parágrafo único da Lei 15.455/2026; links do Planalto que faltavam (Lei 14.541/2023, Decreto 1.973/1996, CF/1988).
- **Trecho novo na Lei Maria da Penha:** art. 2º (direito de viver sem violência e preservar a saúde física e mental).
- **6 fontes novas** (tabela abaixo, marcadas com ★).

## Arquivos

| Prioridade | Arquivo | Norma | Por que entra no Aurora |
|---|---|---|---|
| 1 | `lei-11340-2006-maria-da-penha.md` | Lei 11.340/2006 | Formas de violência (inclusive a psicológica), medidas protetivas, direitos e rede |
| 1 | `cp-art147b-violencia-psicologica.md` | CP, art. 147-B (Leis 14.188/2021 e 15.123/2025) | A violência psicológica contra a mulher é crime |
| 1 ★ | `decreto-12976-2026-violencia-digital.md` | Decreto 12.976/2026 | Violência psicológica por meios digitais; retirada de conteúdo íntimo em até 2 h |
| 1 ★ | `lei-15410-2026-tortura-sofrimento-mental.md` | Lei 15.410/2026 (Barbara Penna) | Sofrimento mental reiterado no contexto doméstico passou a ser tortura |
| 2 | `cp-art147a-perseguicao.md` | CP, art. 147-A (Lei 14.132/2021) | Perseguição/stalking, frequente junto da violência psicológica |
| 2 ★ | `cp-art216b-218c-intimidade-exposicao.md` | CP, arts. 216-B e 218-C | Registro e divulgação de cenas íntimas sem consentimento (chantagem) |
| 2 ★ | `jurisprudencia-stj-tema-1249-medidas-protetivas.md` | STJ, Tema 1249 | Medida protetiva sem prazo fixo, enquanto houver risco |
| 2 ★ | `lei-14713-2023-guarda-e-risco-de-violencia.md` | Lei 14.713/2023 (CC art. 1.584 §2º; CPC art. 699-A) | Medo de "perder os filhos": risco de violência afasta a guarda compartilhada |
| 2 | `lei-10778-2003-notificacao-compulsoria.md` | Lei 10.778/2003 | O que acontece quando ela conta a violência num serviço de saúde |
| 2 | `lei-14541-2023-deam-24h.md` | Lei 14.541/2023 | Como deve ser o atendimento na delegacia da mulher |
| 2 | `lei-14188-2021-sinal-vermelho.md` | Lei 14.188/2021 | Forma discreta de pedir ajuda |
| 3 | `lei-15384-2026-violencia-vicaria.md` | Lei 15.384/2026 | Violência por meio dos filhos e de pessoas próximas |
| 3 ★ | `lei-13431-2017-violencia-psicologica-criancas.md` | Lei 13.431/2017, art. 4º, II | Criança que presencia a violência também é vítima |
| 3 | `lei-14149-2021-formulario-avaliacao-risco.md` | Lei 14.149/2021 | Explica o questionário de risco aplicado na delegacia |
| 3 | `lei-14994-2024-pacote-antifeminicidio.md` | Lei 14.994/2024 | Feminicídio e penas; contexto, usar com cuidado |
| 3 | `decreto-1973-1996-convencao-belem-do-para.md` | Decreto 1.973/1996 | Direito a uma vida livre de violência (tratado internacional) |
| 3 | `cf-1988-art226-par8.md` | CF/1988, art. 226, §8º | Fundamento constitucional |

## Formato de cada arquivo

Igual ao da v0.1: cabeçalho YAML (`id`, `titulo`, `orgao`, `numero`, `data`, `publicacao_dou`, `versao`, `url_oficial`, `url_consulta`, `temas`, `status`, `revisado_por`, `data_revisao`, `proxima_revisao`) mais `verificado_em`; um trecho por seção `##`, marcado com `<!-- chunk: id#localizador -->`, com Localizador, Redação, Temas, Texto oficial, Resumo em linguagem simples (rascunho), Perguntas de teste e Atenção (escopo).

## Regras para entrar na base (mantidas)

- Só entra trecho com `status: aprovado`, depois da revisão da advogada parceira (e da psicóloga, quando indicado).
- O texto que o RAG cita é o **texto oficial**. O resumo serve de apoio para escrever respostas em linguagem simples, nunca como citação da lei.
- Telefones de emergência e o catálogo de serviços **não** entram aqui (CA-05).
- Terminologia: o Aurora **indica**, não "encaminha" nem "aciona".

## Pontos para a revisão jurídica (atualizados)

1. **Lei Maria da Penha:** 14 leis alteraram o texto entre 2023 e 2026 (lista no cabeçalho do arquivo). Última alteração: Lei 15.455/2026. Conferidos os arts. 12-C, 12-D, 16, 16-A e 22. O § 5º do art. 22 (Lei 15.125/2025) foi revogado pela Lei 15.383/2026.
2. **Art. 147-A, § 1º, II:** confirmado que remete ao § 2º-A do art. 121, revogado pelo art. 9º da Lei 14.994/2024. Leitura sugerida: remissão ao art. 121-A, § 1º. Decidir como explicar.
3. **Lei 10.778/2003:** continua aberto como conciliar o sigilo (art. 3º) com a comunicação à polícia em 24 h (art. 1º, § 4º). A Nota Técnica CFP nº 25/2025 trata exatamente desse ponto para psicólogas (ver `guias-oficiais/`).
4. **Links do Planalto:** confirmados e preenchidos.
5. **Novos:** prazo de 12 meses (Lei 15.438/2026) para fatos anteriores a 19/06/2026; alcance do art. 121-B (vicaricídio) menor que o do art. 7º, VI; Lei 15.410/2026 (tortura) ainda sem jurisprudência; Decreto 12.976/2026 é alvo do PDL 466/2026.

## Candidatas para a próxima rodada

- Lei 15.409/2026 (Cadastro Nacional de Pessoas Condenadas por Violência contra a Mulher — inclui o art. 147-B).
- Lei 15.438/2026 como arquivo próprio (hoje está no art. 16-A da LMP e nos arquivos do CP).
- Decreto 4.377/2002 (CEDAW) e Resolução Conjunta CNJ/CNMP nº 5/2020 (modelo do Formulário de Avaliação de Risco — conferir se houve atualização).
- Lei 13.104/2015, só como histórico (substituída pelo art. 121-A).
