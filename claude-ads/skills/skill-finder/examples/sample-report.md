# Skill Candidates Report

> Example output — what skill-finder produces when run on a synthetic CEO workspace with seeded recurring patterns. Shows the full report structure, ranked candidates, cuts, and approval mechanics.

**Generated**: 2026-05-04
**Workspace scanned**: `~/Acme-CEO-Workspace/` (folders 01-07), Calendar snapshot, Sent email snapshot, Granola folder
**Time window**: 2026-01-01 to 2026-04-30 (90 days)
**Patterns analyzed**: 23 distinct clusters
**Recommended skills**: 5

---

## How to use this report

Below are skill candidates ranked by impact. After you've reviewed them, I'll ask which ones to build — you can reply with numbers ("1, 3, and 5"), names ("the investor update and the Friday wrap"), "all", or "none".

---

## Recommended skills

### 1. monthly-investor-update

**What it does**: Drafts your monthly investor update for any of your 5 lead investors using this month's metrics, shipped work, compliance state, hiring pipeline, and asks — preserving your voice and the recipient-specific framing you've used historically.
**When it fires**: First week of each month, when you say "draft the [investor] update" or open the investor folder.
**Inputs needed each run**: Current month's metrics (ARR, accounts, NRR, revenue), shipped product list, compliance updates, hiring deltas, recipient name.
**Outputs**: Markdown draft in `01-Board-and-Investors/[Investor]-Monthly-Update-[YYYY-MM].md`, formatted to match your existing template, with recipient-specific sections (e.g., growth questions for Investor-B, compliance framing for Investor-A).
**Time saved per use**: ~25 minutes
**Frequency**: 5 sends/month (one per investor) → 20/quarter
**Confidence**: HIGH
**Underlying pattern**: 18 historical investor updates across 5 recipients in the 90-day window. Strong template match across instances. Recipient-specific framing detected (e.g., Investor-B asks always include consumer growth questions; Investor-A asks always include compliance + enterprise expansion).

---

### 2. quarterly-board-update

**What it does**: Drafts the quarterly board update from monthly investor updates, weekly product reviews, friday wraps, and metrics — assembling the executive summary, financials, product, growth, compliance, team, risks, and next-quarter sections in the format you've used the last 4 quarters.
**When it fires**: Two weeks before quarter-end, when you say "start the board update" or open the board folder.
**Inputs needed each run**: Three months of investor updates, three months of weekly product reviews, friday wraps, current metrics, hiring deltas.
**Outputs**: Markdown draft in `01-Board-and-Investors/Q[N]-[YYYY]-Board-Update.md` matching your historical structure.
**Time saved per use**: ~3 hours
**Frequency**: Quarterly
**Confidence**: HIGH
**Underlying pattern**: 2 historical board updates (Q4 2025, Q1 2026) with identical 9-section structure. Clear synthesis pattern from monthly artifacts. Highest time-saved per use of any candidate.

---

### 3. compliance-status-monitor

**What it does**: Refreshes your monthly compliance status tracker by reviewing recent customer security inquiries, audit correspondence, and regulatory updates — flagging changes vs. last month, classifying account status (active / in review / inquiry pending / closed), and surfacing strategic risks for the SOC 2 Type II track.
**When it fires**: First week of each month, when you say "update the compliance tracker" or "run the compliance monitor".
**Inputs needed each run**: Last month's tracker, any new inquiry correspondence, audit/legal updates being watched.
**Outputs**: Markdown tracker in `02-Regulatory/State-Tracker-[YYYY-MM].md` with delta section showing changes vs. prior month.
**Time saved per use**: ~90 minutes
**Frequency**: Monthly
**Confidence**: HIGH
**Underlying pattern**: 3 monthly trackers in window with consistent structure (summary, table, closed list, delta section). The "changes vs. prior month" section is the high-value synthesis work that gets repeated.

---

### 4. interview-debrief-synthesizer

