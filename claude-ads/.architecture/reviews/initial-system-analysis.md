# Initial System Analysis

**Project**: Claude Ads  
**Date**: 2026-05-20  
**Analysis Type**: Initial Setup Assessment  
**Analysts**: Systems Architect, Domain Expert, Security Specialist, Maintainability Expert, Performance Specialist, Implementation Strategist, AI Engineer, Pragmatic Enforcer, Python Expert (Dr. Sarah Chen), Claude Skills Architect (Marco Delgado)

---

## Executive Summary

Claude Ads is a Tier 4 Claude Code skill that turns Claude into an in-house ad-strategy team, covering the three dominant ad platforms (Meta, Google, TikTok) that account for roughly 95% of global ad spend. The system is structured as a classic orchestrator → specialist skill pattern: a top-level `/ads` router dispatches to 19 sub-skills and 7 long-running agents (3 platform auditors + 4 creative agents). Each audit agent applies ~158 weighted checks and emits both a human-readable Markdown report and a machine-parseable JSON file validated against a shared schema, which the orchestrator aggregates into a cross-platform health score.

The architecture is well-suited to its constraints: it must run entirely inside Claude Code with no infrastructure footprint, reach $0 cost for the primary use case, and integrate with three different ad-platform MCPs that have uneven coverage. The three-tier data access pattern (MCP → Direct API → Manual export) is a strong design choice that makes the tool broadly accessible. Version 2.4.0 added guided onboarding (`/ads start`) and a continuous coach (`/ads next`) backed by persistent user state in `~/.claude-ads/`, which signals product maturity.

The codebase is young (active development, recently at v2.4.0) and in good health: CI enforces JSON schema validity, reference-file token budgets, shell script syntax, and CVE-free dependencies on every PR. The main risks are skill file size creep, the inherent fragility of scraping-based MCP wrappers for ad platforms, and the absence of integration-level test coverage against live sandbox APIs.

**Overall Assessment**: Good

**Key Findings**:
- Free-first three-tier data access is architecturally sound and well-enforced in documentation, but the direct-API adapters have no automated functional tests against real sandbox responses.
- JSON output contracts are enforced by CI schema validation but the orchestrator's aggregation logic is not independently tested from the agent outputs — a schema-valid but semantically wrong JSON (e.g., wrong field units) would pass CI silently.
- Skill file size discipline is enforced for reference files (200-line cap, CI-checked) but not for SKILL.md files (500-line cap is documented but not automated in CI).

**Critical Recommendations**:
- Add a CI step that counts lines in all `SKILL.md` files and fails if any exceeds 500 lines.
- Add a smoke-test fixture with canned JSON audit output that exercises the orchestrator's score aggregation path end-to-end.

---

## System Overview

### Project Information

**Primary Language(s)**: Python 3.10+ (logic), Markdown (skill definitions), Bash/PowerShell (installers)

**Frameworks**: Claude Code Agent Skills (Tier 4), pytest (testing), GitHub Actions (CI)

**Architecture Style**: Orchestrator → Specialist skill graph; three-tier data access per platform (MCP → Direct API → Manual)

**Deployment**: Runs locally inside Claude Code; no server or container required. Cross-platform installers copy skills into `~/.claude/skills/`.

**Team Size**: Solo / small team (open-source plugin)

**Project Age**: Active development; v2.4.0 is the current release

### Technology Stack

**Skill Layer**:
- Claude Code SKILL.md / agent orchestration
- Task tool with `context: fork` for agent delegation
- MCP server integration (Meta, Google Ads, TikTok MCPs)

**Python Scripts** (`scripts/`):
- Python 3.10+ stdlib-only API adapters (`scripts/api/`)
- ReportLab + Matplotlib for PDF report generation
- Playwright for landing-page screenshot and brand analysis
- Pillow for ad-image dimension validation
- `profile.py` CLI for persistent user state

**Infrastructure**:
- GitHub Actions CI: syntax checks, JSON validation, pytest, pip-audit CVE scan
- No Docker, no hosted database, no cloud deployment

