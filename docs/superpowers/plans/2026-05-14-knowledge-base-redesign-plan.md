# Knowledge Base UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the KB app with sidebar navigation, magazine-grid layout, clean blue theme, and light/dark mode toggle.

**Architecture:** Single CSS file with custom properties for theming, sidebar layout in base.html, grid layout on homepage. No backend changes — purely CSS + template + minor JS. Theme persisted to localStorage, with OS preference as initial default.

**Tech Stack:** FastAPI, Jinja2 templates, vanilla CSS custom properties, EasyMDE, D3.js v7

---

### Task 1: Rewrite CSS with full design system

**Files:**
- Modify: `static/css/style.css`

- [ ] **Step 1: Write the new CSS**

Replace the entire content of `static/css/style.css`:

```css
/* ===== Design tokens ===== */
:root {
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
  --code-bg: #1e293b;
  --code-text: #e2e8f0;
  --danger: #ef4444;
  --danger-hover: #dc2626;
  --radius: 8px;
  --radius-sm: 6px;
  --sidebar-width: 56px;
  --transition: 150ms ease;
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

/* ===== Reset ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  font-size: 15px;
  display: flex;
  min-height: 100vh;
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }

/* ===== Sidebar ===== */
.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
}

.sidebar-logo {
  width: 28px;
  height: 28px;
  background: var(--accent-gradient);
  border-radius: 6px;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.sidebar-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  transition: color var(--transition), background var(--transition);
  position: relative;
  text-decoration: none;
}

.sidebar-btn:hover { color: var(--text); background: var(--border); }
.sidebar-btn.active { color: var(--accent); }

.sidebar-btn svg { width: 20px; height: 20px; }

.sidebar-spacer { flex: 1; }

.sidebar-new {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--transition), transform var(--transition);
  flex-shrink: 0;
  margin: 8px 0;
}

.sidebar-new:hover { background: var(--accent-hover); color: #fff; transform: scale(1.08); }
.sidebar-new svg { width: 18px; height: 18px; }

.theme-toggle {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition), background var(--transition);
  flex-shrink: 0;
}

.theme-toggle:hover { color: var(--text); background: var(--border); }
.theme-toggle svg { width: 18px; height: 18px; }
.theme-toggle .icon-moon { display: none; }
.theme-toggle .icon-sun { display: block; }
[data-theme="dark"] .theme-toggle .icon-moon { display: block; }
[data-theme="dark"] .theme-toggle .icon-sun { display: none; }

/* ===== Main content ===== */
.main {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: 32px 40px;
  max-width: calc(960px + var(--sidebar-width));
  width: 100%;
}

/* ===== Top bar (inside content) ===== */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.topbar h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
}

.topbar-search {
  position: relative;
}

.topbar-search input {
  width: 260px;
  padding: 8px 14px 8px 34px;
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 14px;
  background: var(--surface);
  color: var(--text);
  transition: border-color var(--transition), box-shadow var(--transition);
  outline: none;
}

.topbar-search input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.topbar-search svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  pointer-events: none;
}

/* ===== Tag cloud ===== */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.tag {
  padding: 4px 14px;
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 20px;
  font-size: 13px;
  text-decoration: none;
  font-weight: 500;
  transition: background var(--transition), color var(--transition);
}

.tag:hover { background: var(--accent); color: #fff; }

/* ===== Note grid (magazine) ===== */
.note-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.note-card {
  display: block;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 2px solid transparent;
  border-radius: var(--radius);
  padding: 14px 16px;
  color: var(--text);
  text-decoration: none;
  transition: border-color 200ms ease, border-left-color 200ms ease;
}

.note-card:hover {
  border-color: var(--accent);
  border-left-color: var(--accent);
}

.note-card h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text);
}

.note-card .meta {
  font-size: 12px;
  color: var(--text-muted);
}

/* ===== Note detail ===== */
.note-detail { max-width: 720px; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
  transition: color var(--transition);
}

.back-link:hover { color: var(--text); }
.back-link svg { width: 16px; height: 16px; }

.note-title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--text);
}

/* Prose content */
.prose {
  line-height: 1.8;
  color: var(--text);
}

.prose h1, .prose h2, .prose h3 {
  margin: 28px 0 12px;
  color: var(--text);
}

.prose h1:first-child { margin-top: 0; }
.prose h1 { font-size: 22px; }
.prose h2 { font-size: 18px; }
.prose h3 { font-size: 16px; }

.prose p { margin-bottom: 14px; }

.prose a { color: var(--accent); }
.prose a:hover { text-decoration: underline; }

.prose .broken-link {
  color: var(--danger);
  border-bottom: 1px dashed var(--danger);
  cursor: pointer;
}

.prose pre {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 16px 20px;
  border-radius: var(--radius);
  overflow-x: auto;
  margin: 16px 0;
}

.prose code {
  font-family: "SF Mono", "Fira Code", Menlo, Consolas, monospace;
  font-size: 13px;
}

.prose :not(pre) > code {
  background: var(--border);
  color: var(--text);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 85%;
}

.prose blockquote {
  border-left: 3px solid var(--accent);
  padding-left: 16px;
  color: var(--text-muted);
  margin: 16px 0;
}

.prose ul, .prose ol { margin: 12px 0; padding-left: 24px; }
.prose li { margin-bottom: 4px; }
.prose img { max-width: 100%; border-radius: var(--radius-sm); }

/* ===== Action buttons ===== */
.actions {
  display: flex;
  gap: 8px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: background var(--transition);
  font-family: inherit;
}

.btn:hover { background: var(--accent-hover); color: #fff; }

.btn-ghost {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-ghost:hover { background: var(--border); }

.btn-danger {
  background: transparent;
  color: var(--danger);
  border: 1px solid var(--border);
}

.btn-danger:hover { background: #fef2f2; }

[data-theme="dark"] .btn-danger:hover { background: #3b1111; }

/* ===== Backlinks ===== */
.backlinks {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.backlinks h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.backlinks .note-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.backlinks .note-list .note-card {
  /* inherit grid card styles */
}

/* ===== Editor ===== */
.editor-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
}

.editor-title {
  width: 100%;
  padding: 12px 0;
  border: none;
  border-bottom: 2px solid var(--border);
  font-size: 20px;
  font-weight: 600;
  background: transparent;
  color: var(--text);
  outline: none;
  transition: border-color var(--transition);
  font-family: inherit;
  margin-bottom: 8px;
}

.editor-title:focus { border-bottom-color: var(--accent); }
.editor-title::placeholder { color: var(--text-muted); }

.editor-tags {
  width: 100%;
  padding: 8px 0;
  border: none;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  background: transparent;
  color: var(--text);
  outline: none;
  font-family: inherit;
  margin-bottom: 12px;
}

.editor-tags:focus { border-bottom-color: var(--accent); }
.editor-tags::placeholder { color: var(--text-muted); }

.editor-wrapper .EasyMDEContainer { flex: 1; display: flex; flex-direction: column; }
.editor-wrapper .EasyMDEContainer .CodeMirror { flex: 1; height: auto; border-radius: var(--radius-sm); border-color: var(--border); }

.editor-wrapper .editor-toolbar {
  border-color: var(--border);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  background: var(--surface);
}

.editor-wrapper .editor-toolbar button { color: var(--text-muted) !important; }
.editor-wrapper .editor-toolbar button:hover,
.editor-wrapper .editor-toolbar button.active { background: var(--border); color: var(--text) !important; }

[data-theme="dark"] .editor-wrapper .CodeMirror {
  background: var(--surface);
  color: var(--text);
  border-color: var(--border);
}

[data-theme="dark"] .editor-wrapper .CodeMirror-gutters {
  background: var(--bg);
  border-color: var(--border);
}

[data-theme="dark"] .editor-wrapper .editor-preview {
  background: var(--surface);
}

[data-theme="dark"] .editor-wrapper .editor-preview pre {
  background: var(--code-bg);
}

.editor-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* ===== Search results ===== */
.search-results { display: flex; flex-direction: column; gap: 10px; }

.search-result {
  display: block;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  color: var(--text);
  text-decoration: none;
  transition: border-color var(--transition);
}

.search-result:hover { border-color: var(--accent); }
.search-result h3 { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.search-result p { font-size: 13px; color: var(--text-muted); }
.search-result mark { background: #fef08a; color: #1e293b; padding: 1px 3px; border-radius: 2px; }

[data-theme="dark"] .search-result mark { background: #854d0e; color: #fef08a; }

/* ===== Graph ===== */
.graph-page .main { max-width: none; }
.graph-page .topbar { max-width: 960px; margin-left: auto; margin-right: auto; }

.graph-container {
  width: 100%;
  height: calc(100vh - 120px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  overflow: hidden;
}

/* ===== Empty state ===== */
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 64px 0;
  font-size: 15px;
}

.empty a {
  color: var(--accent);
  font-weight: 500;
}

/* ===== Misc ===== */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

- [ ] **Step 2: Verify the CSS file was written**

Run: `wc -l static/css/style.css`
Expected: ~300+ lines

- [ ] **Step 3: Commit**

```bash
git add static/css/style.css
git commit -m "feat: rewrite CSS with design system, sidebar layout, light/dark mode

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: Rewrite base.html with sidebar layout and theme toggle

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Write the new base template**

