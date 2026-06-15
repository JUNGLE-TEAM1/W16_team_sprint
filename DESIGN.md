---
version: alpha
name: Neo Mirai DevBoard
description: Retro-futuristic Japanese knowledge board with warm paper, amber sun motifs, black architectural linework, and premium editorial density.
colors:
  background: "#140F0A"
  paper: "#F3E4C6"
  paperDeep: "#E2C083"
  ink: "#15100B"
  inkMuted: "#57432E"
  amber: "#D9821F"
  burntOrange: "#A94617"
  gold: "#C99B42"
  border: "#2B2117"
  danger: "#B42318"
  success: "#176C4A"
typography:
  display:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "clamp(42px, 7vw, 104px)"
    fontWeight: 900
    lineHeight: 0.9
  title:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "32px"
    fontWeight: 800
    lineHeight: 1.05
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 500
    lineHeight: 1.55
  monoLabel:
    fontFamily: "'IBM Plex Mono', 'SFMono-Regular', Consolas, monospace"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
rounded:
  sm: "0px"
  md: "2px"
  lg: "4px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  panel:
    backgroundColor: "{colors.paper}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  primaryButton:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    borderColor: "{colors.gold}"
---

## Overview

DevBoard should feel like a retro-futuristic Japanese AI conference poster adapted into a working knowledge tool. It keeps the actual CRUD/RAG workflow, but the visual language is editorial: warm ivory paper, black ink dividers, amber sun disks, burnt-orange accents, thin architectural lines, and deliberate high-contrast type.

## Colors

Use warm paper as the main reading surface and black/near-black as the structural frame. Amber and burnt orange are accents for RAG, active states, and visual motifs. Avoid blue/purple AI gradients entirely.

## Typography

Display titles use a serif editorial voice. UI controls and dense metadata use sans or mono labels. Do not use oversized SaaS dashboard headings inside controls; reserve the largest type for the first viewport/hero.

## Layout

The page should read as a poster-inspired product surface: sticky black nav, full-width hero/work command panel, horizontal tag strip, editorial post cards, and a right-side writing/RAG module. Use thin black rules and geometric separators instead of soft card piles.

## Elevation & Depth

Prefer flat print-like depth: hard shadows, ink borders, paper texture, grid lines, and overlapping circular motifs. Avoid glassmorphism and gray floating-card stacks.

## Shapes

Use circles for sun motifs, thin straight architectural lines, rectangular panels with minimal radius, and stamp-like pills. Buttons should feel deliberate and compact, not rounded SaaS pills.

## Components

Inputs live on paper panels with black borders. Primary actions are ink-filled with amber text or paper text. RAG result panels use amber backgrounds and black rule dividers. Cards should feel like editorial program cards, not generic dashboard cards.

## Do's and Don'ts

Do use: ivory paper grain, amber/burnt orange, black ink, Japanese microcopy, big editorial title, hard dividers, circular sun marks.

Do not use: purple/blue gradients, generic SaaS cards, glass blur, emoji, fake dashboard screenshots, gray-on-white blandness, default Inter-only look.
