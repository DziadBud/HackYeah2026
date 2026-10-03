<!-- Source: Stitch project "Małopolski Hub Innowacji Społecznych" (projects/10050838774213471276). Screens: "Czat - Wersja Mobilna", "Czat - Wersja Desktopowa", logo. -->

---
name: Małopolski Ośrodek Dostępny
colors:
  surface: '#f9f9ff'
  surface-dim: '#cfdaf2'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eeff'
  surface-container-high: '#dee8ff'
  surface-container-highest: '#d8e3fb'
  on-surface: '#111c2d'
  on-surface-variant: '#44474f'
  inverse-surface: '#263143'
  inverse-on-surface: '#ecf1ff'
  outline: '#747780'
  outline-variant: '#c4c6d0'
  surface-tint: '#455e8d'
  primary: '#00183b'
  on-primary: '#ffffff'
  primary-container: '#0f2d59'
  on-primary-container: '#7c95c8'
  inverse-primary: '#adc7fc'
  secondary: '#00504a'
  on-secondary: '#ffffff'
  secondary-container: '#9bf2e8'
  on-secondary-container: '#00201d'
  tertiary: '#001d1a'
  on-tertiary: '#ffffff'
  tertiary-container: '#003430'
  on-tertiary-container: '#4ba39a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d7e2ff'
  primary-fixed-dim: '#adc7fc'
  on-primary-fixed: '#001b3f'
  on-primary-fixed-variant: '#2c4674'
  secondary-fixed: '#c8f5ef'
  secondary-fixed-dim: '#9bf2e8'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#003a35'
  tertiary-fixed: '#9bf2e8'
  tertiary-fixed-dim: '#7fd5cc'
  on-tertiary-fixed: '#00201d'
  on-tertiary-fixed-variant: '#00504a'
  background: '#f9f9ff'
  on-background: '#111c2d'
  surface-variant: '#d8e3fb'
typography:
  display:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.01em
  display-mobile:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 44px
  headline-lg-mobile:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 36px
  headline-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 34px
  headline-sm:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 30px
  body-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-lg-bold:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 28px
  body-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md-bold:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 16px
    fontWeight: '700'
    lineHeight: 24px
  label-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  caption:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  gutter-lg: 2rem
  margin: 1.5rem
  margin-sm: 1rem
  margin-lg: 3rem
  space-xs: 0.375rem
  space-sm: 0.75rem
  space-md: 1.25rem
  space-lg: 2rem
  space-xl: 3rem
---

## Brand & Style

This design system establishes a dignified, welcoming, and deeply accessible digital presence for a regional social policy institution. The interface balances public-sector authority with human warmth, communicating stability, civic transparency, and social care.

The visual style is **Corporate Modern with High-Legibility Functionalism**:
- Pure, purposeful surfaces avoid superficial visual noise, complex skeuomorphic effects, and low-contrast translucent overlays.
- High visual legibility takes precedence over ornamental trends: generous touch targets, clear spatial groupings, and prominent structural anchors reassure citizens, NGO leaders, social workers, and civil servants alike.
- The visual tone balances administrative gravitas with human-centered empathy, delivering clarity across various age brackets and digital literacy levels.

## Colors

The palette is engineered to meet strict WCAG 2.1 AA and AAA standards across all primary, secondary, and informative states:

- **Primary (`#0F2D59`)**: Institutional deep navy commanding authority and calm security. Applied to navigation headers, dominant buttons, and primary structural dividing lines. Contrast ratio against light canvas exceeds 11:1.
- **Secondary (`#00504A`)**: Deep teal from the tertiary family (no red in the UI: it read as too loud next to the navy). Reserved for high-priority calls to action, badge highlights, and essential interactive tags. White text on it is 9.3:1; hover `#003A35`.
- **Tertiary (`#0D766E`)**: Deep spruce teal, used for social impact markers, completed milestones, support initiative flags, and environmental tags.
- **Neutral (`#1E293B` on `#F8FAFC`)**: Slate black on an off-white warm neutral backdrop, providing crisp, glare-free readability without harsh starkness.
- **Border Neutral (`#CBD5E1`)**: Clear structural separation for cards and inputs to define boundaries without visual clutter.
- **Focus Indicator (`#F59E0B` / `#0F2D59`)**: Dual-ring focus token (3px outer amber `#F59E0B` against 2px inner navy `#0F2D59`) ensures absolute visual clarity on both light and dark backgrounds.
- **Accessibility High-Contrast Mode**: Built-in support transforms backgrounds to `#000000` with high-luminance yellow `#FFEB3B` and white `#FFFFFF` for users requiring maximum optical distinction.

## Typography

The design system utilizes **Atkinson Hyperlegible Next** across all text hierarchies. Its purpose-driven letterforms disambiguate traditionally similar characters (such as uppercase `I`, lowercase `l`, and digit `1`), providing clarity for readers with low vision, dyslexia, or cognitive fatigue. Full native coverage for Polish diacritic marks (`ą`, `ć`, `ę`, `ł`, `ń`, `ó`, `ś`, `ź`, `ż`) preserves vertical metrics without clipping.

### Accessibility Sizing & Scaling Tokens
- **Default Base Font**: 18px body size (`body-lg`) as standard for all primary reading blocks.
- **Minimum Interactive Size**: 14px is strictly preserved as the absolute floor (`caption`/`label-md`). Sub-14px typography is explicitly disallowed.
- **Dynamic Text Scaling (A / A+ / A++)**:
  - `scale-100` (Default): 18px body base
  - `scale-115` (A+): 20.7px body base
  - `scale-130` (A++): 23.4px body base