Replace the entire content of `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Knowledge Base{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
    <script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <aside class="sidebar">
        <div class="sidebar-logo"></div>
        <nav class="sidebar-nav">
            <a href="/" class="sidebar-btn {{ 'active' if request.url.path == '/' else '' }}" title="首页">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            </a>
            <a href="/graph" class="sidebar-btn {{ 'active' if '/graph' in request.url.path else '' }}" title="知识图谱">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"/><circle cx="17" cy="19" r="2"/><circle cx="7" cy="19" r="2"/><line x1="10.4" y1="6.5" x2="14.5" y2="17.5"/><line x1="7.5" y1="17.5" x2="9.6" y2="6.5"/><line x1="13.1" y1="6.5" x2="15.5" y2="17.5"/></svg>
            </a>
        </nav>
        <a href="/note/new" class="sidebar-new" title="新建笔记">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </a>
        <button class="theme-toggle" id="theme-toggle" title="切换主题" aria-label="切换亮色/暗色模式">
            <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
    </aside>

    <main class="main">
        {% block content %}{% endblock %}
    </main>

    <script>
    (function() {
        const STORAGE_KEY = 'kb-theme';
        const toggle = document.getElementById('theme-toggle');

        function getTheme() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) return stored;
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        function applyTheme(theme) {
            if (theme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }
        }

        applyTheme(getTheme());

        toggle.addEventListener('click', function() {
            const current = document.documentElement.hasAttribute('data-theme') ? 'dark' : 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem(STORAGE_KEY, next);
        });
    })();
    </script>

    {% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Start the dev server and check the page renders**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765 &`
