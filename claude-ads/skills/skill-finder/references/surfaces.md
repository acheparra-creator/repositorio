# Surfaces — what to look for on each

## File system

**What to scan**: Folders explicitly granted by the user. Do not traverse outside-scoped paths.

**Strong signals**:
- Files with similar naming patterns (`Investor-Update-Mar`, `Investor-Update-Apr`, `Investor-Update-May`)
- Folders containing >3 files of the same structural type
- Subfolders that look like template-driven outputs (e.g., `/debriefs/` with 8 similarly-structured files)
- Files with `-template`, `-draft`, `-final` suffixes (suggests a workflow)

**Weak signals**:
- High raw file count
- Many file types
- Recent modification dates alone

**What to capture**: filename, full path, last modified, file size, file type. For text files, also capture the first 5–10 lines to detect template structure.

---

## Calendar (via Google Calendar connector)

**What to scan**: Events from the last 90 days plus the next 30 days.

**Strong signals**:
- Recurring events with consistent titles (every Mon 9am "1:1 w/ [Name]") → strong skill candidate for meeting prep + follow-up
- Events with consistent attendee patterns (always same investor group)
- Calendar holds named like "Prep — X" before bigger meetings (suggests meeting prep is done manually)

**What to capture**: event title, frequency, recurrence pattern, attendee list, duration, description (if any).

**Skill candidates these surface**: meeting-prep skills, post-meeting follow-up skills, recurring agenda generators, weekly board prep skills.

---

## Email (via Gmail connector)

**What to scan**: Sent items only by default. The inbox is mostly inbound noise; sent items reveal what the user creates.

**Strong signals**:
- Sent emails with recurring subject patterns to the same recipient(s) — e.g., monthly "Pantera Update — [Month]"
- Long emails (>500 words) sent to a single recipient with a similar structure each time → likely a recurring report
- Email threads where the user is repeatedly asked the same question

**What to capture**: subject, recipient(s), date, length, first paragraph (for structural detection).

**Skill candidates these surface**: investor update generators, recurring report drafters, FAQ-style auto-responders.

---

## Slack (via Slack connector)

**What to scan**: User's DMs, mentions, and high-activity channels (especially exec/leadership channels). Last 30 days.

**Strong signals**:
- Recurring questions asked OF the user ("can you send the latest metrics?")
- Recurring questions asked BY the user ("what's the status of X?")
- Messages with link/file shares to the same destinations repeatedly
- Long-form Slack messages (>200 words) — these are often work the user is doing inline that should be a doc

**What to capture**: channel, sender, timestamp, first 50 words.

**Skill candidates these surface**: status-fetcher skills, FAQ-responders, internal communication generators.

---

## Linear / Asana (via connectors)

**What to scan**: User's recently created or assigned tickets. Project structures.

**Strong signals**:
- Tickets with template-like titles repeating across projects ("Sprint Planning — [Date]")
- Recurring project structures (same column/section setup repeatedly)
- Tickets with very similar descriptions across projects

**Skill candidates these surface**: ticket generators, sprint planning skills, project scaffolders.

---

## Notion (via connector)

**What to scan**: Recently edited pages. Database structures.

**Strong signals**:
- Database entries with recurring structure (board updates, weekly notes, debrief logs)
- Pages where the user repeatedly applies the same structure manually
- Templates that exist but are inconsistently applied

**Skill candidates these surface**: structured-doc generators, database entry skills.

---

## Cross-surface signals

The strongest signals are cross-surface. If a recurring calendar event ("Monthly Pantera Sync") matches a sent email pattern ("Pantera Update — March") matches files in a folder (`/board-and-investors/pantera-monthly/`), that's a near-certain skill candidate. Always check for cross-surface alignment before finalizing the report.
