# Pattern detection heuristics

The job here: take the raw discovery inventory and cluster it into skill candidates. Not all clusters become skills.

## The three-property test

A cluster is a viable skill candidate only if it passes all three:

1. **Repeated**: 3+ instances in the discovery window
2. **Structured**: Has a recognizable shape (template, format, recurring inputs/outputs)
3. **Expertise-laden**: Requires judgment, voice, knowledge, or specialized context — i.e., a generic LLM call wouldn't do it well

A weekly metrics dump that's just "copy numbers from dashboard to email" passes 1 and 2 but fails 3 — it doesn't need a skill, it needs a Zapier zap or a Cowork automation. Note these in the "considered but not recommended" section of the report.

## Clustering signals (from strongest to weakest)

### Tier 1: Explicit recurrence

- Recurring calendar event with consistent title
- Sent email subject line repeating monthly/weekly with same recipient
- Folder of files with sequential dated names (`-2026-01`, `-2026-02`, `-2026-03`)
- Linear/Asana templates being instantiated repeatedly

These are nearly always skill candidates. High confidence.

### Tier 2: Structural twins

- Multiple files in different folders that share a structural template
- Slack messages with similar opening phrases ("here's the update on...")
- Notion pages with recurring section headers

Medium-high confidence. Validate by sampling 2–3 instances and confirming structure matches.

### Tier 3: Cross-surface alignment

When a Tier 1 or Tier 2 signal appears on multiple surfaces simultaneously (calendar event + email pattern + folder of artifacts), confidence escalates to highest. These are the skills the user is *already manually executing every week*.

### Tier 4: User-flagged

Things the user has explicitly mentioned wanting to automate, even if the discovery signal is weak. Always include if mentioned, but mark confidence based on actual signal strength.

## Anti-patterns — clusters that look like skills but aren't

- **One-off projects**: A folder full of files about "Q1 Strategy Refresh" looks structured but it happens once.
- **Volume without structure**: A Downloads folder with 200 PDFs has volume but no template.
- **Single-instance templates**: A `template.md` file with no instances of it being used. The template exists, the workflow doesn't.
- **Pure data movement**: "Copy numbers from A to B" is automation, not a skill. Note it but recommend a different tool (Zapier, Cowork direct automation, Make).

## Ranking the final list

After identifying all viable candidates, score each on:

- **Time saved per use** (minutes): rough estimate based on artifact length and complexity
- **Frequency** (uses per quarter): from the recurrence signal
- **Confidence** (0.3 / 0.6 / 1.0 for low/medium/high)

Score = `time_saved × frequency × confidence`

Take top 7. Cut the rest. The cut list goes in the "considered but not recommended" section with a one-line reason for each.

## The "would I actually use this?" gut check

Before finalizing each candidate, ask: would the user actually fire this skill, or would they just keep doing the work manually because their manual version is fast enough? If the manual version is fast and the skill barely improves it, cut.

A skill is worth building when it shifts a 30-minute task to a 5-minute review. Not when it shifts a 5-minute task to a 4-minute task.