Open: `http://localhost:8765`
Expected: Page loads with sidebar visible, theme toggle works. Content area is unstyled beyond what the CSS provides (templates not yet updated).

- [ ] **Step 3: Stop the dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 4: Commit**

```bash
git add templates/base.html
git commit -m "feat: add sidebar layout and light/dark theme toggle

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: Update index.html with magazine grid layout

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Write the new index template**

Replace the entire content of `templates/index.html`:

```html
{% extends "base.html" %}
{% block title %}{{ tag_name or '首页' }} - Knowledge Base{% endblock %}
{% block content %}

<div class="topbar">
    <h2>{% if tag_name %}#{{ tag_name }}{% else %}最近笔记{% endif %}</h2>
    <form action="/search" method="get" class="topbar-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" name="q" placeholder="搜索笔记..." value="{{ query or '' }}">
    </form>
</div>

{% if tags %}
<div class="tag-cloud">
    {% for t in tags %}
    <a href="/tag/{{ t.slug }}" class="tag">{{ t.name }}</a>
    {% endfor %}
</div>
{% endif %}

{% if notes %}
<div class="note-grid">
    {% for note in notes %}
    <a href="/note/{{ note.slug }}" class="note-card">
        <h3>{{ note.title }}</h3>
        <span class="meta">{{ note.updated_at[:10] }}{% if not note.content %} · 草稿{% endif %}</span>
    </a>
    {% endfor %}
</div>
{% else %}
<div class="empty">还没有笔记，<a href="/note/new">写一篇</a></div>
{% endif %}

{% endblock %}
```

- [ ] **Step 2: Start the dev server and verify the homepage**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765`
Open: `http://localhost:8765`
Expected: Notes rendered in a 2-column grid. Search bar in topbar. Tag cloud above grid. Cards have hover effect with left blue border.

- [ ] **Step 3: Stop the dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat: update homepage to magazine grid layout with topbar search

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: Update note detail page

**Files:**
- Modify: `templates/note_detail.html`

- [ ] **Step 1: Write the new detail template**

Replace the entire content of `templates/note_detail.html`:

