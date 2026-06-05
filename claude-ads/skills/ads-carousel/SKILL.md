---
name: ads-carousel
description: "Carousel ad creator for Meta and LinkedIn. Builds multi-card carousel briefs with narrative arc, per-card copy, and image generation prompts. Reads brand-profile.json and optional campaign-brief.md. Outputs carousel-brief.md ready for /ads generate. Triggers on: carousel ad, carrusel, carousel campaign, multi-card ad, carousel brief, create carousel, carousel copy, carousel images."
user-invokable: false
argument-hint: "[--platform meta|linkedin] [--cards N] [--objective sales|leads|awareness|retargeting]"
---

# Ads Carousel: Multi-Card Ad Builder

Generates a structured carousel brief with narrative arc, per-card copy, and image
generation prompts. Outputs `carousel-brief.md` for use by `/ads generate`.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/ads carousel` | Full carousel brief → `carousel-brief.md` |
| `/ads carousel --platform meta` | Meta carousel only (2-10 cards, 1:1) |
| `/ads carousel --platform linkedin` | LinkedIn carousel only (document format) |
| `/ads carousel --cards 5` | Set a specific card count |
| `/ads carousel --objective retargeting` | Optimize arc for retargeting funnel |

## Platform Specs

### Meta Carousel
| Spec | Value |
|------|-------|
| Cards | 2–10 |
| Aspect ratio | 1:1 |
| Dimensions | 1080×1080px |
| Headline per card | ≤40 chars |
| Description per card | ≤20 chars |
| Primary text (intro) | ≤125 chars |
| Link | Each card can have a unique URL |

### LinkedIn Carousel
| Spec | Value |
|------|-------|
| Cards | 2–20 |
| Aspect ratio | 1:1 or 4:5 |
| Dimensions | 1080×1080 or 1080×1350px |
| Headline per card | ≤150 chars |
| File format | PDF (uploaded as document ad) |
| First card | Acts as the cover — must stop the scroll |

## Process

### Step 1: Check Profile and Brand Context

Run `python3 scripts/profile.py get`. On exit 2 (no profile), surface:
> "No profile found. Run `/ads start` for full setup, or describe your brand and I'll continue."

Allow the user to proceed inline. Load `brand-profile.json` from the current directory
if present. Note voice, visual style, and target audience for card copy tone.

### Step 2: Check for Existing Campaign Brief

Look for `campaign-brief.md` in the current directory.

- **Found**: Read `## Campaign Concepts` to align the carousel arc with an existing concept.
  Ask: "I found a campaign brief. Which concept should this carousel be based on? (or 'none')"
- **Not found**: Continue. The carousel will stand alone.

### Step 3: Collect Carousel Parameters

If `--platform`, `--cards`, or `--objective` flags were provided, use those values
and skip the corresponding questions.

Ask (combine into one message; omit any already provided via flags):
1. **Platform**: Meta · LinkedIn · Both
2. **Objective**: Sales/Revenue · Leads/Demos · Brand Awareness · Retargeting · Product Showcase
3. **Product or offer**: What is being featured in this carousel?
4. **Card count**: How many cards? (Meta default: 5 · LinkedIn default: 7)
5. **Narrative style**: Story arc · Feature list · Before/After · Step-by-step · Social proof

### Step 4: Define Narrative Arc

Based on objective and narrative style, map a card-by-card arc:

| Narrative Style | Arc Pattern |
|-----------------|-------------|
| Story arc | Hook → Problem → Tension → Solution → Proof → CTA |
| Feature list | Hook → Feature 1 → Feature 2 → Feature 3 → Comparison → CTA |
| Before/After | Hook → Before state → Pain point → After state → How → CTA |
| Step-by-step | Hook → Step 1 → Step 2 → Step 3 → Result → CTA |
| Social proof | Hook → Stat → Testimonial 1 → Testimonial 2 → Guarantee → CTA |

**Card 1 is always the hook** — it must stop the scroll with a bold claim, question,
or visual contrast. Never start with your brand name or logo.

**Last card is always the CTA** — clear action, matching landing page message.

### Step 5: Spawn Copy Writer Agent

Spawn the `copy-writer` agent using the Task tool with `context: fork`.

Pass:
- The narrative arc from Step 4
- Platform character limits
- Brand voice from brand-profile.json (or inline description)
- Objective and offer

The agent writes per-card copy:
- **Card intro** (primary text for the overall carousel, ≤125 chars — Meta only)
- **Per card**: headline + description within platform limits
- **CTA card**: headline + button label recommendation

Wait for `copy-writer` to **fully complete** before continuing.

