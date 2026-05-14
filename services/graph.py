def get_graph_data(db, limit: int = 200) -> dict:
    """Return {nodes, edges} for knowledge graph visualization."""
    nodes = db.execute("""
        SELECT n.slug, n.title, COUNT(l2.id) AS degree
        FROM notes n
        LEFT JOIN links l2 ON l2.target_note_id = n.id OR l2.source_note_id = n.id
        WHERE n.content != ''
        GROUP BY n.id
        ORDER BY degree DESC
        LIMIT ?
    """, (limit,)).fetchall()

    node_slugs = {row["slug"] for row in nodes}
    if not node_slugs:
        return {"nodes": [], "edges": []}

    placeholders = ",".join("?" * len(node_slugs))
    edges = db.execute(f"""
        SELECT n1.slug AS source, n2.slug AS target
        FROM links l
        JOIN notes n1 ON n1.id = l.source_note_id
        JOIN notes n2 ON n2.id = l.target_note_id
        WHERE n1.slug IN ({placeholders}) AND n2.slug IN ({placeholders})
    """, list(node_slugs) + list(node_slugs)).fetchall()

    return {
        "nodes": [{"slug": r["slug"], "title": r["title"], "degree": r["degree"]} for r in nodes],
        "edges": [{"source": r["source"], "target": r["target"]} for r in edges],
    }