```html
{% extends "base.html" %}
{% block title %}{{ note.title }} - Knowledge Base{% endblock %}
{% block content %}

<div class="note-detail">
    <a href="/" class="back-link">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        返回
    </a>

    <h1 class="note-title">{{ note.title }}</h1>

    <div class="prose">
        {{ note.html_content | safe if note.html_content else note.content }}
    </div>

    <div class="actions">
        <a href="/note/{{ note.slug }}/edit" class="btn">编辑</a>
        <button class="btn btn-danger" onclick="if(confirm('确定删除？')){fetch('/api/notes/{{ note.id }}/delete',{method:'POST'}).then(()=>location.href='/')}">删除</button>
    </div>
</div>

{% if backlinks %}
<div class="backlinks">
    <h3>链接到这里的笔记</h3>
    <div class="note-list" style="margin-top: 12px;">
        {% for bl in backlinks %}
        <a href="/note/{{ bl.slug }}" class="note-card">
            <h3>{{ bl.title }}</h3>
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}

{% endblock %}
```

- [ ] **Step 2: Start dev server and verify a note detail page**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765`
Open: `http://localhost:8765/note/<any-existing-note-slug>`
Expected: Back arrow, large title, prose-styled content, action buttons, backlinks section if any.

- [ ] **Step 3: Stop the dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 4: Commit**

```bash
git add templates/note_detail.html
git commit -m "feat: redesign note detail page with prose styling and back-link

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5: Update note editor page

**Files:**
- Modify: `templates/note_edit.html`

- [ ] **Step 1: Write the new editor template**

Replace the entire content of `templates/note_edit.html`:

```html
{% extends "base.html" %}
{% block title %}{% if note %}编辑 {{ note.title }}{% else %}新建笔记{% endif %} - Knowledge Base{% endblock %}
{% block content %}

<div class="topbar">
    <h2>{% if note %}编辑笔记{% else %}新建笔记{% endif %}</h2>
</div>

<div class="editor-wrapper">
    <form id="note-form" style="display: contents;">
        {% if note %}<input type="hidden" name="note_id" value="{{ note.id }}">{% endif %}
        <input type="text" name="title" placeholder="标题" value="{{ note.title if note else '' }}" class="editor-title">
        <input type="text" name="tags" placeholder="标签（逗号分隔）" value="{{ note_tags if note_tags else '' }}" class="editor-tags">
        <textarea id="editor-textarea" name="content">{{ note.content if note else '' }}</textarea>
        <div class="editor-actions">
            <button type="button" id="save-btn" class="btn">保存</button>
            {% if note %}
            <a href="/note/{{ note.slug }}" class="btn btn-ghost">取消</a>
            {% else %}
            <a href="/" class="btn btn-ghost">取消</a>
            {% endif %}
        </div>
    </form>
</div>

<script src="/static/js/editor.js"></script>
{% endblock %}
```

- [ ] **Step 2: Start dev server and verify the editor page**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765`
Open: `http://localhost:8765/note/new`
Expected: Borderless title input, tags input, EasyMDE editor filling remaining height, save/cancel buttons.

- [ ] **Step 3: Stop the dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 4: Commit**

```bash
git add templates/note_edit.html
git commit -m "feat: redesign editor page with borderless inputs and full-height layout

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: Update search results page

**Files:**
- Modify: `templates/search_results.html`

- [ ] **Step 1: Write the new search results template**

Replace the entire content of `templates/search_results.html`:

```html
{% extends "base.html" %}
{% block title %}搜索: {{ query }} - Knowledge Base{% endblock %}
{% block content %}

<div class="topbar">
    <h2>搜索: "{{ query }}"</h2>
    <form action="/search" method="get" class="topbar-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" name="q" placeholder="搜索笔记..." value="{{ query or '' }}">
    </form>
</div>

{% if results %}
<div class="search-results">
    {% for r in results %}
    <a href="/note/{{ r.slug }}" class="search-result">
        <h3>{{ r.title_hl | safe if r.title_hl else r.title }}</h3>
        {% if r.content_hl %}<p>{{ r.content_hl | safe }}</p>{% endif %}
    </a>
    {% endfor %}
</div>
{% elif query %}
<div class="empty">没有找到匹配 "{{ query }}" 的结果</div>
{% endif %}

{% endblock %}
```

- [ ] **Step 2: Start dev server and verify search**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765`
Open: `http://localhost:8765/search?q=python`
Expected: Search results in cards with highlighted snippets. Topbar with pre-filled search input.

- [ ] **Step 3: Stop the dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 4: Commit**

