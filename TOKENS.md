# Design tokens

Source of truth: `design-reference/design.md` (brand prose) and
`design-reference/arohi_wellness/DESIGN.md` (Stitch-generated color/type
frontmatter), cross-checked against the actual class usage in
`design-reference/*/code.html`. Implemented in `web/app/globals.css` (CSS
custom properties) and `web/tailwind.config.ts` (`theme.extend`).

Pages are **not** converted yet — this is infrastructure only. `login`/`signup`
still use the placeholder `pink-*` scale from the initial scaffold; those are
left untouched on purpose (see "What wasn't touched" below).

## Brand pink base

| Token | CSS var | Value | Source |
|---|---|---|---|
| Primary | `--color-primary` | `#FF6B9D` | design.md: "Primary #FF6B9D" |
| Blush | `--color-blush` | `#FFE4EC` | design.md: "blush surfaces #FFE4EC" |
| Deep | `--color-deep` | `#C2185B` | design.md: "deep accent #C2185B" |

Tailwind: `brand.primary`, `brand.blush`, `brand.deep` → `bg-brand-primary`,
`text-brand-deep`, etc.

Neutral surface system (also extracted, not invented): `--background
#FFF8F8`, `--foreground #25181C`, `--surface #FFFFFF`, `--border #F5DCE3` —
from `arohi_wellness/DESIGN.md`'s `background`/`on-surface`/
`surface-container-lowest`/`outline-variant` roles.

## Four phase palettes

| Phase | Accent(s) | Source |
|---|---|---|
| Menstrual | `#E63970` | "menstrual warm rose" |
| Follicular | `#FF8FB1` | "follicular blush-coral" |
| Ovulatory | `#FF4081` + `#FFD54F` (gold) | "ovulatory vivid pink + gold" |
| Luteal | `#CE93D8` | "luteal mauve-lavender" |

Ovulatory is the only phase with two source-defined colors; the others get a
single accent. Tailwind: `phase.menstrual.DEFAULT`, `phase.ovulatory.accent`,
`phase.luteal["accent-2"]`, etc.

### Per-phase token tiers

Each phase has up to four CSS vars:

- **`--phase-X`** — decorative fill: icons, wheel segments, badges, gradient stops.
- **`--phase-X-soft`** — light tint for card/chip backgrounds (e.g. `bg-phase-luteal/20`-style surfaces in the Stitch mockups).
- **`--phase-X-text`** — a darkened, AA-safe variant for when the phase color is used *as text color* directly on `--background`/`--surface`. Needed because `home_dashboard/code.html` renders `text-phase-luteal` on a `text-display-lg` headline ("Luteal Phase") — the raw accents fail AA as text (see audit below), so a separate tier exists for that specific use.
- **`--phase-ovulatory-accent-text`** — same idea, for the gold accent specifically.

`--phase-luteal-accent-2` (`#9B6EA2`) is the one **derived, not sourced**
value: design-reference has no second luteal color (menstrual pairs with
brand `deep`, follicular pairs with brand `primary`, ovulatory already has
its own gold — luteal has nothing to pair with). Derived as `phase-luteal`
at 75% HSL lightness, used only as the luteal `--accent-2`/gradient partner.

## PhaseTheme provider

`web/components/phase-theme.tsx` exports `PhaseThemeProvider` and
`usePhaseTheme()`. The provider sets `data-phase="<phase>"` on
`document.documentElement`; `globals.css` has one `[data-phase="..."]` block
per phase that swaps `--accent`, `--accent-2`, and `--gradient`
(`linear-gradient(135deg, accent, accent-2)`) for whatever's currently active.

```tsx
const { phase, setPhase } = usePhaseTheme();
// <div className="bg-accent text-on-accent" /> now follows whichever
// phase is active, without knowing which one that is.
```

Not yet mounted in `app/layout.tsx` — wire it in when pages actually start
consuming phase theming, per "do not convert pages yet."

## Fonts

Nunito Sans (weights 400/600/700/800) — the only typeface actually used
across every `code.html` export, despite `design.md`'s vaguer "e.g.
Poppins/Nunito." Imported via `next/font/google` in `app/layout.tsx`,
exposed as `--font-nunito-sans`, wired to Tailwind's `font-sans`.

