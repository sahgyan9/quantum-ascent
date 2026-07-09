# 🏔️ Quantum Ascent — Brand Guidelines

This document outlines the visual system, color theories, typography, spacing, and component specifications for the **Quantum Ascent** learning platform.

---

## 🎨 1. Color Palette

Our colors reflect the deep-space nature of quantum mechanics combined with the energetic, gamified feel of climbing a mountain summit.

### Base Colors (Theme Neutral)
* **Gold / Amber** (`#fbbf24` to `#f59e0b`)
  * *Psychological Rationale:* Represents triumph, high achievement, and completeness. Used for badges, XP indicators, and the final summit node.

### Dark Mode (Default Environment)
* **Deep Space Navy** (`--bg`: `#070a13` / `#0b1020`)
  * *Psychological Rationale:* Deep, immersive slate blue that reduces eye strain for long learning sessions and establishes a serious, high-tech context.
* **Glassmorphic Indigo** (`--panel`: `#131a30`)
  * *Psychological Rationale:* A slightly lighter blue-violet that adds a layer of depth and structure when placed over the deep-space background.
* **Border Line** (`--line`: `#26304f`)
  * *Psychological Rationale:* Low-contrast slate blue that gives sharp structure to panels without drawing focus away from key actions.
* **Vibrant Violet** (`--violet`: `#8b5cf6`)
  * *Psychological Rationale:* Combines blue stability and red energy. Evokes mystery, high intellect, and the complexity of quantum entanglement.
* **Neon Cyan** (`--cyan`: `#22d3ee`)
  * *Psychological Rationale:* Fresh, energetic, and digital. Associated with lasers, state vectors, and forward-looking technologies.
* **Mint Green** (`--green`: `#34d399`)
  * *Psychological Rationale:* Associated with success, correct answers, and verification. Used for successful checks and green success buttons.

### Light Mode (High Contrast Toggle)
* **Ice Blue** (`--bg`: `#f6f8ff`)
  * *Psychological Rationale:* Clean, crisp, high-contrast background that feels modern and lightweight.
* **Chamber White** (`--panel`: `#ffffff`)
  * *Psychological Rationale:* Pure white panels that float over the ice blue base.
* **Slate Line** (`--line`: `#d8def0`)
  * *Psychological Rationale:* Soft gray border that keeps layout elements well-aligned.
* **Royal Violet** (`--violet`: `#7c3aed`)
  * *Psychological Rationale:* Darker, high-contrast violet that reads cleanly against light backgrounds.
* **Deep Cyan** (`--cyan`: `#0891b2`)
  * *Psychological Rationale:* High-contrast turquoise cyan that commands action.
* **Forest Green** (`--green`: `#059669`)
  * *Psychological Rationale:* Strong, readable green for success states.

---

## ✍️ 2. Typography

We use a modern, geometric type scale that feels clean, digital, and premium.

* **Headings:** `Space Grotesk` or `Outfit`
  * *Characteristics:* Sans-serif, geometric, futuristic, slightly wide curves.
  * *Weight:* SemiBold (600) or Bold (700).
* **Body / Interface:** `Inter` or `Plus Jakarta Sans`
  * *Characteristics:* Highly readable at small sizes, neutral, elegant spacing.
  * *Weight:* Regular (400) or Medium (500).
* **Code / Math:** `Fira Code` or `JetBrains Mono`
  * *Characteristics:* Monospace with clear coding ligatures for displaying state amplitudes and notebooks.
  * *Weight:* Regular (400).

---

## 📏 3. Spacing System

We adhere strictly to an **8px grid** to guarantee visual alignment and layout balance:

| Token | Size | Application |
| :--- | :--- | :--- |
| `xs` | 4px | Small badge padding, minor text gaps |
| `sm` | 8px | Button padding (vertical), card gaps |
| `md` | 16px | Standard button padding (horizontal), list item spacing |
| `lg` | 24px | Card padding, standard container gaps |
| `xl` | 32px | Section gaps, hero text margins |
| `xxl`| 48px | Hero vertical spacing, footer margins |

---

## 🕹️ 4. Component Personality

To make the site feel alive and Gen Z-friendly, all components must use micro-animations and custom styling:

### Card & Panels
* **Style:** Glassmorphic borders (`border: 1px solid var(--line)`).
* **Radius:** `border-radius: 16px`.
* **Glow:** Subtle dropshadows using HSL values based on their active states (cyan or violet glows).

### Interactive Buttons
* **Base Hover:** Brightness increase (`filter: brightness(1.12)`).
* **Active Press:** Scale down (`transform: scale(0.97)`), transition speed of `0.08s`.
* **Transitions:** All state changes should transition smoothly over `0.2s ease`.

### Ascent Nodes (Basecamps)
* **Inactive:** Dark border, muted gray text.
* **Available:** Glowing Violet outline (`filter: drop-shadow(0 0 6px var(--violet))`).
* **Completed:** Neon Cyan core, glowing outer halo (`filter: drop-shadow(0 0 8px var(--cyan))`), display checkmark.
