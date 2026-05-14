# Knowledge Base UI Redesign Spec

**Date**: 2026-05-14
**Status**: Approved

## Overview

Redesign the Knowledge Base web UI from a bare MVP into a polished, modern interface with sidebar navigation, magazine-grid layout, clean blue color scheme, and light/dark mode support.

## Design Decisions

| Decision | Choice |
|----------|--------|
| Style direction | Clean Blue — white-dominant with blue accents |
| Homepage layout | Magazine Grid — two-column note cards |
| Color intensity | Modern Fresh — bright blue + indigo gradient accents |
| Navigation | Sidebar — left icon nav with top search |
| Dark mode | Toggle in sidebar footer, CSS variables, respects OS preference |

## Color Palette

### Light Mode
- **Background**: `#f8fafc` (slate-50)
- **Surface/Card**: `#ffffff`
- **Sidebar**: `#f1f5f9` (slate-100)
- **Text primary**: `#0f172a` (slate-900)
- **Text secondary**: `#64748b` (slate-500)
- **Border**: `#e2e8f0` (slate-200)
- **Accent**: `#3b82f6` (blue-500)
- **Accent hover**: `#2563eb` (blue-600)
- **Accent gradient**: `linear-gradient(135deg, #3b82f6, #6366f1)`
- **Card left border**: `#3b82f6` 2px on hover/active
- **Tag bg**: `#eff6ff` (blue-50), text `#3b82f6`

### Dark Mode
- **Background**: `#0f172a` (slate-900)
- **Surface/Card**: `#1e293b` (slate-800)
- **Sidebar**: `#0f172a`
- **Text primary**: `#e2e8f0` (slate-200)
- **Text secondary**: `#94a3b8` (slate-400)
- **Border**: `#334155` (slate-700)
- **Accent**: `#3b82f6` (unchanged — stays visible on dark)
- **Tag bg**: `#1e3a5f`, text `#60a5fa` (blue-400)

## Typography

- System font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif`
- Monospace: `"SF Mono", "Fira Code", Menlo, Consolas, monospace`
- Heading scale: 28/22/18/16px
- Body: 15px, line-height 1.7
- Small/meta: 12-13px

## Layout Structure

```
┌──────────┬──────────────────────────────────────┐
│ Sidebar  │  Content Area                        │
│ 56px     │                                      │
│          │  ┌─────────────────────────────────┐  │
│  Logo    │  │  Page Title / Search            │  │
│  ──────  │  ├─────────────────────────────────┤  │
│  Home    │  │                                 │  │
│  Graph   │  │  Grid / Editor / Detail         │  │
│  Tags    │  │                                 │  │
│          │  │                                 │  │
│  ──────  │  └─────────────────────────────────┘  │
│  New     │                                      │
│  ──────  │                                      │
│  ☀/☽    │                                      │
└──────────┴──────────────────────────────────────┘
```

### Sidebar
- Width: 56px fixed
- Background: matches theme, separated by 1px border
- Items: Logo (gradient icon), Home, Graph, Tags, New Note, spacer, Theme Toggle
- Icons: inline SVG, 18-20px
- Active state: blue text, subtle left-border indicator
- Hover: color transition

### Top Bar (inside content area, not a separate nav)
- Page title on the left
- Search input on the right (280px, rounded)
- Height: 48px, margin-bottom: 24px

## Page Designs

### 1. Homepage (`/`)
- Page title: "最近笔记" (or "#tagname" when filtering)
- Tag cloud below title: pill-shaped, blue bg on active tag
- Note grid: 2 columns, 8px gap
- Each card: surface bg, 1px border, rounded 8px, padding 14px 16px
- Active/hover card: 2px left blue border, border-color accent transition
- Card content: title (14px semibold), date (12px muted), optional first-line excerpt
- Empty state: centered illustration-style message with CTA to create first note

### 2. Note Detail (`/note/<slug>`)
- Back link at top: ← 返回
- Note title: large heading (24px)
- Content area: prose-style, max-width 720px for readability
- Markdown rendered: headings, code blocks (dark bg even in light mode), blockquotes (blue left border), links (accent color), broken wiki-links (red dashed)
- Action buttons below content: Edit (primary btn), Delete (ghost danger btn)
- Backlinks section: separated by horizontal rule, "链接到这里的笔记" heading, compact list of linked notes

### 3. Note Editor (`/note/new`, `/note/<slug>/edit`)
- Full-width editor area
- Title input: large (18px), borderless-bottom style, full width
- Tag input: below title, smaller
- EasyMDE editor: full height (calc-height to fill viewport)
- Action bar: Save (primary), Cancel (ghost), sticky at bottom or top of editor
- Auto-save indicator if applicable

### 4. Search Results (`/search?q=...`)
- Page title: 搜索: "query"
- Result cards: similar to note cards but with highlighted snippet
- `<mark>` styling: yellow bg (#fef08a) in light, amber in dark
- Empty state: "没有找到匹配的结果"

### 5. Knowledge Graph (`/graph`)
- Full-height graph container (calc(100vh - 100px))
- Surface bg, rounded border
- D3.js force-directed graph (existing functionality preserved)
- Nodes: accent blue, slight glow on hover

## CSS Architecture

Single `style.css` with CSS custom properties:

```css
:root {
  /* light theme (default) */
  --bg: #f8fafc;
  --surface: #ffffff;
  --sidebar-bg: #f1f5f9;
  --text: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --accent-gradient: linear-gradient(135deg, #3b82f6, #6366f1);
  --tag-bg: #eff6ff;
  --tag-text: #3b82f6;
  --radius: 8px;
  --card-padding: 14px 16px;
}

[data-theme="dark"] {
  --bg: #0f172a;
  --surface: #1e293b;
  --sidebar-bg: #0f172a;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --border: #334155;
  --tag-bg: #1e3a5f;
  --tag-text: #60a5fa;
}
```

Theme persisted to `localStorage`, initial load checks OS preference via `prefers-color-scheme`.

## Interactions & Polish

- Sidebar icons: 150ms color transition on hover
- Note cards: 200ms border-color + left-border transition
- Theme toggle: instant (CSS variables swap, no flash)
- Smooth page transitions: not needed (MPA, server-rendered)
- Focus states: blue ring for accessibility
- Markdown code blocks: always dark background (`#1e293b`) in both themes for contrast

## Browser Support

Modern browsers (Chrome, Firefox, Safari, Edge). No IE support needed.

## Files to Modify

| File | Change |
|------|--------|
| `static/css/style.css` | Complete rewrite with new design system |
| `templates/base.html` | Sidebar layout, theme toggle script |
| `templates/index.html` | Grid layout, new card markup |
| `templates/note_detail.html` | Refined detail layout |
| `templates/note_edit.html` | Refined editor layout |
| `templates/search_results.html` | Refined search cards |
| `templates/graph.html` | Minor layout adjustments |
| `static/js/editor.js` | Minor theme-aware adjustments if needed |
| `static/js/graph.js` | Theme-aware colors for D3 |

## Out of Scope

- User authentication / accounts
- Note version history
- Image/file attachments
- Full-text search engine (current SQLite LIKE search stays)
- Mobile app or PWA
- Real-time collaboration
