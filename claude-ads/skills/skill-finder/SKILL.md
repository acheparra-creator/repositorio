---
name: skill-finder
description: Audit a user's working environment (folders, recurring calendar events, sent email patterns, Granola meeting transcripts, Slack/Notion/Linear activity) to surface high-leverage skill and automation candidates, present them as a ranked report for human approval, and scaffold approved candidates into ready-to-use SKILL.md files. Use this skill any time the user asks to "find automation opportunities", "audit my workflow for skills", "what should I automate", "review my workspace and suggest skills", or "scan my work and tell me what to automate" — even if they don't use the word "skill" explicitly. Also use when a user says they're new to skills and wants to know where to start. Bias toward triggering this skill whenever the user mentions wanting to find, identify, or discover automation opportunities in their existing workflow.
---

# skill-finder

A meta-skill that finds skills. Given access to a user's working environment, it identifies repetitive, structured work that compounds in value when automated, surfaces it as ranked candidates, and — once approved — scaffolds the SKILL.md files automatically.

## When to use

Trigger this skill when the user wants to:
- Audit their workflow for automation opportunities
- Find candidate skills hidden in their existing work patterns
- Get started with skills, but doesn't know where to begin
- Generate a portfolio of skills tailored to their actual work, not generic templates

Do NOT use this skill for:
- Building a single, specific skill the user already knows they want (use `skill-creator` instead)
- General productivity advice
- Workflow consulting that doesn't end in shipped skills

## Core principle

A skill is worth building when a workflow is **repeated**, **structured**, and **expertise-laden**. The job of this skill is to find those three properties hiding in the user's actual work — not to invent generic skills they don't need.

The default failure mode is producing a 30-item list of vaguely-automatable tasks. That output is useless. Aim for **5–7 candidates, ranked by impact**, each with a concrete trigger, a time-saved estimate, and a one-line description of what gets automated.

## Workflow

Run these phases in order. Do not skip phases. Do not collapse them into a single pass — pattern detection requires the discovery output as input.

### Phase 1: Scope

Before scanning anything, confirm with the user:

1. **Which surfaces are in scope?** Read `references/surfaces.md` for the full list. At minimum, ask which folders to scan and which connectors are authorized (Gmail, Calendar, Granola, Slack, Linear, Notion, Asana).
2. **What's the time window?** Default to the last 90 days. Older signal is weaker.
3. **Are there confidentiality boundaries?** Some folders may need to be excluded (legal, M&A, personnel files).

If the user hasn't set up connectors but has them available, suggest enabling them rather than scanning a partial picture. Document scanning alone is the weakest version of this skill.

### Phase 2: Discovery

Capture artifacts across each in-scope surface. Read `references/surfaces.md` for what to look for on each surface. The output of this phase is a structured inventory file at `~/skill-finder-output/01-discovery.md` containing:

- File inventory: filename, path, size, last-modified, file type — grouped by directory
- Recurring calendar events: title, frequency, attendees pattern, duration
- Sent email patterns: recurring subjects/templates, recipient clusters, frequency
- Granola meeting patterns: recurring meeting titles, folder/tag groupings, structured note patterns (decisions, action items), repeated post-meeting deliverable types
- Slack/messaging patterns: channels with high activity, recurring questions the user is asked, recurring questions the user asks
- Tool-specific artifacts: Linear ticket templates, Notion page patterns, Asana project structures

Do not analyze yet. Just inventory.

### Phase 3: Pattern detection

Read `references/pattern-detection.md` for the full heuristics. The high-level move: cluster the discovery output by **structural repetition signals**, not file types.

Strong signals:
- Multiple files with similar naming patterns (`Investor-Update-Mar.md`, `Investor-Update-Apr.md`)
- Recurring calendar events with the same title (almost always a skill candidate — meeting prep, follow-ups, agenda generation)
- Sent emails with recurring subject patterns to the same recipient set
- Folders that contain >3 files of the same structural type (debrief notes, status reports, briefs)
- Repeated Slack questions asked of the user (e.g., "what's the latest on X")