- **Paragraph Spacing**: Set to `1.5` minimum line-height, with a paragraph separation gap of `1.25em` to prevent dense cognitive wall-of-text fatigue.

## Layout & Spacing

A structured 12-column responsive fluid grid aligns institutional content predictably:

- **Desktop (>= 1280px)**: 12 columns, max content container width `1280px`, `gutter-lg` (32px), `margin-lg` (48px).
- **Tablet (768px - 1279px)**: 8 columns, fluid width, `gutter` (24px), `margin` (24px).
- **Mobile (< 768px)**: 4 columns, fluid width, `gutter-sm` (16px), `margin-sm` (16px).

### Spacing Philosophy
Spacing tokens are strictly applied as empty distances between discrete containers and inside structural cards:
- Vertical rhythm follows an explicit 8px base grid, stepped through `space-xs` (6px) through `space-xl` (48px).
- Complex application forms and multi-tier institutional overviews maintain `space-lg` separation to avoid visual collision and cognitive overwhelm.
- Interactive touch targets adhere to a minimum physical bounding box of `48px x 48px` regardless of the optical icon or text footprint inside.

## Elevation & Depth

Visual hierarchy is communicated via clean tonal layers and crisp low-contrast outlines rather than deep or distracting drop shadows:

- **Level 0 (Base Canvas)**: Solid `#F8FAFC`. All primary navigation, layout wrappers, and background elements sit here.
- **Level 1 (Surface Cards & Panels)**: Solid `#FFFFFF` enclosed by a 1px solid border of `#CBD5E1`. A soft ambient underlay (`0 2px 4px rgba(15, 45, 89, 0.04)`) separates interactive modules from the backdrop.
- **Level 2 (Dropdowns, Floating Toolbars, Modals)**: Solid `#FFFFFF` enclosed by a 1.5px border of `#94A3B8` accompanied by an ambient resting shadow (`0 8px 24px rgba(15, 45, 89, 0.08)`).
- **Focus State (Interactive Depth)**: Focus does not rely on elevation or z-index changes. Instead, active items produce a 3px outer outline in `#F59E0B` separated by a 2px offset in `#FFFFFF`.

## Shapes

The design system implements a consistent **Level 2 (Rounded)** shape language:
- Standard UI containers, cards, dialog boxes, and interactive text inputs employ an outer corner radius of `12px` (`0.75rem`).
- Secondary utility badges, small tags, and status chips apply a soft radius of `6px` (`0.375rem`).
- Full circle shapes (`border-radius: 9999px`) are restricted solely to user avatars, quick action accessibility buttons, and binary step indicator numbers.
- Avoid razor-sharp 0px borders to reduce harsh visual tension, while avoiding exaggerated pill containers to maintain civic credibility.

## Components

### Accessibility Toolbar (Sticky Top Bar)
- Positioned persistently at the topmost viewport edge across all pages.
- Houses dedicated controls for:
  - Text Size Adjustment (`A-`, `Standard`, `A+`, `A++`)
  - Contrast Toggles (Standard Light, High-Contrast Black/Yellow)
  - Screen Reader Direct Jump links (`Przejdź do treści głównej`, `Dla osób z niepełnosprawnościami` → accessibility statement). Compact site footer repeats `Deklaracja dostępności`.
- Renders in high-contrast navy `#0F2D59` with crisp white buttons and unmistakable active underline indicators.

### Buttons
- **Primary**: Solid `#0F2D59` background, white text (`#FFFFFF`), min-height 48px, minimum horizontal padding `space-md` (20px), rounded-12px. Hover state deepens to `#0A1F3D`; focus triggers the dual amber focus outline.
- **Secondary (Regional Callout)**: Solid `#C53030` background, white text (`#FFFFFF`), used exclusively for grant applications, submission deadlines, and urgent social announcements. Hover state shifts to `#9B2C2C`.
- **Tertiary / Outlined**: Transparent background, 2px solid `#0F2D59`, `#0F2D59` text weight 600.

### Input Fields & Selects
- 48px standard height, white background (`#FFFFFF`), 1.5px border `#CBD5E1`, internal horizontal padding 16px.
- Labels sit persistently above the input field in `16px` semibold navy `#0F2D59` (never rely solely on disappearing placeholder text).
- Error states enforce a 2px `#C53030` border alongside an unambiguous exclamation icon and red validation message text below.

### Cards & Content Modules
- Rendered in solid `#FFFFFF` with 1px border `#CBD5E1` and 12px corner radius.
- Padding uses `space-md` (20px) on mobile scaling to `space-lg` (32px) on desktop.
- Interactive cards provide an unmistakable 2px border color shift to `#0F2D59` on hover/focus, avoiding erratic transforms or scale animations.

### Checkboxes & Radio Buttons
- 24px x 24px minimum hit targets with a 48px touch wrapper.
- 2px solid `#0F2D59` border in unchecked state, filling with `#0F2D59` and displaying an unmistakable high-contrast white checkmark icon upon selection.
- Distinct inline descriptive text paired with explicit associated label tags.

### Status Chips & Badges
- 32px height, 6px corner radius, horizontal padding 12px.
- Color combinations strictly verified for minimum 4.5:1 contrast:
  - *Open Call / Active*: Teal background (`#E6FFFA`), `#0D766E` text.
  - *Deadline Approaching*: Amber background (`#FEF3C7`), `#92400E` text.
  - *Closed / Archived*: Slate background (`#F1F5F9`), `#334155` text.
