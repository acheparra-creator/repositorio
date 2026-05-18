---
name: ads-carousel
description: "Multi-card carousel ad builder for Meta (Facebook + Instagram) and TikTok. Guides users through structuring carousel narratives, writing per-card copy within platform limits, and generating card images. Outputs carousel-brief.md ready for /ads generate. Use when user says carousel, multi-card ad, swipeable ad, or carousel brief."
user-invokable: false
---

# Ads Carousel: Multi-Card Carousel Ad Builder

Builds structured carousel ad briefs for Meta and TikTok. Each card gets its
own image prompt, headline, description, and optional per-card URL. Outputs
`carousel-brief.md` for review and image generation.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/ads carousel` | Interactive carousel builder → `carousel-brief.md` |
| `/ads carousel --platform meta` | Meta-only (FB + IG) |
| `/ads carousel --platform tiktok` | TikTok carousel only |
| `/ads carousel --cards 5` | Pre-set card count |

## Platform Specs

### Meta Carousel
- Cards: 2–10
- Ratio: 1:1 (1080×1080 each card)
- Headline per card: ≤40 chars
- Description per card: ≤20 chars
- Primary text (top): ≤125 chars visible before "See More"
- CTA: single platform button applies to all cards (or per-card in some placements)
- Per-card URL: supported (different destination per card)
- Loops: optional (last card links back to first)

### TikTok Carousel
- Cards: 2–10 (static images only; video carousel not supported)
- Ratio: 9:16 (1080×1920) or 1:1 (1080×1080); 9:16 preferred
- Safe zone: X:40–940, Y:150–1470
- Caption (shared): ≤150 chars
- Per-card text: not supported — single caption applies to all cards
- CTA: single CTA button

## Process

### Step 1: Check Brand Profile

```bash
python3 scripts/profile.py get
```

- Exit 0 → use saved `context.industry`, `context.primary_goal`, `context.active_platforms`.
- Exit 2 → proceed inline; offer to save profile at the end.

Load `brand-profile.json` from cwd if present (for visual style injection).

### Step 2: Collect Carousel Parameters

If `--platform` or `--cards` were passed, skip matching questions.

Ask in a single message (omit already-provided values):

1. **Platform**: Meta (FB + IG) · TikTok · Both
2. **Number of cards**: 3–5 recommended (2–10 allowed)
3. **Narrative type** — choose one:
   - **Story arc**: cards tell a sequential story (Problem → Agitate → Solve → Proof → CTA)
   - **Product showcase**: each card = one product or feature
   - **Step-by-step**: how-to / tutorial format
   - **Before/After**: contrast across cards
   - **Social proof**: one testimonial or stat per card
4. **Offer or message**: any specific promotion or core message to anchor copy
5. **Per-card URLs?** (Meta only): different landing pages per card, or single URL?

### Step 3: Load Copy Reference

Read `ads/references/copy-frameworks.md`. Select framework based on narrative type:

| Narrative | Framework |
|-----------|-----------|
| Story arc | PAS (Problem, Agitate, Solve) or BAB |
| Product showcase | FAB (Features, Advantages, Benefits) |
| Step-by-step | 4P (Promise, Picture, Proof, Push) |
| Before/After | BAB (Before, After, Bridge) |
| Social proof | Star-Story-Solution |

### Step 4: Build Card Outlines

Generate one outline per card. Each outline:

```
Card N
  Headline: [≤40 chars — Meta] / [caption shared for TikTok]
  Description: [≤20 chars — Meta only]
  Visual hook: [1 sentence describing the image]
  URL: [destination or "shared" — Meta only]
  Narrative role: [how this card advances the sequence]
```

Present card outlines to the user. Allow edits before generating the full brief.
Wait for explicit approval ("looks good", "proceed", "yes") before continuing.

### Step 5: Write carousel-brief.md

After user approval, write `carousel-brief.md` to cwd.

#### carousel-brief.md Format

```markdown
# Carousel Brief: [brand_name or "Untitled"]
**Generated:** [date]
**Platform:** [Meta | TikTok | Both]
**Cards:** [N]
**Narrative:** [narrative type]
**Objective:** [from profile or user input]

## Primary Text (shared)
[≤125 chars for Meta; ≤150 chars for TikTok]

## Cards

### Card 1: [Title / Role]
**Headline:** [≤40 chars — Meta; omit for TikTok]
**Description:** [≤20 chars — Meta only]
**URL:** [destination URL or "shared"]
**Image Brief:**
  Prompt: [generation prompt]
  Dimensions: 1080×1080 (Meta) / 1080×1920 (TikTok)
  Safe zone notes: [constraint or "None"]
  Brand injection: [colors, style from brand-profile.json if available]

### Card 2: [Title / Role]
[same structure]

[repeat for all cards]

## Copy Notes
- Framework applied: [framework name]
- Narrative flow: [1-sentence description of the arc]
- CTA: [button text]
- Split-test suggestion: [one alternative headline or primary text to A/B test]
```

### Step 6: Confirm and Offer Next Steps

After writing the file, confirm output and present next steps:

```
✓ carousel-brief.md generated ([N] cards, [platform])

Next steps:
  1. Review carousel-brief.md and adjust any card copy or image prompts
  2. Run /ads generate to produce card images from the briefs
  3. Upload assets and copy to Meta Ads Manager or TikTok Ads Manager
  4. Run /ads test to design an A/B test (narrative type A vs B)
```

## Quality Gates

- **Narrative coherence**: each card must advance the stated narrative — no random card order.
- **Copy limits**: enforce Meta (≤40/≤20 headline/description) and TikTok (≤150 caption) limits. Truncate to limit and flag if user input exceeds.
- **Minimum 2 cards, maximum 10**: reject out-of-range requests with an explanation.
- **Image briefs**: every card must have a generation prompt and correct dimensions.
- **TikTok safe zone**: flag any prompt placing critical elements outside X:40–940, Y:150–1470.
- **Andromeda diversity (Meta)**: cards must use distinct visuals and angles; flag if all card prompts are near-identical.

## Meta-Specific Notes

- Advantage+ Catalog: if the user has a product catalog, recommend Catalog Carousel (dynamic) over manual carousel — Meta auto-populates cards from catalog with real-time inventory.
- Loop toggle: if the last card's URL matches the first card's product, recommend enabling the carousel loop option.
- Mobile preview: remind user to preview on mobile in Ads Manager before publishing — carousel swipe is touch-driven.

## TikTok-Specific Notes

- TikTok Carousel is static images only; video carousels use a different format (Spark Ads series).
- 9:16 ratio preferred; safe zone overlay at Y:150–1470 hides UI chrome.
- Single caption applies to all cards — make it a hook that invites swiping ("Swipe to see all 5 →").
- TikTok carousels work well for product lookbooks, tutorials, and listicles.
