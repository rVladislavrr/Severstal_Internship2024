from httpx import AsyncClient


async def test_add(ac: AsyncClient):
    response = await ac.post("/add", json={
        "length": 1,
        "weight": 1,
    })
    assert response.status_code == 201
    assert not (response.json().get('data_add') is None)

    response = await ac.post("/add", json={
        "length": 0,
        "weight": 1,
    })
    assert response.status_code == 422

    response = await ac.post("/add", json={
        "length": 1,
        "weight": 0,
    })
    assert response.status_code == 422

    response = await ac.post("/add", json={
        "length": -1,
        "weight": 1,
    })
    assert response.status_code == 422

    response = await ac.post("/add", json={
        "length": 1,
        "weight": -1,
    })
    assert response.status_code == 422

    response = await ac.post("/add", json={
        "length": -1,
        "weight": -1,
    })
    assert response.status_code == 422


async def test_delete(ac: AsyncClient):
    response = await ac.delete("/del/1")
    assert response.status_code == 200
    assert not (response.json().get('data_del') is None)

    response = await ac.delete("/add/1")
    assert response.status_code == 404

async def test_get(ac: AsyncClient):
    response = await ac.get("/filters", params={"id_start": 1, "id_end": 5})
    assert response.status_code == 200
    assert len(response.json()) == 0
    await ac.post("/add", json={
        "length": 1,
        "weight": 1,
    })
    response = await ac.get("/filters", params={"id_start": 1, "id_end": 5})

    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await ac.get("/filters", params={"length_start": 1, "length_end": 5})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await ac.get("/filters", params={"weight_start": 1, "weight_end": 5})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await ac.get("/filters", params={"data_del_start": "2024-01-01"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    await ac.delete("/del/2")

    response = await ac.get("/filters", params={"data_del_start": "2024-01-01"})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await ac.get("/filters", params={"id_end": 1, "data_del_start": "2024-01-01"})
    assert response.status_code == 200
    assert len(response.json()) == 1
