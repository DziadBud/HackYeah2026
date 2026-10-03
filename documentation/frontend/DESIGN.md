---
name: Małopolska Public Trust
colors:
  surface: '#f8f9ff'
  surface-dim: '#d0dbed'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dee9fc'
  surface-container-highest: '#d9e3f6'
  on-surface: '#121c2a'
  on-surface-variant: '#434750'
  inverse-surface: '#27313f'
  inverse-on-surface: '#eaf1ff'
  outline: '#737781'
  outline-variant: '#c3c6d1'
  surface-tint: '#375f99'
  primary: '#002752'
  on-primary: '#ffffff'
  primary-container: '#0b3d75'
  on-primary-container: '#84a9e8'
  inverse-primary: '#a8c8ff'
  secondary: '#bb0021'
  on-secondary: '#ffffff'
  secondary-container: '#e22334'
  on-secondary-container: '#fffbff'
  tertiary: '#00294a'
  on-tertiary: '#ffffff'
  tertiary-container: '#003f6e'
  on-tertiary-container: '#6cacf3'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#a8c8ff'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#1b477f'
  secondary-fixed: '#ffdad7'
  secondary-fixed-dim: '#ffb3af'
  on-secondary-fixed: '#410005'
  on-secondary-fixed-variant: '#930017'
  tertiary-fixed: '#d1e4ff'
  tertiary-fixed-dim: '#9fcaff'
  on-tertiary-fixed: '#001d36'
  on-tertiary-fixed-variant: '#00497d'
  background: '#f8f9ff'
  on-background: '#121c2a'
  surface-variant: '#d9e3f6'
  surface-page: '#f8f9fa'
  surface-card: '#ffffff'
  border-subtle: '#e2e8f0'
  border-strong: '#cbd5e1'
  text-muted: '#4b5563'
  high-contrast-bg: '#000000'
  high-contrast-text: '#ffff00'
  tag-blue-bg: '#ebf3fa'
  tag-blue-text: '#0b3d75'
  tag-red-bg: '#fdf2f2'
  tag-red-text: '#c91e2b'
typography:
  headline-xl:
    fontFamily: Public Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Public Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-lg:
    fontFamily: Public Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Public Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 30px
  headline-md:
    fontFamily: Public Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
  headline-sm:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  caption:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes an authoritative, highly accessible, and citizen-centered visual language for regional social policy administration. The visual tone balances administrative legitimacy with public warmth, dignity, and transparency. Designed to serve diverse civic demographics—including persons with disabilities, social welfare professionals, senior citizens, and civic leaders—it prioritizes clarity, intuitive navigation, and effortless readability.

The visual style is **Corporate / Modern** inflected with accessible civic UI conventions:
- High contrast, crisp typographic structures with strict adherence to WCAG 2.1 AA/AAA criteria.
- Dedicated accessibility header bar for text size scaling and contrast toggling.
- Crisp white structural surfaces framed by subtle neutral outlines, supported by Małopolska regional accents (carmine red) and foundational royal/navy blue tones.
- Balanced container cards with soft radii, avoiding overly sterile bureaucratic stiffness while maintaining formal institutional rigor.

## Colors

The color palette anchors on official institutional trust, public clarity, and regional identity:

- **Primary (`#0b3d75`):** Deep Royal/Navy Blue. Anchors the institutional presence across main navigation, headers, critical action buttons, and dominant iconography.
- **Secondary (`#d1122a`):** Małopolska Regional Red. Reserved for regional signifiers, date stamps, urgency markers, active status pills, and high-visibility editorial accents.
- **Tertiary (`#0b62a4`):** Vibrant Civic Blue. Serves as active link states, focused list selections, and subtle hover interactions.
- **Neutral (`#1f2937` & `#4b5563`):** Slate dark grays ensuring high contrast for continuous body text and supplementary captions, preventing the visual fatigue of absolute black against stark white.
- **Surface & Backgrounds:** The base canvas uses `#f8f9fa` to provide subtle visual relief against pure `#ffffff` cards and content containers, outlined neatly by `#e2e8f0`.

Specialized high-contrast modes invert to pure black (`#000000`) and cadmium yellow (`#ffff00`) in compliance with standard Polish public sector Biuletyn Informacji Publicznej (BIP) accessibility guidelines.

## Typography

The design system employs **Public Sans** across all typographic hierarchies. Modeled after open-source civic standards, its geometric stability, generous x-height, and open counters provide extreme legibility on low-resolution displays and across various assistive technologies.

- **Headlines (`headline-xl`, `headline-lg`, `headline-md`):** Solid, bold weights convey official authority without aggressive styling. Line heights are spaced generously to ensure that multiline headlines remain comfortably legible.
- **Body Text (`body-lg`, `body-md`):** Set at a standard minimum of 16px for desktop content bodies to facilitate fatigue-free reading for public tenders, training notices, and policy documentation.
- **Labels and Metadata (`label-md`, `label-sm`):** Slightly elevated font weights (`600`) paired with subtle positive letter spacing are used on publication tags, date stamps, and navigation items to distinguish them from editorial prose.

