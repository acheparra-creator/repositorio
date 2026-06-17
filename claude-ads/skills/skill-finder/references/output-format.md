# Output format — skill candidates report

The report is the user-facing artifact. It must be skimmable in 90 seconds by a busy executive. Stick to this format exactly.

## Required structure

```markdown
# Skill Candidates Report

**Generated**: [ISO date]
**Workspace scanned**: [folder paths + connector list]
**Time window**: [date range]
**Patterns analyzed**: [count from discovery]
**Recommended skills**: [count, max 7]

---

## How to use this report

Below are skill candidates ranked by impact. After reading the report, Claude will ask which ones you'd like built — you can reply with numbers ("1, 3, and 5"), names ("the investor update and the friday wrap"), "all", or "none".

---

## Recommended skills

### 1. [skill-name]

**What it does**: [one sentence]
**When it fires**: [trigger condition / user phrase]
**Inputs needed each run**: [list]
**Outputs**: [what gets produced]
**Time saved per use**: ~[N] minutes
**Frequency**: ~[N] times per [week/month/quarter]
**Confidence**: [high / medium / low]
**Underlying pattern**: [the discovery evidence — which files, calendar events, emails — that motivated this]

---

### 2. [skill-name]

[same structure]

---

[continue through max 7]

---

## Considered but not recommended

Patterns we noticed but cut from the recommendations list:

- **[pattern name]**: [one-line reason for cutting]
- **[pattern name]**: [one-line reason for cutting]

---

## Open questions

If any patterns were ambiguous or the user could clarify:

- [question 1]
- [question 2]

---

## Next step

After Claude presents the report, it will ask which candidates to build. Reply with numbers ("1, 3, 5"), names ("the investor update"), "all", or "none". Claude will echo back the selection for confirmation before scaffolding.
```

## Tone and language conventions

- **No fluff.** Every line has to earn its place. Cut all "I noticed that..." and "It seems like..." preambles.
- **Use the user's language.** If they call it a "weekly board update", call it that. If they call it a "shareholder note", call it that. Discovery output should give you their vocabulary.
- **Lead with impact.** First sentence of "What it does" should describe the *outcome*, not the mechanism. "Drafts your monthly investor update from this month's metrics and qualitative notes" not "Reads files in /investor-monthly and produces a markdown document."
- **Be honest about confidence.** A "medium confidence" candidate with strong impact is worth surfacing; mark it medium and let the user judge.
- **Show evidence.** The "Underlying pattern" line is non-negotiable. The user has to be able to verify why each candidate was promoted.

## What NOT to include

- Generic productivity tips
- Long explanations of what a skill is
- Caveats about limitations of LLMs
- Comparisons to other tools
- Anything that doesn't help the user decide which candidates to approve