Not extracted yet: the named type scale (`display-lg`, `headline-lg`,
`body-sm`, etc.) and the spacing/radius scale in `arohi_wellness/DESIGN.md`'s
frontmatter. Both exist in the source and can be lifted into
`tailwind.config.ts` (`fontSize`, `spacing`, `borderRadius`) when pages are
actually converted — out of scope for this pass, which was colors + phases
+ fonts + the theme provider.

Also unaddressed: Material Symbols Outlined, used for every icon in the
mockups. Needs its own decision later (next/font supports it too, or a React
icon library) — not needed until pages are converted.

## Contrast audit (WCAG AA)

Computed via the standard relative-luminance formula, not eyeballed.

**Soft tints, with `--foreground` text (chips/cards)** — all pass comfortably,
no adjustment needed:

| Surface | Contrast |
|---|---|
| menstrual-soft | 13.98 |
| follicular-soft | 15.50 |
| ovulatory-soft | 14.70 |
| luteal-soft | 12.91 |

**Raw phase accents as a solid fill, with white text** — every one failed
AA (4.5 for normal text):

| Accent | vs white | vs `--foreground` |
|---|---|---|
| menstrual | 4.05 fail | 4.23 fail |
| follicular | 2.14 fail | 8.01 pass |
| ovulatory | 3.33 fail | 5.14 pass |
| ovulatory-accent (gold) | 1.41 fail | 12.14 pass |
| luteal | 2.39 fail | 7.17 pass |
| brand primary (`#FF6B9D`) | 2.68 fail | 6.40 pass |
| brand deep (`#C2185B`) | 5.87 pass | 3.58 fail |

This means **white-on-primary buttons fail AA** — contradicting
`design.md`'s own suggestion ("Primary buttons... FF6B9D background with
white text"). Fix: two dedicated on-fill tokens instead of reusing
`--foreground` (which itself narrowly fails against menstrual and the
derived luteal `accent-2`):

- **`--on-accent: #000000`** — pairs with brand primary and every phase
  accent (5.15–14.88 contrast, all pass with margin).
- **`--on-deep: #FFFFFF`** — the one exception; `deep` is dark enough to need
  light text (5.87, pass).

**Raw phase accents used directly as *text* color on `--background`** — this
is the case that matters for the existing app: `login`/`signup` already
render `text-phase-menstrual` for form-validation error text. All four raw
accents fail here too (1.35–3.86 contrast against `#FFF8F8`). Fix: the
`--phase-X-text` tier above, each darkened until it clears AA against
**both** `--background` (`#FFF8F8`) and pure white with margin:

| Token | Value | vs background | vs white |
|---|---|---|---|
| menstrual-text | `#DB1C58` | 4.65 | 4.86 |
| follicular-text | `#E10044` | 4.69 | 4.90 |
| ovulatory-text | `#E1004C` | 4.66 | 4.88 |
| ovulatory-accent-text | `#8F6D00` | 4.62 | 4.82 |
| luteal-text | `#AB46BC` | 4.61 | 4.85 |

Because `--phase-menstrual` changed from the initial scaffold's placeholder
(`#D6336C`, which passed at 4.62) to the real sourced value (`#E63970`,
which fails at 4.05), `login`/`signup`'s existing `text-phase-menstrual`
error text is technically still under-contrast today — it references
`--phase-menstrual` directly rather than `--phase-menstrual-text`. Since
converting those pages is explicitly out of scope for this pass, this is a
known follow-up: point that one class at `text-phase-menstrual-text` instead
when `login`/`signup` are touched next.

## What wasn't touched

- The `pink-50`...`pink-900` scale (`--pink-*` vars) from the initial
  scaffold — `login`/`signup` already reference `bg-pink-500`,
  `focus:ring-pink-400`, etc. Left as-is so those pages don't shift
  underneath them. Migrate them to `brand.*`/`phase.*` when those pages get
  converted.
- `app/(auth)/*`, `app/(app)/*` page/layout files — no page markup changed.
