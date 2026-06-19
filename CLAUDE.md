# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a mono-repo containing one project:

- **`claude-ads/`** — A Claude Code skill for paid advertising audits across Meta, Google, and TikTok. See `claude-ads/CLAUDE.md` for full architecture, commands, and development rules.

## Build & Test

```bash
# Run all tests (from claude-ads/)
cd claude-ads && pytest tests/

# Validate reference file length (must produce no output)
find claude-ads/ads/references -name "*.md" -exec wc -l {} \; | awk '$1 > 200'

# Validate JSON schemas
python3 -c "import json; json.load(open('claude-ads/ads/references/audit-output-schema.json'))"

# Check shell script syntax
bash -n claude-ads/install.sh && bash -n claude-ads/uninstall.sh
```

CI runs all of the above on every push and PR to `main`.

## Key Conventions

- Python 3.10+, pure stdlib for API adapters (`scripts/api/`)
- SKILL.md files must stay under 500 lines / 5000 tokens
- Reference files under 200 lines
- Kebab-case for skill directories
- Agents invoked via Task tool with `context: fork`, never via Bash
- Audit agents must emit both `.md` (human) and `.json` (machine) outputs validated against `ads/references/audit-output-schema.json`
- Three free data tiers per platform: MCP (Capa 1) → Direct API (Capa 2) → Manual exports (Capa 3)
- No hardcoded credentials; secrets stay in env vars or MCP config