**What it does**: Generates your interview debrief from your raw notes, populates the debrief template (strengths/concerns/hire decision/next-round tests), and updates a candidate-pipeline summary so you can see all final-round candidates side-by-side before deciding.
**When it fires**: After any final-round CEO interview, when you say "debrief [name]" or "log the debrief for [name]".
**Inputs needed each run**: Candidate name, role, raw notes from the interview, interview round number. Optional: Granola transcript of the interview if available.
**Outputs**: Debrief file in `03-Hiring/Interview-debriefs/[YYYY-MM-DD]-[Name]-[Role]-R[N].md` plus an updated `03-Hiring/Pipeline-Summary.md` showing all open final-round candidates side-by-side.
**Time saved per use**: ~15 minutes
**Frequency**: ~6 final-round interviews/month based on hiring pace
**Confidence**: HIGH
**Underlying pattern**: 4 debrief files in window using consistent template, plus an explicit `_TEMPLATE.md` file. Pipeline-summary view doesn't currently exist — this skill creates it as a side effect. Granola folder contains transcripts of 3 of the 4 debriefed interviews — strong cross-surface alignment.

---

### 5. friday-wrap-generator

**What it does**: Drafts your weekly Friday Wrap from this week's product review, calendar (decisions/meetings), Granola transcripts of leadership syncs, and any new hires/losses — populating wins, losses, open items, and a next-week focus section.
**When it fires**: Friday at 3pm, when you say "draft the wrap" or open the exec-cadence folder.
**Inputs needed each run**: This week's product review notes, recent hiring updates, Granola transcripts of the leadership sync and 1:1s, your gut sense of the energy score (skill leaves this for you to fill).
**Outputs**: Markdown draft in `05-Exec-Cadence/Friday-Wrap-[YYYY-MM-DD].md`.
**Time saved per use**: ~12 minutes
**Frequency**: Weekly
**Confidence**: HIGH
**Underlying pattern**: 3 friday wraps in window with identical 5-section structure (wins/losses/open/energy/next week). High consistency, low complexity — quick win. Granola "Leadership Sync" folder contains 12 weekly transcripts that align perfectly with each wrap, providing strong source material.

---

## Considered but not recommended

Patterns we noticed but cut from the list, with one-line reasons:

- **Weekly product review compiler**: Strong recurring pattern but the meeting itself is where the synthesis happens. Skill would risk replacing the live discussion.
- **Press inquiry responder**: 7 instances detected but each response is too context-specific to template safely. Recommend a press-kit-link skill instead, but de-prioritized.
- **Candidate offer letter generator**: 11 instances but legal/comp/title sensitivity makes this high-stakes. Better handled by HR tooling.
- **Conference invite decliner**: 6 instances with simple template — too lightweight to need a skill. A saved canned response in Gmail does this.
- **Compliance application drafter**: Single high-value document, not recurring. Not a skill.
- **Q2 strategy refresh**: One-off strategic project, not a recurring workflow.
- **Weekly all-hands prep**: Pattern is real but the inputs (metrics + culture moments) are too varied to template safely.
- **Sprint summary generator**: Belongs to the eng/product team's tooling, not the CEO's.
- **1:1 follow-up emailer**: 24 Granola transcripts of weekly 1:1s in the window, but the post-1:1 follow-ups are too varied per direct-report to template — different DRs need different framings.

---

## Open questions

- For the `monthly-investor-update` skill: do you want one skill that takes a `--recipient` flag, or 5 separate skills (one per investor)? One skill is cleaner; 5 lets you tune voice per recipient. Recommend one with a recipient flag, but defer to you.
- For `compliance-status-monitor`: should this also generate a draft "update for [CLO]" email summarizing the changes? Detected pattern is you forward the tracker to them each month, but only 2 instances in window.
- For `friday-wrap-generator`: Granola transcripts cover the leadership sync but not all 1:1s. Want the skill to incorporate only the leadership sync, or attempt to weave 1:1 highlights too? Recommend leadership-sync only — 1:1 weave creates noise.

---

## Next step

Which would you like me to build?

- "all" to build everything
- specific numbers like "1, 3, and 5"
- specific names like "the investor update and the friday wrap"
- "none" or "let me think about it" to stop here

Once you pick, I'll echo back the selection for confirmation, then scaffold the SKILL.md files in `~/skill-finder-output/skills/`.