### Project Structure

```
claude-ads/
├── ads/SKILL.md              # Top-level orchestrator router
├── ads/references/           # On-demand knowledge files (200-line cap enforced)
├── skills/                   # 19 sub-skills (SKILL.md per skill)
├── agents/                   # 7 agents (3 audit + 4 creative)
├── scripts/api/              # Pure-stdlib OAuth adapters (Meta, Google, TikTok)
├── scripts/profile.py        # User profile + audit history CLI
├── tests/                    # pytest suite (schema validation, reference checks)
├── .claude-plugin/           # Claude Code plugin manifest
└── CLAUDE.md                 # Project instructions
```

**Key Observations**:
- Clear separation between orchestrator (ads/), execution units (skills/), long-running agents (agents/), and data-access scripts (scripts/api/).
- Reference files in `ads/references/` act as an on-demand knowledge base loaded only when needed, preserving context budget for actual analysis data.

---

## Individual Member Analyses

### Systems Architect

**Perspective**: Big-picture system coherence and component interaction.

The orchestrator → specialist skill graph is a clean decomposition. The top-level router in `ads/SKILL.md` acts as a thin dispatch layer that stays free of business logic, which is the right separation. The three-tier data access pattern is consistently documented across all platform skills and enforced culturally through CLAUDE.md rules. The main systemic concern is that the 7 agents are invoked via Task tool with `context: fork`, meaning each audit is a separate, isolated model context with no shared memory between them during a run. The orchestrator must therefore collect all output through files rather than in-memory state — this is correct for the Claude Code environment but introduces a dependency on file I/O ordering that is untested.

#### Strengths Identified

1. **Clear routing table**: The `/ads` router is explicit about which sub-skill handles each command, making it easy to trace any user-facing command to its implementation.
2. **Stateless agents**: Each audit agent is independently runnable and produces self-contained output files, which makes individual agent debugging straightforward.
3. **Plugin-first distribution**: The `.claude-plugin/` manifest enables auto-update delivery, significantly reducing the maintenance burden compared to manual install instructions.

#### Concerns Raised

1. **File I/O ordering in multi-agent audit** (Impact: Medium)
   - **Issue**: When three platform agents run in parallel via Task tool, the orchestrator waits for all three JSON files to appear before aggregating. There is no explicit synchronization mechanism — the orchestrator polls or relies on Claude Code's implicit Task tool completion.
   - **Why It Matters**: On slow systems or when one agent errors mid-run, the aggregator might read a partially-written JSON file or silently miss a platform's score.
   - **Recommendation**: Add explicit Task tool completion checks in the orchestrator before reading output files. Document the expected file list and add a test fixture that verifies the aggregator handles missing files gracefully.

2. **No architectural decision records** (Impact: Low)
   - **Issue**: Key design choices (three-tier data access, JSON contract, profile-first state) are documented in CLAUDE.md but not in formal ADRs that record the alternatives considered and the rationale.
   - **Why It Matters**: As contributors rotate, the reasoning behind constraints (e.g., "why pure stdlib?") gets lost, leading to well-intentioned PRs that add external dependencies.
   - **Recommendation**: Create ADRs for the three-tier data access pattern, the JSON output contract, and the profile-first user state design. Three ADRs is a one-afternoon investment.

#### Initial Recommendations

1. **Explicit Task tool completion guard** (Priority: Important, Effort: Small)
   - Add a check in the orchestrator that verifies all expected output files exist before proceeding to aggregation.

2. **Seed ADR backlog** (Priority: Important, Effort: Small)
   - Document the three core design decisions as ADRs so future contributors understand the constraints without reading all of CLAUDE.md.

---

### Domain Expert

**Perspective**: How well the architecture represents the advertising audit domain.

The domain model is well-represented. The skill decomposition maps cleanly to how ad professionals think: platform audit → creative review → budget optimization → competitive research → report generation. The weighted-check approach (~158 checks with impact × ease scoring) mirrors real audit methodology used by agency professionals. The health score (0–100) with ranked fix list is a concrete, actionable output that matches client deliverable expectations.

