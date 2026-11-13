# API de Pedidos

MVP de uma API REST para cadastro de clientes, produtos e pedidos.

## Requisitos

- Python 3.11 ou superior
- Dependências em `requirements.txt`

## Execução

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`. O banco SQLite padrão é `pedidos.db`. Para usar outro banco SQLite, defina `URL_BANCO`, por exemplo:

```bash
URL_BANCO=sqlite:///./desenvolvimento.db uvicorn app.main:app --reload
```

## API

Todas as rotas de negócio usam o prefixo `/api/v1`:

- `POST`, `GET`, `GET/{id}`, `PATCH/{id}`, `DELETE/{id}` em `/clientes`
- `POST`, `GET`, `GET/{id}`, `PATCH/{id}`, `DELETE/{id}` em `/produtos`
- `POST`, `GET`, `GET/{id}`, `PATCH/{id}`, `DELETE/{id}` em `/pedidos`
- `PATCH /pedidos/{id}/estado` para concluir ou cancelar um pedido pendente

Um pedido pode ser criado sem entrega, representando retirada no local. Quando houver entrega, o endereço é obrigatório e o valor da taxa é opcional, com padrão zero. Cada item informa quantidade; o valor unitário é copiado do produto no momento da criação do pedido.

## Testes

```bash
pytest
```

O arquivo `teste.ipynb` continua disponível para experimentos manuais com a API.
