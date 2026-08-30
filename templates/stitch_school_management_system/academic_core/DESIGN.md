---
name: Academic Core
colors:
  surface: '#fbf8fa'
  surface-dim: '#dcd9db'
  surface-bright: '#fbf8fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f4'
  surface-container: '#f0edef'
  surface-container-high: '#eae7e9'
  surface-container-highest: '#e4e2e3'
  on-surface: '#1b1b1d'
  on-surface-variant: '#45474c'
  inverse-surface: '#303032'
  inverse-on-surface: '#f3f0f2'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#545f73'
  primary: '#091426'
  on-primary: '#ffffff'
  primary-container: '#1e293b'
  on-primary-container: '#8590a6'
  inverse-primary: '#bcc7de'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#1e1200'
  on-tertiary: '#ffffff'
  tertiary-container: '#35260c'
  on-tertiary-container: '#a38c6a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e3fb'
  primary-fixed-dim: '#bcc7de'
  on-primary-fixed: '#111c2d'
  on-primary-fixed-variant: '#3c475a'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#fadfb8'
  tertiary-fixed-dim: '#ddc39d'
  on-tertiary-fixed: '#271902'
  on-tertiary-fixed-variant: '#564427'
  background: '#fbf8fa'
  on-background: '#1b1b1d'
  surface-variant: '#e4e2e3'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 24px
  margin: 24px
  sidebar-width: 280px
---

## Brand & Style

This design system is built for a School Management System, focusing on **authority, clarity, and efficiency**. The target audience includes administrators, teachers, and parents who require a reliable tool to manage complex data. 

The design style is **Modern Corporate Minimalism**. It prioritizes a high-contrast interface for accessibility and a "data-first" philosophy. By utilizing a restrained color palette and generous whitespace, the system reduces cognitive load, allowing users to focus on critical academic tasks. The aesthetic is professional and stable, evoking the feeling of a prestigious educational institution while remaining technologically advanced.

## Colors

The palette is anchored by **Deep Navy (#1e293b)**, used for structural elements like sidebars and primary headings to establish authority. **Royal Blue (#2563eb)** serves as the functional driver for interactive elements, links, and primary actions.

- **Primary:** Deep Navy for institutional stability.
- **Action:** Royal Blue for interactivity.
- **Feedback:** Emerald Green for success states (grades, attendance) and Rose Red for errors/warnings.
- **Surface:** The background uses a very light slate (#f8fafc) to provide a clean canvas that minimizes eye strain during long working hours.

## Typography

The typography system relies exclusively on **Inter**, a typeface designed for screen readability. It utilizes a systematic scale to differentiate between administrative data and navigational cues.

Headlines use a bold weight and tight letter-spacing to appear grounded and confident. Body text maintains a generous line height (1.5x) to ensure legibility when reading student records or reports. Labels are occasionally set in uppercase with slight tracking to provide clear section headers within dense forms.

## Layout & Spacing

The layout utilizes a **Fixed-Fluid hybrid grid**. The main navigation is a fixed-width sidebar (280px), while the content area is a fluid 12-column grid that expands to fill the remaining viewport.

- **Grid:** 12 columns on desktop, 6 on tablet, 1 on mobile.
- **Rhythm:** A 4px baseline shift is used. Most components use 16px (md) or 24px (lg) padding to maintain an airy, professional feel.
- **Margins:** Consistent 24px outer margins ensure content never touches the screen edges, maintaining a "contained" and organized appearance.

## Elevation & Depth

Depth is used sparingly to signify "interactive layers" over "static data."

- **Level 0 (Surface):** The main background (#f8fafc), flat.
- **Level 1 (Cards):** White background (#ffffff) with a 1px border (#e2e8f0) and a subtle 4px blur ambient shadow. Used for student files, grade summaries, and dashboard widgets.
- **Level 2 (Overlays):** Modals and dropdowns. These use a more pronounced 12px blur shadow with 5% opacity to separate them from the primary workspace.
- **Focus States:** Elements like input fields do not use shadows for depth; instead, they use a 2px Royal Blue outer glow to signify active focus without shifting the layout.

## Shapes

The design system employs a **Rounded (8px-12px)** shape language. This softens the "institutional" feel of the deep navy colors, making the software feel modern and approachable for daily use.

- **Standard (8px):** Buttons, input fields, and small UI components.
- **Large (16px):** Main dashboard cards and container modules.
- **Full (Pill):** Used strictly for status badges (e.g., "Present", "Late", "Paid").

## Components

### Buttons
Primary buttons are solid Royal Blue with white text. Secondary buttons are outlined in Slate-300 with Deep Navy text. All buttons have a height of 40px (standard) or 48px (large/CTA) and an 8px corner radius.

### Input Fields
Inputs use a white background with a 1px border (#cbd5e1). On focus, the border transitions to Royal Blue with a subtle halo. Labels are always positioned above the field in a bold, 14px font.

### Cards
Cards are the primary container for the system. They must include a 16px padding and a subtle header separator line when displaying data tables or student metrics.

### Navigation Sidebar
The sidebar uses the Primary Deep Navy color. Nav items are high-contrast white (active) or semi-transparent slate (inactive). Active items are indicated by a 4px Royal Blue vertical bar on the left edge.

### Status Chips
Small, pill-shaped indicators. Use light background tints of the Success/Error/Warning colors with dark text of the same hue for maximum readability (e.g., Light Green background with Dark Green text).