#### Strengths Identified

1. **Domain-accurate decomposition**: Each sub-skill corresponds to a recognizable agency workflow (audit, creative, landing page, math/ROI, A/B test), meaning the skill names serve as documentation.
2. **Platform-specific specialization**: Separate agents for Meta, Google, and TikTok respect the real differences in ad platform semantics rather than forcing a generic abstraction.
3. **Free-first philosophy matches user reality**: The target audience (freelancers, small agencies) genuinely cannot afford paid SaaS dependencies — the free-tier-first design is a domain constraint, not just a preference.

#### Concerns Raised

1. **Platform changelog staleness** (Impact: Medium)
   - **Issue**: `/ads update` refreshes platform references monthly via WebSearch, but the references themselves are static Markdown files. If a platform makes a breaking API change between updates, skill checks may silently test against obsolete criteria.
   - **Recommendation**: Add a `last_updated` timestamp to each reference file and surface a warning in audit output when the reference is older than 60 days.

2. **Missing industry-template coverage** (Impact: Low)
   - **Issue**: v2.3.0 removed four industry templates (SaaS, B2B enterprise, info products, mobile app) when the dependent platforms were removed. The remaining templates may not cover common use cases for the current platform focus.
   - **Recommendation**: Audit which industries are most common among `/ads plan` users and restore or create templates for the top two missing segments.

#### Initial Recommendations

1. **Reference staleness indicator** (Priority: Important, Effort: Small)
   - Add `last_updated: YYYY-MM-DD` frontmatter to each reference file in `ads/references/`. Surface a deprecation warning in audit output when the reference exceeds the 60-day threshold.

---

### Security Specialist

**Perspective**: Security implications of architecture, credentials, and integrations.

The security posture for a local-only CLI tool is generally good. The no-credentials-in-profile rule (only `*_present: true/false` flags) is a strong guard against accidental token leakage. The pip-audit CVE gate in CI catches known Python dependency vulnerabilities before release. MCP integrations delegate OAuth to the respective MCP servers, keeping tokens outside the codebase.

#### Strengths Identified

1. **No credential storage**: The profile schema explicitly excludes API keys and tokens, reducing the blast radius of a profile file leak.
2. **CVE gate on CI**: pip-audit runs on every push, preventing known-vulnerable dependency versions from shipping.
3. **Principle of least privilege in MCP wiring**: Platform agents declare only the MCP tools they need in their `tools:` frontmatter, not a blanket MCP access grant.

#### Concerns Raised

1. **OAuth redirect-URI handling in direct-API adapters** (Impact: Medium)
   - **Issue**: The scripts in `scripts/api/` implement OAuth flows using stdlib `http.server` for the local redirect URI. Localhost OAuth servers are a well-known CSRF vector if not bound correctly.
   - **Why It Matters**: A malicious page on the same machine could steal the OAuth code before the adapter captures it.
   - **Recommendation**: Verify that the redirect server binds only to `127.0.0.1` (not `0.0.0.0`) and uses a state parameter with sufficient entropy. Add a test that exercises the redirect handler with a mismatched state parameter.

2. **Playwright with user's browser profile** (Impact: Low)
   - **Issue**: The landing-page analysis skill uses Playwright, which may launch with the user's existing browser profile, potentially exposing authenticated sessions to the analysis script.
   - **Recommendation**: Ensure Playwright launches with `--incognito` / a fresh profile context so it cannot access the user's authenticated sessions.

#### Initial Recommendations

1. **Audit OAuth state parameter** (Priority: Important, Effort: Small)
   - Review `scripts/api/` redirect handlers for state parameter generation and server bind address. Fix any gaps.

2. **Playwright incognito mode** (Priority: Nice-to-Have, Effort: Small)
   - Add `browser.new_context()` with a fresh context rather than `browser.new_page()` from a persistent profile.

---

### Maintainability Expert