```bash
git add templates/search_results.html
git commit -m "feat: redesign search results page with topbar and card layout

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: Update graph page and graph.js for theme support

**Files:**
- Modify: `templates/graph.html`
- Modify: `static/js/graph.js`

- [ ] **Step 1: Write the new graph template**

Replace the entire content of `templates/graph.html`:

```html
{% extends "base.html" %}
{% block title %}知识图谱 - Knowledge Base{% endblock %}
{% block content %}

<div class="topbar">
    <h2>知识图谱</h2>
</div>
<div id="graph-container" class="graph-container"></div>
<script src="/static/js/graph.js"></script>
{% endblock %}
```

- [ ] **Step 2: Update graph.js with theme-aware colors**

Replace the entire content of `static/js/graph.js`:

```js
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('graph-container');
    if (!container) return;

    const isDark = document.documentElement.hasAttribute('data-theme');
    const colors = {
        node: '#3b82f6',
        link: isDark ? '#475569' : '#d6d3d1',
        label: isDark ? '#94a3b8' : '#78716c',
    };

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    fetch('/api/graph')
        .then(res => res.json())
        .then(data => {
            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.edges).id(d => d.slug).distance(80))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .selectAll('line')
                .data(data.edges)
                .join('line')
                .attr('stroke', colors.link)
                .attr('stroke-width', 1);

            const node = svg.append('g')
                .selectAll('circle')
                .data(data.nodes)
                .join('circle')
                .attr('r', d => Math.max(4, Math.min(20, d.degree * 3 + 4)))
                .attr('fill', colors.node)
                .attr('cursor', 'pointer')
                .attr('stroke', isDark ? '#1e293b' : '#fff')
                .attr('stroke-width', 1.5)
                .on('click', (event, d) => {
                    window.location.href = '/note/' + d.slug;
                })
                .call(d3.drag()
                    .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                    .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
                    .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
                );

            const labels = svg.append('g')
                .selectAll('text')
                .data(data.nodes)
                .join('text')
                .text(d => d.title.length > 10 ? d.title.slice(0, 10) + '...' : d.title)
                .attr('font-size', 10)
                .attr('dx', 14)
                .attr('dy', 4)
                .attr('fill', colors.label)
                .style('pointer-events', 'none');

            simulation.on('tick', () => {
                link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
                node.attr('cx', d => d.x).attr('cy', d => d.y);
                labels.attr('x', d => d.x).attr('y', d => d.y);
            });
        });
});
```

- [ ] **Step 3: Start dev server and verify graph page**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765`
Open: `http://localhost:8765/graph`
Expected: Graph renders with theme-appropriate colors. Toggle dark mode — refresh — graph uses dark-appropriate link/label colors.

- [ ] **Step 4: Stop the dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 5: Commit**

```bash
git add templates/graph.html static/js/graph.js
git commit -m "feat: make graph theme-aware with dark mode colors

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: Final integration test

**Files:**
- No changes — verification only

- [ ] **Step 1: Start the dev server**

Run: `cd /Users/mymac/cc && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765`

- [ ] **Step 2: Verify all pages**

Navigate through each page and check:
- [ ] `/` — sidebar visible, 2-column grid, search bar, tag cloud, theme toggle works
- [ ] `/note/new` — editor loads, EasyMDE renders, save creates note and redirects
- [ ] `/note/<slug>` — detail page with back-link, prose content, action buttons
- [ ] `/note/<slug>/edit` — editor pre-filled with note data
- [ ] `/search?q=<term>` — results with highlights
- [ ] `/graph` — D3 graph renders, nodes clickable
- [ ] Toggle dark mode — all pages respect theme, preference persists across page loads
- [ ] Browser refresh on dark mode — stays dark (localStorage)

- [ ] **Step 3: Stop dev server**

Run: `kill $(lsof -ti:8765)`

- [ ] **Step 4: Commit any remaining fixes**

```bash
git status
# If changes: git add <files> && git commit -m "chore: integration fixes after redesign"
```

---

## Verification Checklist

At the end, verify:

1. All existing functionality still works (CRUD notes, search, graph, tag filtering)
2. Sidebar visible on every page, active state correct
3. Light/dark toggle works and persists across page loads
4. No horizontal scroll on viewport >= 768px
5. Code blocks always have dark background regardless of theme
6. Focus states visible on keyboard navigation
7. Graph colors adapt to theme