### Step 6: Spawn Visual Designer Agent

Spawn the `visual-designer` agent using the Task tool with `context: fork`.

Pass:
- Card count and dimensions (1080×1080 for Meta; 1080×1080 or 1080×1350 for LinkedIn)
- Narrative arc and per-card copy from Step 5
- Brand visual style
- Instruction: maintain consistent visual style across all cards (same background
  palette, typography system, and lighting — carousel cards scroll together and
  must read as a cohesive set)

The agent writes one image generation brief per card.

Wait for `visual-designer` to **fully complete** before continuing.

### Step 7: Write carousel-brief.md

Assemble the full brief from Steps 4–6 following the format spec below.
Write to `carousel-brief.md` in the current directory.

### Step 8: Present Summary

```
✓ carousel-brief.md generated

Summary:
  Platform:  [Meta / LinkedIn / Both]
  Cards:     [N]
  Objective: [objective]
  Arc:       [narrative style]
  Copy:      [N] card headlines + descriptions ready
  Images:    [N] generation briefs ready

Next steps:
  1. Review carousel-brief.md and adjust any card copy
  2. Run `/ads generate` to produce card images from the briefs
  3. Upload to [Meta Ads Manager / LinkedIn Campaign Manager]
```

## carousel-brief.md Format Specification

The section headings below are a **parsing contract** — downstream agents depend on exact names.

```markdown
# Carousel Brief: [brand_name]
**Generated:** [date]
**Platform:** [Meta / LinkedIn / Both]
**Objective:** [objective]
**Cards:** [N]
**Arc:** [narrative style]

## Brand Context
[2-sentence synthesis of voice and visual identity from brand-profile.json or inline input]

## Campaign Alignment
[Concept name from campaign-brief.md, or "Standalone carousel"]

## Narrative Arc

| Card | Role | Core Message |
|------|------|-------------|
| 1 | Hook | [one-line] |
| 2 | [arc role] | [one-line] |
| ... | ... | ... |
| N | CTA | [one-line] |

## Copy Deck

### Primary Text (carousel intro — Meta only)
[≤125 chars]

### Card 1 — [Role: Hook]
**Headline:** [≤40 chars Meta / ≤150 chars LinkedIn]
**Description:** [≤20 chars Meta / N/A LinkedIn]
**Image direction:** [2-sentence visual description]

### Card 2 — [Role]
[same structure]

[repeat for all cards]

## Image Generation Briefs

### Card 1 Image
**Prompt:** [exact generation prompt]
**Dimensions:** 1080×1080
**Safe zone notes:** Keep critical elements within center 900×900px; avoid edges
**Style consistency:** [shared palette/typography note — same across all cards]

### Card 2 Image
[same structure]

[one brief per card]

## Upload Checklist

**Meta Carousel:**
- [ ] All card images: 1080×1080, ≤30MB, JPG or PNG
- [ ] Headlines ≤40 chars per card
- [ ] Descriptions ≤20 chars per card
- [ ] Primary text ≤125 chars
- [ ] Each card URL configured (or single destination URL)
- [ ] Advantage+ Creative enhancements reviewed

**LinkedIn Carousel:**
- [ ] Export all card images as a single PDF (in card order)
- [ ] First card is scroll-stopping (cover image)
- [ ] PDF ≤100MB
- [ ] Introductory text filled in Campaign Manager
```

## Quality Gates

- **Card 1 must be a hook**: no brand name as the opener; bold claim, question, or visual tension
- **Visual consistency**: all cards share the same background palette and typography — checked by format-adapter
- **Copy within limits**: every headline and description validated against platform character limits before writing
- **Arc completeness**: first card = hook, last card = CTA — no exceptions
- **Minimum cards**: Meta ≥2, LinkedIn ≥3 (a 1-card carousel is a single image ad — use `/ads create` instead)

## Meta-Specific Rules

- Enable **Advantage+ Catalog** if the carousel features products from a catalog feed
- For retargeting carousels: use dynamic product cards (Meta auto-fills from catalog)
- Frequency cap recommendation: ≤3 impressions per user per 7-day window for carousel retargeting
- Andromeda note: carousel cards are evaluated as a unit — visual diversity between cards within the carousel is encouraged; between carousels, use distinct hooks to avoid Andromeda clustering

## LinkedIn-Specific Rules

- Upload as a **Document Ad**, not a standard carousel — higher organic reach on LinkedIn
- First card = cover; design it to stand alone in the feed before a user swipes
- Professional tone always; avoid urgency language ("Act now!") — underperforms on LinkedIn
- Optimal card count: 5–8 (more than 10 cards drops completion rate significantly)