**Perspective**: Long-term code quality, developer experience, and sustainable evolution.

The codebase has good structural discipline: kebab-case skill directories, explicit routing tables, a 200-line reference cap, and documented rules in CLAUDE.md. The main maintainability risk is that SKILL.md size limits are documented but not enforced by CI, and the `agents/` directory has accreted platform-specific logic in ways that may diverge over time.

#### Strengths Identified

1. **CLAUDE.md as the authoritative rule source**: Development rules are centralized and comprehensive, reducing rule drift across contributors.
2. **Consistent output contract**: The shared `audit-output-schema.json` ensures all platform agents produce structurally compatible output, making cross-platform logic maintainable.
3. **Cross-platform installers tested in CI**: `bash -n install.sh` catches shell syntax errors before they affect end users.

#### Concerns Raised

1. **SKILL.md size not CI-enforced** (Impact: Medium)
   - **Issue**: The 500-line / 5000-token limit is documented in CLAUDE.md but has no corresponding CI check. Reference files have an automated 200-line gate; SKILL.md files do not.
   - **Recommendation**: Add a CI step: `find . -name "SKILL.md" -exec wc -l {} \; | awk '$1 > 500 {print; exit 1}'`

2. **Agent logic duplication risk** (Impact: Medium)
   - **Issue**: The audit methodology in `ads/references/audit-methodology.md` is supposed to be the canonical source for the 7-step process, but each platform agent's SKILL.md must explicitly reference it. A future contributor may copy the methodology inline rather than referencing the file.
   - **Recommendation**: Add a CI grep check: `grep -rn "audit-methodology" agents/ | wc -l` should equal the number of audit agents. Fail if any audit agent doesn't reference the methodology file.

#### Initial Recommendations

1. **Add SKILL.md line-count CI gate** (Priority: Critical, Effort: Small)
   - This is the highest-priority gap: the reference-file gate exists but the more important skill files are unguarded.

2. **Audit-methodology reference check in CI** (Priority: Important, Effort: Small)
   - A one-line grep assertion that all audit agents reference the shared methodology.

---

### Performance Specialist

**Perspective**: System performance, context budget efficiency, and resource utilization.

Performance in a Claude Code skill context means two things: wall-clock latency (how long users wait) and context budget (how many tokens each invocation consumes). Both are well-considered in this architecture.

#### Strengths Identified

1. **Parallel agent dispatch**: The full audit invokes three platform agents simultaneously via Task tool, reducing wall-clock time from ~3× sequential to roughly the slowest single agent.
2. **On-demand reference loading**: Reference files in `ads/references/` are not pre-loaded — they are read only when a specific skill needs them, keeping the base context lean.
3. **PDF generation outside model context**: ReportLab/Matplotlib run as Python scripts, not in model context, so report generation doesn't consume tokens.

#### Concerns Raised

1. **Playwright invocation latency** (Impact: Medium)
   - **Issue**: Browser launch adds 2–5 seconds of cold-start latency to landing-page analysis. On repeated calls in the same session, this could be eliminated by reusing a browser process.
   - **Recommendation**: Consider a `--reuse-browser` flag or a long-lived Playwright subprocess for sessions with multiple landing-page checks.

2. **profile.py subprocess overhead** (Impact: Low)
   - **Issue**: Every user-facing command spawns `python3 scripts/profile.py get` as a subprocess. On macOS with SIP, subprocess spawn can add ~300ms.
   - **Recommendation**: Acceptable at current scale, but document this as a known latency source. If latency becomes noticeable, inline the JSON read directly in the SKILL.md rather than delegating to a subprocess.

#### Initial Recommendations

1. **Benchmark landing-page skill latency** (Priority: Nice-to-Have, Effort: Small)
   - Add a timing note in SKILL.md so users understand the browser launch overhead and can plan accordingly.

---

### Implementation Strategist

**Perspective**: Change sequencing, blast radius, and readiness for future evolution.