## Layout & Spacing

The layout is built upon a standard 12-column responsive fluid grid bounded by a central max-width of `1280px` for desktop viewports, ensuring content does not stretch across ultra-wide monitors.

- **Desktop (1024px+):** 12 columns with `1.5rem` (24px) gutters and `2rem` (32px) margins. Asymmetrical two-column templates are common: a 4-column side navigation / calendar rail alongside an 8-column main content stream.
- **Tablet (768px – 1023px):** 8 columns with `1.25rem` (20px) gutters. Side navigation drops to a collapsible drawer or stacks above primary feeds.
- **Mobile (< 768px):** 4 columns with `1rem` (16px) gutters and `1rem` (16px) outer page margins. News cards and publication covers shift into vertical single-column stacks.

Vertical rhythm is governed by multiples of 8px (`0.5rem`, `1rem`, `1.5rem`, `2.5rem`), maintaining clear visual separation between administrative modules and publication listings.

## Elevation & Depth

Visual depth is communicated primarily through **clean tonal layering paired with low-contrast structural borders**, avoiding heavy, distracting skeuomorphic shadows to optimize accessibility:

- **Flat/Resting Surfaces:** Information cards, event items, and navigation sections rest on a `#ffffff` background bounded by a `1px` border in `#e2e8f0`.
- **Card Hover / Interaction:** Elevation on cards is indicated subtly via a slight shift to `0 4px 12px rgba(11, 61, 117, 0.08)` and border intensification to `#cbd5e1`.
- **Modals & Drawers:** High-priority overlays (e.g., search modals, mobile navigation menus) use an ambient, soft shadow: `0 12px 32px rgba(15, 23, 42, 0.15)`.
- **Focus States:** Depth and focus are elevated via a mandatory 3px high-contrast outline (`#0b62a4` or `#ffff00` in contrast mode) with a 2px white offset gap, satisfying WCAG 2.4.7 focus criteria.

## Shapes

The system implements a structured **Rounded (`2`)** shape philosophy:

- **Buttons & Form Fields:** Standard base radius of `0.5rem` (8px), offering a welcoming, contemporary feel without appearing whimsical.
- **Cards & Modules (`rounded-lg` / `rounded-xl`):** Primary news cards, project highlights, and calendar blocks utilize `1rem` (16px) or `1.5rem` (24px) corner radii.
- **Pills & Status Tags:** Fully rounded pill silhouettes (`9999px`) are designated for date chips, category tags, and accessibility switchers.
- **Thumbnails & Media Containers:** Media previews feature `0.75rem` (12px) clipping to integrate naturally with surrounding card containers.

## Components

### Accessibility Bar & Public Header
- Positioned at the very top of the layout on `#ffffff` with a subtle bottom divider.
- Houses the Biuletyn Informacji Publicznej (BIP) emblem, language switcher, high-contrast toggle (`A`), and three progressive text-scaling buttons (`A-`, `A`, `A+`).
- Next to it sits the official regional coat-of-arms (Małopolska) and institutional identity.

### Buttons
- **Primary:** Solid `#0b3d75` fill, `#ffffff` text, `0.5rem` border-radius, `0.75rem 1.5rem` padding. On hover: shifts to `#0b62a4`.
- **Secondary / Action:** Outlined in `#0b3d75` (1.5px solid) with white fill and blue text.
- **Regional / Urgent:** Solid `#d1122a` fill, white text, reserved for critical calls for applications or deadlines.
- **Interactive Links ("Więcej >"):** Inline flex row with a chevron icon, typed in `label-md`, hovering with an arrow translation of +4px.

### Badges & Pill Tags
- **Date Stamps:** `#fdf2f2` background with `#c91e2b` text, bold `label-sm` font, pill-rounded.
- **Category / Division Tags:** `#ebf3fa` background with `#0b3d75` text, cleanly delineating topics such as "Adopcja", "Ekonomia Społeczna", or "Szkolenia".

### Cards & Content Feeds
- **News Item Card:** White background, `1px solid #e2e8f0`, `1rem` border radius, containing an optional 16:9 thumbnail, a red or blue date pill, an emphatic `headline-sm` title, and an excerpt capped at 3 lines.
- **Side Rail Navigation:** Dark royal blue container (`#0b3d75`) with white text links separated by low-opacity dividers (`rgba(255, 255, 255, 0.15)`), active item highlighted with a left white bar.

### Form Inputs & Checkboxes
- **Text Inputs:** White background, `1px solid #cbd5e1`, `0.5rem` radius, padding `0.75rem 1rem`. Focus state triggers a crisp 3px ring in `#0b62a4`.
- **Checkboxes & Radios:** 20px by 20px boxes, primary blue checked state with high-contrast white tick marks, fully navigable via keyboard Tab/Space controls.

### Breadcrumbs
- Placed directly beneath header titles, set in `body-sm` (`#4b5563`), with `/` or `>` dividers, terminating in a bolded current page label in `#1f2937`.