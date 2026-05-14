import jieba


def _tokenize(text: str) -> str:
    """Tokenize text for FTS5. Jieba cuts Chinese words; plain ASCII passes through.

    Uses both ``cut`` (preserves compound words) and ``cut_for_search`` (splits
    into sub-tokens).  All tokens are OR-ed with ``*`` suffix so partial
    queries match longer terms via FTS5 prefix search.

    For example, "机器学习" produces:
      - cut: "机器学习"
      - cut_for_search: "机器", "学习"
    The FTS5 index may contain the compound word as a single token, so we
    include both forms to ensure a match regardless of tokenization.
    """
    if not text:
        return ""
    tokens = list(jieba.cut(text))
    tokens += list(jieba.cut_for_search(text))
    # Deduplicate while preserving order
    seen = set()
    unique: list[str] = []
    for t in tokens:
        s = t.strip()
        if s and s not in seen:
            seen.add(s)
            unique.append(s)
    # Prefix matching: "深度*" matches "深度学习" in the FTS5 index
    return " OR ".join(
        f"{t}*" for t in unique
    )


def search_notes(db, query: str, limit: int = 20) -> list[dict]:
    """Full-text search notes by title and content."""
    tokenized = _tokenize(query)
    if not tokenized.strip():
        return []

    rows = db.execute("""
        SELECT n.id, n.title, n.slug,
               snippet(notes_fts, 0, '<mark>', '</mark>', '...', 32) AS title_hl,
               snippet(notes_fts, 1, '<mark>', '</mark>', '...', 64) AS content_hl
        FROM notes_fts f
        JOIN notes n ON n.id = f.rowid
        WHERE notes_fts MATCH ?
        ORDER BY bm25(notes_fts, 5.0, 1.0)
        LIMIT ?
    """, (tokenized, limit)).fetchall()
    return [dict(r) for r in rows]