The current architecture is well-positioned for incremental change. The skill graph is modular: adding a new platform requires a new sub-skill, a new agent, and a new API adapter — no changes to existing platform skills. Removing a platform (as done in v2.3.0 when YouTube, LinkedIn, Apple, and Microsoft were dropped) requires only deleting the relevant files. This low coupling is a significant implementation advantage.

#### Strengths Identified

1. **Low coupling between platforms**: Adding or removing a platform has a well-defined, minimal blast radius (one skill, one agent, one adapter).
2. **Version-controlled schema**: `audit-output-schema.json` is in the repo, so schema changes are reviewable in PRs and breaking changes are detectable before merge.
3. **Installer idempotency**: `install.sh` / `install.ps1` can be re-run safely, reducing the risk of partial-upgrade states.

#### Concerns Raised

1. **Profile schema migration path** (Impact: Medium)
   - **Issue**: `~/.claude-ads/profile.json` is a user-local file outside the repo. When `profile-schema.json` adds new required fields in a future version, existing profiles will fail validation silently or with an unhelpful error.
   - **Why It Matters**: User-local state is the hardest thing to migrate — you can't just run a DB migration.
   - **Recommendation**: Add a `schema_version` field to `profile.json` and implement a migration function in `profile.py` that upgrades old schemas when a version mismatch is detected at startup.

2. **No deprecation path for removed skills** (Impact: Low)
   - **Issue**: When skills are removed (e.g., `/ads apple`), users who have memorized the old commands receive unhelpful "skill not found" errors.
   - **Recommendation**: Add a deprecation notice in the router for recently removed commands that redirects users to the replacement.

#### Initial Recommendations

1. **Profile schema versioning and migration** (Priority: Important, Effort: Medium)
   - This protects the growing installed base from silent breakage on upgrade. A `schema_version` field and a `migrate()` function in `profile.py` would cover the next several schema iterations.

---

### AI Engineer

**Perspective**: AI integration quality, agent orchestration patterns, and system evaluation.

This is an unusually well-architected Claude Code skill for a domain tool. The orchestrator-plus-specialists pattern is correctly implemented: the top-level skill stays thin and delegates depth to agents; agents use `context: fork` to isolate their analysis from the orchestrator's context window; output flows through files (the only reliable IPC in this environment). The profile-first design for user state is the right approach for a tool that benefits from accumulating context over time.

#### Strengths Identified

1. **Correct use of context: fork**: Agent isolation prevents cross-contamination of audit findings between platforms and avoids context window exhaustion on full audits.
2. **Structured output with schema validation**: JSON contracts make the AI output machine-readable, enabling deterministic score aggregation rather than asking the model to parse its own previous output.
3. **Self-updating references**: `/ads update` is a clever pattern — using WebSearch to refresh platform knowledge means the tool stays accurate without manual curation of static facts.

#### Concerns Raised

1. **No evaluation harness for audit accuracy** (Impact: Medium)
   - **Issue**: The ~158 audit checks are applied by agents reading platform data, but there is no test dataset (golden inputs + expected outputs) to verify that check logic is correct. Regression in audit accuracy would be invisible in CI.
   - **Why It Matters**: For an audit tool, correctness of findings is the primary user value. A check that silently stops detecting an issue is worse than no check at all.
   - **Recommendation**: Create a small eval dataset: 3–5 canned platform export files (one "healthy" account, one with known issues) with expected audit JSON outputs. Run these through the agent logic in CI using the manual-export tier.

2. **Orchestrator has no retry on agent failure** (Impact: Medium)
   - **Issue**: If one of the three parallel audit agents fails (API timeout, MCP error), the orchestrator currently has no documented retry or partial-result recovery path.
   - **Recommendation**: Document the expected behavior when one agent fails and add a graceful degradation path: surface the results from the two successful agents with a note that the third is unavailable.

#### Initial Recommendations

1. **Golden-file eval dataset** (Priority: Important, Effort: Medium)
   - Even a minimal eval (one healthy, one problematic account fixture) would catch audit logic regressions that pure schema validation misses.

