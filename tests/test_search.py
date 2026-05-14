from services.search import search_notes


def test_search_finds_by_title(db):
    from services.notes import create_note
    create_note(db, title="Python 入门", content="这是一篇教程")
    create_note(db, title="JavaScript 基础", content="前端必学")

    results = search_notes(db, "python")
    assert len(results) == 1
    assert results[0]["title"] == "Python 入门"


def test_search_finds_by_content(db):
    from services.notes import create_note
    create_note(db, title="Note A", content="深度学习基础")
    results = search_notes(db, "深度")
    assert len(results) == 1


def test_search_no_results(db):
    results = search_notes(db, "nonexistent")
    assert results == []


def test_search_chinese(db):
    from services.notes import create_note
    create_note(db, title="机器学习", content="监督学习和无监督学习")
    results = search_notes(db, "监督")
    assert len(results) == 1
    results2 = search_notes(db, "机器学习")
    assert len(results2) >= 1
