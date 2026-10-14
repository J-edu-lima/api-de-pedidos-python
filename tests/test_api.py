from datetime import date


def cadastrar_dados_basicos(cliente_api):
    cliente = cliente_api.post("/api/v1/clientes", json={"nome": "Ana", "numero": "11999999999"})
    chocolate = cliente_api.post(
        "/api/v1/produtos", json={"nome": "Chocolate", "descricao": "Caixa", "valor": "50.00"}
    )
    leite = cliente_api.post("/api/v1/produtos", json={"nome": "Leite", "valor": "10.00"})
    return cliente.json(), chocolate.json(), leite.json()


def test_cadastra_pedido_calcula_total_e_congela_preco(cliente_api):
    cliente, chocolate, leite = cadastrar_dados_basicos(cliente_api)
    resposta = cliente_api.post(
        "/api/v1/pedidos",
        json={
            "cliente_id": cliente["id"],
            "itens": [
                {"produto_id": chocolate["id"], "quantidade": 2},
                {"produto_id": leite["id"], "quantidade": 1},
            ],
            "entrega": {"endereco": "Rua A, 10", "valor": "5.00"},
        },
    )

    assert resposta.status_code == 201
    pedido = resposta.json()
    assert pedido["valor_total"] == "115.00"
    assert pedido["estado"] == "Pendente"
    assert len(pedido["itens"]) == 2

    cliente_api.patch(f"/api/v1/produtos/{chocolate['id']}", json={"valor": "60.00"})
    consulta = cliente_api.get(f"/api/v1/pedidos/{pedido['id']}")
    assert consulta.json()["valor_total"] == "115.00"


def test_retirada_no_local_e_transicoes_de_estado(cliente_api):
    cliente, chocolate, _ = cadastrar_dados_basicos(cliente_api)
    resposta = cliente_api.post(
        "/api/v1/pedidos",
        json={"cliente_id": cliente["id"], "itens": [{"produto_id": chocolate["id"], "quantidade": 1}]},
    )
    pedido = resposta.json()
    assert pedido["entrega"] is None
    assert pedido["valor_total"] == "50.00"
    assert pedido["data_entrada"]

    concluido = cliente_api.patch(
        f"/api/v1/pedidos/{pedido['id']}/estado", json={"estado": "Concluido"}
    )
    assert concluido.status_code == 200
    bloqueado = cliente_api.patch(
        f"/api/v1/pedidos/{pedido['id']}/estado", json={"estado": "Cancelado"}
    )
    assert bloqueado.status_code == 409


def test_validacoes_e_conflitos(cliente_api):
    cliente, chocolate, _ = cadastrar_dados_basicos(cliente_api)
    inexistente = cliente_api.post(
        "/api/v1/pedidos",
        json={"cliente_id": cliente["id"], "itens": [{"produto_id": 999, "quantidade": 1}]},
    )
    assert inexistente.status_code == 404

    pedido = cliente_api.post(
        "/api/v1/pedidos",
        json={"cliente_id": cliente["id"], "itens": [{"produto_id": chocolate["id"], "quantidade": 1}]},
    ).json()
    assert cliente_api.delete(f"/api/v1/clientes/{cliente['id']}").status_code == 409
    assert cliente_api.delete(f"/api/v1/pedidos/{pedido['id']}").status_code == 409


def test_crud_de_cliente_e_produto(cliente_api):
    cliente = cliente_api.post("/api/v1/clientes", json={"nome": "Joao", "numero": "11900000000"})
    assert cliente.status_code == 201
    assert cliente_api.get(f"/api/v1/clientes/{cliente.json()['id']}").status_code == 200
    assert cliente_api.patch(f"/api/v1/clientes/{cliente.json()['id']}", json={"nome": "Joao Silva"}).status_code == 200
    produto = cliente_api.post("/api/v1/produtos", json={"nome": "Agua", "valor": "3.50"})
    assert produto.status_code == 201
    assert cliente_api.patch(f"/api/v1/produtos/{produto.json()['id']}", json={"valor": "4.00"}).status_code == 200
    assert cliente_api.delete(f"/api/v1/produtos/{produto.json()['id']}").status_code == 204
    assert cliente_api.delete(f"/api/v1/clientes/{cliente.json()['id']}").status_code == 204