2. **Agent failure graceful degradation** (Priority: Important, Effort: Small)
   - Document and implement the partial-result path in the orchestrator.

---

### Pragmatic Enforcer

**Perspective**: YAGNI — what complexity is necessary right now versus what can be deferred?

The overall system is pragmatically scoped. The v2.3.0 platform reduction (from 7 to 3) was the right call — maintaining 7 platform integrations at different maturity levels creates unsustainable support burden for a small team. The free-tier-first constraint is a forcing function for simplicity: you cannot add a complex paid integration without explicitly opting in. However, there are a few places where complexity has crept in ahead of demonstrated need.

#### Concerns Raised

1. **4 creative agents vs. 3 audit agents — is creative scope justified?** (Impact: Low)
   - **Issue**: The system has 4 creative agents (strategist, visual designer, copy writer, format adapter) but the audit path is the primary value proposition. Creative generation via Claude is broadly available; ad-platform-specific auditing is the differentiator.
   - **Pragmatic question**: Do the 4 creative agents carry their weight in user usage vs. the 3 audit agents? If creative usage is low, the maintenance surface is higher than the value delivered.
   - **Recommendation**: Add usage telemetry (even a simple "which commands are used?" log in profile history) to validate creative agent ROI before adding more creative features.

2. **PDF report generation: is it the right layer?** (Impact: Low)
   - **Issue**: ReportLab + Matplotlib are non-trivial Python dependencies for PDF output. Many users would be satisfied with the Markdown audit output.
   - **Pragmatic question**: Does PDF generation justify the dependency and complexity? Could a simpler approach (Markdown → user's preferred tool) cover 80% of the use case?
   - **Recommendation**: Keep PDF for now (it's already built), but don't expand it or add dependencies to it without evidence of user demand.

#### Initial Recommendations

1. **Track skill invocation frequency in audit history** (Priority: Nice-to-Have, Effort: Small)
   - Log which skill was invoked in `~/.claude-ads/history/index.json`. This costs nothing and provides the data needed to make informed future scope decisions.

---

### Python Expert (Dr. Sarah Chen)

**Perspective**: Python code quality, dependency discipline, and stdlib-first patterns.

The pure-stdlib requirement for `scripts/api/` is the right decision and is well-enforced culturally. The scripts I reviewed follow the constraint. However, the CI pip-audit check runs against the full `requirements.txt`, which includes non-stdlib packages (Playwright, ReportLab, Matplotlib, Pillow, Requests). This is correct and appropriate — but the CVE audit cadence (per-push) may generate noise if upstream packages release frequent patch versions with low-severity CVEs.

#### Strengths Identified

1. **Pure-stdlib API adapters**: No external dependencies in `scripts/api/` means the adapters work in any Python 3.10+ environment without a pip install step, which is critical for the "zero setup" user experience.
2. **CVE gate on CI**: pip-audit catches known vulnerabilities before they ship to users.
3. **Type annotations and docstrings in scripts**: `profile.py` has proper CLI interface and JSON output, following the documented standards.

#### Concerns Raised

1. **requirements.txt has no version upper bounds** (Impact: Medium)
   - **Issue**: Pinning exact versions (e.g., `playwright==1.40.0`) prevents CVEs from sneaking in via automatic upgrades, but it also means users on fresh installs always get a known-good version. However, if the exact version is pulled from PyPI and later yanked, the install breaks with no fallback.
   - **Recommendation**: Use minimum-version pins with pip-audit to catch CVEs, and document the policy. Consider adding `pip install --upgrade-strategy=only-if-needed` to the installer to reduce dependency churn.

2. **No type annotations on API adapter functions** (Impact: Low)
   - **Issue**: `scripts/api/` functions lack type annotations, making it harder to verify the shape of returned data without running the code.
   - **Recommendation**: Add `-> dict` or `-> list[dict]` annotations to public functions in the API adapters.

#### Initial Recommendations

1. **Document dependency pinning policy** (Priority: Important, Effort: Small)
   - A one-paragraph `scripts/api/README.md` section explaining the pinning strategy and how to update pins safely.

---

### Claude Skills Architect (Marco Delgado)

**Perspective**: Claude Code skill design, MCP integration patterns, and agent orchestration correctness.

The skill design follows the documented conventions well: sub-skill frontmatter is canonical (`name`, `description`, `user-invokable: false`, `allowed-tools`), platform agents declare only their needed MCP tools, and the orchestrator delegates rather than reimplements. The MCP integration pattern in `ads/references/mcp-meta-integration.md` is the right approach — a mapping file that connects audit checks to specific MCP tool calls prevents ad-hoc, undocumented MCP usage from spreading.

#### Strengths Identified

1. **Canonical MCP integration pattern**: The `mcp-<platform>-integration.md` reference file pattern ensures MCP wiring is reviewable and auditable.
2. **Correct Task tool usage**: `context: fork` is used consistently, which is the correct isolation mode for parallel long-running agents.
3. **Skill routing table in orchestrator**: The explicit command-to-skill mapping in `ads/SKILL.md` makes the dispatch logic transparent and easy to extend.

#### Concerns Raised

1. **SKILL.md size not CI-enforced** (Impact: High for this stack)
   - **Issue**: Skill file bloat is the #1 operational failure mode for Claude Code skills. A 600-line SKILL.md consumes a significant fraction of the context window before any user data is loaded.
   - **Recommendation**: This is the single most important CI gap. Add the line-count check immediately.

2. **No test coverage for MCP tool → check mapping** (Impact: Medium)
   - **Issue**: The `mcp-<platform>-integration.md` files define which MCP tools map to which audit checks, but there is no automated test that verifies all documented checks have a corresponding MCP tool invocation in the agent.
   - **Recommendation**: A pytest fixture that parses the integration mapping file and verifies each check ID appears in the corresponding agent file would catch mapping drift.

#### Initial Recommendations

1. **SKILL.md line-count CI gate** (Priority: Critical, Effort: Small)
   - Mirrors the Maintainability Expert's recommendation. This is the highest-ROI single CI addition.

2. **MCP integration coverage test** (Priority: Important, Effort: Medium)
   - Parse `mcp-*-integration.md` and verify check IDs against agent SKILL.md content.

---

## Collaborative Synthesis

### Common Themes

**Strengths** (praised by multiple members):
1. **Free-first data access pattern**: Independently praised by Systems Architect, Domain Expert, and Claude Skills Architect. The three-tier design is both architecturally sound and domain-correct for the target audience.
2. **JSON output contracts with schema validation**: Flagged as a strength by AI Engineer, Claude Skills Architect, and Maintainability Expert. The shared schema is a rare example of a skill system with a formal output contract.
3. **Minimal external dependencies**: Python Expert and Pragmatic Enforcer both noted the stdlib-first discipline as a meaningful constraint that reduces operational complexity.

**Concerns** (flagged by multiple members):
1. **SKILL.md size not CI-enforced**: Flagged independently by Maintainability Expert and Claude Skills Architect as the highest-priority gap. Both agree the reference-file gate exists but the more critical skill files are unguarded.
2. **Audit accuracy has no golden-file eval**: AI Engineer and Domain Expert both raised the absence of a ground-truth test dataset for audit correctness. Schema validity ≠ semantic correctness.
3. **Profile schema migration path missing**: Implementation Strategist and Python Expert both flagged the risk of user-local state breaking silently on upgrade.

**Disagreements**:
- **PDF generation scope**: Pragmatic Enforcer questioned whether PDF justifies ReportLab + Matplotlib; Performance Specialist noted that running PDF generation outside model context is actually a good design decision. Resolution: keep PDF but don't expand it without usage data.

### Prioritized Findings

**Critical (Address Immediately)**:
1. **SKILL.md line-count CI gate**: The reference-file cap is enforced but the more impactful skill files are not. One `find` + `awk` command in CI fixes this.
2. **Orchestrator file-I/O ordering and partial-failure behavior**: Undocumented and untested. A single failing agent in a three-agent parallel audit produces an ambiguous outcome.

**Important (Address in Near Term)**:
1. **Golden-file eval dataset**: Even 2–3 canned audit fixtures would catch semantic regressions that schema validation misses.
2. **Profile schema versioning + migration**: Protects the growing installed base from silent breakage on future schema changes.
3. **OAuth state parameter and server bind address audit**: Low effort, medium security impact.
4. **Seed ADR backlog**: Three ADRs covering the core design decisions would prevent future contributors from re-litigating resolved choices.

**Nice-to-Have (Consider for Future)**:
1. **Skill invocation telemetry**: Logging which skills are used would enable data-driven scope decisions.
2. **Reference staleness indicator**: `last_updated` frontmatter in reference files would surface outdated platform checks.
3. **Playwright incognito mode**: Small security improvement for landing-page analysis.

---

## Recommendations

### Immediate Actions (0–2 Weeks)

1. **Add SKILL.md line-count CI gate**
   - **Why**: The existing reference-file cap is enforced but the more context-expensive skill files are not. Skill file bloat is the primary operational failure mode for Claude Code skills.
   - **How**: Add to `.github/workflows/ci.yml`: `find . -name "SKILL.md" -exec wc -l {} \; | awk '$1 > 500 {print; exit 1}'`
   - **Effort**: 1 hour

2. **Document orchestrator partial-failure behavior**
   - **Why**: Three parallel agents with no defined behavior on partial failure is a silent reliability gap.
   - **How**: Add a "failure modes" section to `ads/SKILL.md` and the audit orchestration logic. Implement a graceful degradation path: surface results from successful agents with a clear notice about the failed one.
   - **Effort**: 2–3 hours

3. **Audit OAuth state parameter and server bind address**
   - **Why**: Localhost OAuth CSRF is a known attack vector; verification is low effort.
   - **How**: Review `scripts/api/` redirect handlers. Confirm `127.0.0.1` bind and state parameter with `secrets.token_urlsafe(16)`.
   - **Effort**: 1–2 hours

### Short-Term Actions (2–8 Weeks)

1. **Seed ADR backlog with three core decisions**
   - Three-tier data access pattern, JSON output contract, profile-first user state.
   - **Effort**: 3–4 hours (one afternoon)

2. **Profile schema versioning and migration function**
   - Add `schema_version` to `profile.json`. Add `migrate()` in `profile.py` that upgrades old schemas on startup.
   - **Effort**: Half day

3. **Create golden-file eval dataset**
   - Two canned Meta export fixtures (healthy account + account with known issues) + expected JSON audit output. Wire into `pytest tests/`.
   - **Effort**: 1–2 days

### Long-Term Initiatives (2–6 Months)

1. **MCP integration coverage tests**
   - Parse `mcp-*-integration.md` mapping files and assert all check IDs appear in the corresponding agent files.
   - **Effort**: 1–2 days

2. **Skill invocation telemetry**
   - Log invoked skill name + timestamp to `~/.claude-ads/history/index.json`. Use this data to validate creative agent ROI and guide future scope decisions.
   - **Effort**: Half day

---

## Suggested Next Steps

1. **Add SKILL.md line-count CI gate** — the single highest-ROI CI addition, implementable in under an hour.
2. **Create three seed ADRs** for the core design decisions — prevents future contributors from re-litigating resolved choices.
3. **Run `List architecture members`** to verify the customized team (Python Expert + Claude Skills Architect added).
4. **Run `What's our architecture status?`** to confirm the framework is wired up correctly.
5. **Document the orchestrator partial-failure path** — the next highest reliability gap after the CI gate.

**Next Review**: 2026-08-20 (3 months)

---

*Analysis conducted using the AI Software Architect framework v1.5.4. Team: Systems Architect, Domain Expert, Security Specialist, Maintainability Expert, Performance Specialist, Implementation Strategist, AI Engineer, Pragmatic Enforcer, Python Expert (Dr. Sarah Chen), Claude Skills Architect (Marco Delgado).*
