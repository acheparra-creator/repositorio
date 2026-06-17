# skill-finder

A Claude meta-skill that audits a working environment — folders, recurring calendar events, sent email patterns, Slack/Notion/Linear activity — and surfaces the 5–7 highest-leverage skills worth building, ranked by impact × frequency × confidence. Once approved, it scaffolds the `SKILL.md` files automatically.

It exists because most automation audits produce a 30-item list that nobody acts on. This one is constrained to surface the few candidates that actually compound, show the work behind the cuts, and close the loop with installable output.

## How it works

The skill runs a 6-phase workflow:

1. **Scope** — confirm which folders and connectors are in-scope, time window, confidentiality boundaries
2. **Discovery** — inventory artifacts across each surface (no analysis yet)
3. **Pattern detection** — cluster the inventory by structural repetition signals
4. **Synthesis** — convert clusters into ranked skill candidates with trigger, time-saved estimate, and confidence
5. **Reporting** — generate a markdown report with checkbox approval
6. **Scaffolding** — once approved, generate the `SKILL.md` files, voice extracts, and reference templates

A skill is only promoted as a candidate if it's **repeated** (3+ instances), **structured** (has a recognizable shape), and **expertise-laden** (judgment, voice, or specialized context). Anything that fails the third test gets cut and noted in a "considered but not recommended" section so the user sees the reasoning, not just the conclusion.

## Install

```bash
git clone https://github.com/ahuntcuse19/skill-finder.git
cp -r skill-finder/skill-finder/ ~/.claude/skills/
```

Then, in Claude (Cowork, Claude Code, or any Claude environment with skill support), invoke it with:

> Run skill-finder on `~/path/to/working-folder`

## Output

See [`skill-finder/examples/sample-report.md`](skill-finder/examples/sample-report.md) for what the report looks like — run on a synthetic CEO workspace with seeded recurring patterns (monthly investor updates, quarterly board updates, monthly regulatory trackers, weekly product reviews, interview debriefs, friday wraps).

The report is structured for a 90-second skim:

- 5–7 ranked candidates, each with: trigger condition, inputs, outputs, time-saved estimate, frequency, confidence, and the underlying pattern evidence
- "Considered but not recommended" section with one-line reasons
- "Open questions" for anything ambiguous
- Approval checkboxes — toggle `[x]` and re-run with "scaffold approved skills"

## Repo structure

```
skill-finder/
├── SKILL.md                          # the skill definition
├── references/
│   ├── surfaces.md                   # per-surface scanning guidance
│   ├── pattern-detection.md          # heuristics for clustering
│   ├── output-format.md              # required report format
│   └── skill-template.md             # template for scaffolded skills
└── examples/
    └── sample-report.md              # example output
```

## License

MIT
