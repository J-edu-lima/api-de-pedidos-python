"""Dados locais de demonstração, no formato dos objetos do MVP."""

CLIENTES = [
    {"id": 1, "nome": "Mariana Costa", "numero": "(11) 98765-4321", "ativo": True},
    {"id": 2, "nome": "Rafael Mendes", "numero": "(11) 97654-3210", "ativo": True},
    {"id": 3, "nome": "Camila Ferreira", "numero": "(11) 96543-2109", "ativo": True},
    {"id": 4, "nome": "Lucas Almeida", "numero": "(11) 95432-1098", "ativo": True},
]

PRODUTOS = [
    {"id": 1, "nome": "Caneca personalizada", "descricao": "Caneca de cerâmica, 350 ml", "valor": 35.00, "ativo": True},
    {"id": 2, "nome": "Caixa para presente", "descricao": "Embalagem kraft com laço", "valor": 12.50, "ativo": True},
    {"id": 3, "nome": "Bolo de chocolate", "descricao": "Bolo artesanal, tamanho médio", "valor": 85.00, "ativo": True},
    {"id": 4, "nome": "Buquê de balões", "descricao": "Buquê com seis balões", "valor": 48.00, "ativo": True},
]

PEDIDOS = [
    {
        "id": 101,
        "cliente_id": 1,
        "estado": "Pendente",
        "data_entrada": "2026-11-11T09:15:00",
        "data_entrega": "2026-11-13",
        "entrega": {"endereco": "Rua das Flores, 120 — Vila Mariana", "valor": 8.00},
        "itens": [{"produto_id": 1, "quantidade": 2, "valor_unitario": 35.00}],
        "valor_total": 78.00,
    },
    {
        "id": 102,
        "cliente_id": 2,
        "estado": "Pendente",
        "data_entrada": "2026-11-11T09:42:00",
        "data_entrega": None,
        "entrega": None,
        "itens": [{"produto_id": 2, "quantidade": 3, "valor_unitario": 12.50}],
        "valor_total": 37.50,
    },
    {
        "id": 103,
        "cliente_id": 3,
        "estado": "Pendente",
        "data_entrada": "2026-11-11T10:05:00",
        "data_entrega": "2026-11-12",
        "entrega": {"endereco": "Av. Paulista, 845 — Bela Vista", "valor": 12.00},
        "itens": [{"produto_id": 3, "quantidade": 1, "valor_unitario": 85.00}],
        "valor_total": 97.00,
    },
    {
        "id": 104,
        "cliente_id": 4,
        "estado": "Pendente",
        "data_entrada": "2026-11-11T10:28:00",
        "data_entrega": "2026-11-14",
        "entrega": {"endereco": "Rua Aurora, 56 — Centro", "valor": 10.00},
        "itens": [{"produto_id": 1, "quantidade": 4, "valor_unitario": 35.00}],
        "valor_total": 150.00,
    },
    {
        "id": 105,
        "cliente_id": 1,
        "estado": "Concluido",
        "data_entrada": "2026-11-10T16:20:00",
        "data_entrega": "2026-11-11",
        "entrega": None,
        "itens": [{"produto_id": 3, "quantidade": 1, "valor_unitario": 85.00}],
        "valor_total": 85.00,
    },
    {
        "id": 106,
        "cliente_id": 2,
        "estado": "Cancelado",
        "data_entrada": "2026-11-10T14:10:00",
        "data_entrega": None,
        "entrega": {"endereco": "Rua do Sol, 19 — Saúde", "valor": 8.00},
        "itens": [{"produto_id": 4, "quantidade": 1, "valor_unitario": 48.00}],
        "valor_total": 56.00,
    },
]

# A etapa de trabalho é apenas do quadro visual; não altera o objeto da API.
ETAPAS_INICIAIS = {101: "novos", 102: "novos", 103: "andamento", 104: "andamento"}
