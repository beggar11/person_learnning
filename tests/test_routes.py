def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "最近笔记" in resp.text

def test_new_note_page(client):
    resp = client.get("/note/new")
    assert resp.status_code == 200
    assert "新建" in resp.text

def test_graph_page(client):
    resp = client.get("/graph")
    assert resp.status_code == 200
    assert "graph-container" in resp.text

def test_search_page(client):
    resp = client.get("/search?q=test")
    assert resp.status_code == 200

def test_create_note_via_api(client):
    resp = client.post("/api/notes", data={"title": "Hello", "content": "World"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "hello"

def test_view_created_note(client):
    client.post("/api/notes", data={"title": "View Test", "content": "# Hello"})
    resp = client.get("/note/view-test")
    assert resp.status_code == 200
    assert "View Test" in resp.text

def test_edit_note_page(client):
    client.post("/api/notes", data={"title": "Edit Test"})
    resp = client.get("/note/edit-test/edit")
    assert resp.status_code == 200
    assert "Edit Test" in resp.text

def test_search_api(client):
    resp = client.get("/search?q=nonexistent_xyz")
    assert resp.status_code == 200
    assert "没有找到" in resp.text

def test_graph_api(client):
    client.post("/api/notes", data={"title": "G1", "content": "[[g2]]"})
    resp = client.get("/api/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data

def test_note_not_found(client):
    resp = client.get("/note/nonexistent-12345")
    assert resp.status_code == 404

def test_tag_page(client):
    client.post("/api/notes", data={"title": "Tagged", "content": "Test", "tags": "python"})
    resp = client.get("/tag/python")
    assert resp.status_code == 200
    assert "Tagged" in resp.text