Weak signals (note but don't lead with):
- High raw file counts in one folder
- Many file types in one folder
- Unread emails (volume signal, not pattern signal)

Output of this phase is a clusters file at `~/skill-finder-output/02-clusters.md`. Do not write the report yet.

### Phase 4: Synthesis

Convert each cluster into a skill candidate. For each candidate, fill in:

- **Name**: kebab-case, descriptive (e.g., `investor-monthly-update`, `state-regulatory-monitor`)
- **Trigger**: the user phrase or context that should fire this skill
- **What it does**: one sentence
- **Time saved per use**: realistic estimate in minutes/hours
- **Frequency**: how often this fires (weekly, monthly, ad-hoc)
- **Confidence**: high / medium / low — based on how strong the underlying pattern signal was
- **Inputs needed**: what files, data, or context the skill would need each time
- **Outputs**: what the skill produces

Drop candidates with low confidence AND low frequency. They're not worth building.

### Phase 5: Reporting and conversational approval

Generate the report at `~/skill-finder-output/03-skill-candidates-report.md`. Use the exact format in `references/output-format.md`. Critical conventions:

- Maximum 7 candidates. Rank by `time_saved_per_use × frequency × confidence`. Cut everything else.
- Each candidate is presented as a numbered entry (1, 2, 3…). The numbering is the approval handle.
- Include a "Considered but not recommended" section briefly explaining what was cut and why. This is a trust-building move — shows the user the work, not just the conclusion.
- Include an "Open questions" section if any patterns were ambiguous.

After writing the report, present a short summary in chat (numbered list of candidates with one-line descriptions) and **ask the user directly which they'd like built**. Use this exact prompt structure:

> Report saved to `~/skill-finder-output/03-skill-candidates-report.md`. Here's the shortlist:
>
> 1. [skill-name] — [one-line description]
> 2. [skill-name] — [one-line description]
> 3. [skill-name] — [one-line description]
> ...
>
> Which would you like me to build? You can say:
> - "all" to build everything
> - specific numbers like "1, 3, and 5"
> - specific names like "the investor update and the friday wrap"
> - "none" or "let me think about it" to stop here

Then stop and wait for the user's response.

When the user replies, parse their answer:
- "all" → all candidates approved
- "none" / "stop" / "let me think" → exit without scaffolding
- Numbers (e.g., "1, 3, 5") → match to candidate index
- Names (e.g., "the investor update") → match to candidate name (be tolerant of partial matches)
- Mixed (e.g., "1 and the friday wrap") → resolve both

Before proceeding to scaffolding, **echo back the selection for confirmation**:

> Got it — I'll build:
> - [skill-name-1]
> - [skill-name-2]
> - [skill-name-3]
>
> Confirm and I'll start scaffolding. (Say "go" or "yes" to proceed, or "wait" to revise.)

Wait for confirmation before moving to Phase 6. If the user revises ("actually drop #2"), update the selection and confirm again. Do not scaffold without explicit go-ahead.

### Phase 6: Scaffolding

Trigger condition: the user has explicitly confirmed the selection from Phase 5 (said "go", "yes", "build them", or equivalent affirmative response).

For each approved candidate:
1. Read `references/skill-template.md` for the SKILL.md template
2. Generate `~/skill-finder-output/skills/<skill-name>/SKILL.md` with the template populated from the candidate's synthesis fields
3. If the candidate needs reference files (e.g., a board update template), generate those too based on the discovery artifacts
4. Add a one-line note to each scaffolded skill: `<!-- Generated by skill-finder on YYYY-MM-DD. Review before installing. -->`

After scaffolding, present the user with:
- Count of skills generated
- Path to the skills folder
- Installation guidance: "Move to `~/.claude/skills/` to install, or test individually with `claude --skill <path>`"

## Failure modes to avoid

1. **Generic skills**: "email-summarizer" or "meeting-notes-skill" are not useful outputs. They have to be tailored to the user's actual recurring artifacts.
2. **Hallucinated patterns**: If a pattern only appears once or twice in the discovery output, do not promote it to a skill candidate. The threshold is 3+ instances unless the user explicitly flagged something as recurring.
3. **Bypassing approval**: Never auto-scaffold without an explicit affirmative response from the user (e.g., "go", "yes", "build them"). The conversational confirmation step is the trust mechanism — do not skip it, even if the user sounds enthusiastic earlier in the conversation.
4. **Burying the cuts**: Always show what was considered and rejected. The user needs to know the thinking, not just the recommendation.
5. **Skipping discovery**: Do not generate clusters or candidates from memory or assumption. Only from the actual discovery output file.

## Reference files

- `references/surfaces.md` — Per-surface scanning guidance (file system, calendar, email, Slack, etc.)
- `references/pattern-detection.md` — Heuristics for clustering discovery output into candidates
- `references/skill-template.md` — Template used in Phase 6 scaffolding
- `references/output-format.md` — Required format for the candidates report
- `examples/sample-report.md` — Example output for reference
