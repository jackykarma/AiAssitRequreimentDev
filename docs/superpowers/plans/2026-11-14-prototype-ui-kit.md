# Prototype UI Kit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a ColorOS-like shared `uk-*` CSS kit under feature prototype templates and wire product/UX HTML + skills to use it.

**Architecture:** Kit lives in `templates/feature/prototype/shared/ui-kit/` so `init_feature` copytree already distributes it. Product and UX pages link the three CSS files; showcase.html is the human visual gate.

**Tech Stack:** Plain CSS + vanilla HTML/JS (no build).

## File map

- Create: `aiassitrequreimentdev/templates/feature/prototype/shared/ui-kit/{tokens,components,phone}.css`, `showcase.html`
- Rewrite: `templates/feature/prototype/index.html`, `templates/feature/prototype/ux/index.html`
- Update: product/ux SKILL.md (plugin + sync), `artifacts.md`, modus product/ux notes

### Task 1: CSS kit + showcase

- [x] Add tokens / components / phone CSS (ColorOS-like)
- [x] Add showcase.html covering all first-wave components
- [x] Open showcase locally and sanity-check layout

### Task 2: Wire templates

- [x] Product `index.html` uses kit (patch/new)
- [x] UX `ux/index.html` uses kit (interactive multi-view)

### Task 3: Docs / skills

- [x] Skills + artifacts mention `prototype/shared/ui-kit/`
- [x] `python scripts/sync_plugin_skills.py`
