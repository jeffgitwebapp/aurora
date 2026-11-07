// PreToolUse (Edit/Write/MultiEdit/NotebookEdit): pede confirmação antes de editar
// caminhos protegidos pelo plano docs/plano-implementacao-adicionando-agente-aurora.md (R-01..R-03).
let raw = "";
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  let input;
  try {
    input = JSON.parse(raw);
  } catch {
    process.exit(0);
  }
  const toolInput = input.tool_input || {};
  const target = toolInput.file_path || toolInput.notebook_path || "";
  if (!target) process.exit(0);

  const path = target.replace(/\\/g, "/").toLowerCase();
  const rules = [
    {
      pattern: /\/src\/frontend\//,
      reason:
        "Frontend: só é permitida a exibição das fontes por trecho (U-06: lista Fontes numerada e [n] clicável em features/chat).",
    },
    {
      pattern: /\/contexts\/conversation\/services\/(triage|guardrail|knowledge|content_offer)\//,
      reason:
        "Serviços que a v1.2 não altera (triagem, escopo, conhecimento por fixtures, oferta) — R-02/U-01.",
    },
    {
      pattern: /\/docs\/jornada-usuario\//,
      reason: "Plano da jornada e contratos do protótipo não são alterados (R-03).",
    },
  ];
  const hit = rules.find((rule) => rule.pattern.test(path));
  if (!hit) process.exit(0);

  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: `Caminho protegido pelo plano v1.2: ${hit.reason}`,
      },
    }),
  );
});
