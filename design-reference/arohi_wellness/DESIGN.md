---
name: Arohi Wellness
colors:
  surface: '#fff8f8'
  surface-dim: '#ecd4da'
  surface-bright: '#fff8f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff0f3'
  surface-container: '#ffe8ee'
  surface-container-high: '#fbe2e8'
  surface-container-highest: '#f5dce3'
  on-surface: '#25181c'
  on-surface-variant: '#574146'
  inverse-surface: '#3b2c31'
  inverse-on-surface: '#ffecf0'
  outline: '#8a7176'
  outline-variant: '#ddbfc5'
  surface-tint: '#ac2a5d'
  primary: '#ac2a5d'
  on-primary: '#ffffff'
  primary-container: '#ff6b9d'
  on-primary-container: '#6e0035'
  inverse-primary: '#ffb1c5'
  secondary: '#6d5960'
  on-secondary: '#ffffff'
  secondary-container: '#f3d9e1'
  on-secondary-container: '#715d64'
  tertiary: '#b90c55'
  on-tertiary: '#ffffff'
  tertiary-container: '#ff6c95'
  on-tertiary-container: '#6f002f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9e1'
  primary-fixed-dim: '#ffb1c5'
  on-primary-fixed: '#3f001b'
  on-primary-fixed-variant: '#8c0a46'
  secondary-fixed: '#f6dce4'
  secondary-fixed-dim: '#d9c0c8'
  on-secondary-fixed: '#26171d'
  on-secondary-fixed-variant: '#544248'
  tertiary-fixed: '#ffd9df'
  tertiary-fixed-dim: '#ffb1c2'
  on-tertiary-fixed: '#3f0018'
  on-tertiary-fixed-variant: '#8f003f'
  background: '#fff8f8'
  on-background: '#25181c'
  surface-variant: '#f5dce3'
  phase-menstrual: '#E63970'
  phase-follicular: '#FF8FB1'
  phase-ovulatory-main: '#FF4081'
  phase-ovulatory-accent: '#FFD54F'
  phase-luteal: '#CE93D8'
  surface-blush: '#FFF5F8'
  text-muted: '#8A767C'
typography:
  display-lg:
    fontFamily: Nunito Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Nunito Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-lg-mobile:
    fontFamily: Nunito Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
  title-md:
    fontFamily: Nunito Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Nunito Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Nunito Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Nunito Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  button-text:
    fontFamily: Nunito Sans
    fontSize: 16px
    fontWeight: '700'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 20px
  stack-gap: 16px
  section-margin: 32px
  touch-target-min: 48px
---

## Brand & Style

The design system is built on the principles of warmth, feminine empowerment, and inclusive care. It moves away from the sterile, clinical aesthetic of traditional medical apps toward a "wellness companion" experience. The personality is gentle and nurturing, yet modern and reliable.

The visual style is **Soft Minimalist** with a focus on tactile comfort. It utilizes generous whitespace, organic rounded shapes, and a layered "Blush" surface architecture to create a safe space for users. The presence of "Sakhi," the lotus mascot, should be integrated through friendly micro-interactions and supportive empty-state illustrations, ensuring the tone remains encouraging and low-pressure. High-contrast typography and large touch targets ensure accessibility for a diverse range of users, prioritizing ease of use during physically or emotionally taxing cycle phases.

## Colors

The color palette is anchored in a spectrum of pinks and warm neutrals designed to feel biological rather than synthetic.

- **Primary & Surfaces:** The primary pink (#FF6B9D) is used for active states and critical calls to action. The blush surface (#FFE4EC) serves as the default background for cards and secondary containers, creating a soft, non-white interface that reduces eye strain.
- **Accent Themes:** The design system employs a dynamic theme engine based on the four cycle phases. These colors should dominate the dashboard's "Cycle Wheel" and related progress indicators:
    - **Menstrual:** A deep, grounded rose.
    - **Follicular:** A light, energetic coral-pink.
    - **Ovulatory:** A vibrant pink paired with gold highlights to signify peak energy.
    - **Luteal:** A calming mauve-lavender to represent the transition toward rest.
- **Typography:** Avoid pure black. Use the deep neutral (#4A3A3F) for primary text to maintain warmth while ensuring high legibility.

## Typography

This design system uses **Nunito Sans** for all levels to leverage its rounded terminals, which mirror the app's friendly and soft brand personality.

- **Scale:** Headlines are bold and expressive to provide clear hierarchy for users who may be skimming for information. 
- **Readability:** Body text uses a generous 1.5x line height to ensure ease of reading. 
- **Visual Cues:** Use the `label-caps` style for small metadata like date headers or cycle phase labels to provide clear distinction without adding visual bulk. 
- **Iconography Pairing:** Text is often paired with emojis or custom soft-line icons; maintain a 1:1 scale ratio between text height and icon size.

## Layout & Spacing

This is a **mobile-first** design system utilizing a fluid grid with generous internal margins.

- **Grid:** A 4-column fluid grid is used for mobile, expanding to 8 columns for tablet views. 
- **Rhythm:** Spacing follows an 8px linear scale. A default container padding of 20px ensures that content never feels cramped against the screen edges.
- **Comfort:** Vertical spacing between cards is set at 16px to allow the soft shadows room to breathe. 
- **Interactivity:** Every interactive element (pills, buttons, list items) must adhere to a minimum 48px touch target height to ensure accessibility for all users, including those with limited dexterity.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Soft Shadows** rather than harsh lines.

- **The Base:** The primary app background is a very pale version of the blush surface.
- **The Surface:** Cards and containers use the secondary blush color (#FFE4EC) or pure white to "pop" from the background.
- **The Shadow:** Use highly diffused shadows with a slight pink tint (e.g., `rgba(255, 107, 157, 0.08)`) and a large blur radius (12px to 20px). This "ambient glow" effect makes elements feel as though they are resting softly on a cushion rather than floating in a vacuum.
- **Active State:** When pressed, elements should use a slight inner shadow or a subtle scale-down (0.98x) to provide tactile feedback.

## Shapes

The shape language is organic and inviting. 

- **Cards:** Use a standard 16px to 20px corner radius. This creates a "friendly rectangle" that feels safe and approachable.
- **Buttons & Chips:** These are strictly **pill-shaped** (fully rounded ends). This reinforces the "modern wellness" aesthetic and distinguishes interactive triggers from informational cards.
- **Icons:** Use rounded caps and joins for all custom iconography to maintain consistency with the typography and mascot design.

## Components

- **Buttons:** Primary buttons are pill-shaped, using the #FF6B9D background with white text. Secondary buttons use an outline of the primary color or a subtle blush fill.
- **Pill Chips:** Used for cycle tagging and mood logging. These should change color based on the current cycle phase theme when selected.
- **Cards:** The primary content container. Use a 20px radius and a soft blush shadow. Cards should never have borders; depth is strictly tonal.
- **Cycle Wheel:** A central dashboard component. It uses a thick, rounded stroke divided into the four phase colors. The current day is highlighted with a soft outer glow.
- **Input Fields:** Fields should be rounded (12px) with a subtle blush background. Focus states are indicated by a primary pink glow rather than a sharp border change.
- **Mascot (Sakhi) Integration:** Sakhi should appear in "Empty States" or as a small badge for "Daily Tips," always rendered in soft, vector gradients that match the current phase theme.