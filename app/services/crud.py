from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.models import Cliente, Entrega, EstadoPedido, ItemPedido, Pedido, Produto
from app.schemas.schemas import (
    ClienteAtualizacao,
    ClienteCriacao,
    PedidoAtualizacao,
    PedidoCriacao,
    ProdutoAtualizacao,
    ProdutoCriacao,
)


def obter_cliente(sessao: Session, cliente_id: int) -> Cliente:
    cliente = sessao.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente


def criar_cliente(sessao: Session, dados: ClienteCriacao) -> Cliente:
    cliente = Cliente(**dados.model_dump())
    sessao.add(cliente)
    sessao.commit()
    sessao.refresh(cliente)
    return cliente


def listar_clientes(sessao: Session) -> list[Cliente]:
    return list(sessao.scalars(select(Cliente).order_by(Cliente.id)))


def atualizar_cliente(sessao: Session, cliente_id: int, dados: ClienteAtualizacao) -> Cliente:
    cliente = obter_cliente(sessao, cliente_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    sessao.commit()
    sessao.refresh(cliente)
    return cliente


def excluir_cliente(sessao: Session, cliente_id: int) -> None:
    cliente = obter_cliente(sessao, cliente_id)
    if any(pedido.estado == EstadoPedido.PENDENTE for pedido in cliente.pedidos):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cliente possui pedido pendente")
    cliente.ativo = False
    sessao.commit()


def obter_produto(sessao: Session, produto_id: int, somente_ativo: bool = False) -> Produto:
    produto = sessao.get(Produto, produto_id)
    if produto is None or (somente_ativo and not produto.ativo):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto


def criar_produto(sessao: Session, dados: ProdutoCriacao) -> Produto:
    produto = Produto(**dados.model_dump())
    sessao.add(produto)
    sessao.commit()
    sessao.refresh(produto)
    return produto


def listar_produtos(sessao: Session) -> list[Produto]:
    return list(sessao.scalars(select(Produto).where(Produto.ativo.is_(True)).order_by(Produto.id)))


def atualizar_produto(sessao: Session, produto_id: int, dados: ProdutoAtualizacao) -> Produto:
    produto = obter_produto(sessao, produto_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    sessao.commit()
    sessao.refresh(produto)
    return produto


def excluir_produto(sessao: Session, produto_id: int) -> None:
    produto = obter_produto(sessao, produto_id)
    if any(item.pedido.estado == EstadoPedido.PENDENTE for item in produto.itens):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Produto possui item em pedido pendente")
    produto.ativo = False
    sessao.commit()


def _carregar_pedido(sessao: Session, pedido_id: int) -> Pedido:
    consulta = (
        select(Pedido)
        .where(Pedido.id == pedido_id)
        .options(
            selectinload(Pedido.cliente),
            selectinload(Pedido.entrega),
            selectinload(Pedido.itens).selectinload(ItemPedido.produto),
        )
    )
    pedido = sessao.scalar(consulta)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    return pedido


def criar_pedido(sessao: Session, dados: PedidoCriacao) -> Pedido:
    cliente = obter_cliente(sessao, dados.cliente_id)
    if not cliente.ativo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cliente inativo")

    pedido = Pedido(cliente=cliente, data_entrega=dados.data_entrega)
    produto_ids = [item.produto_id for item in dados.itens]
    produtos = {produto.id: produto for produto in sessao.scalars(select(Produto).where(Produto.id.in_(produto_ids)))}
    if len(produtos) != len(set(produto_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Um ou mais produtos não encontrados")
    if any(not produto.ativo for produto in produtos.values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pedido contém produto inativo")

    pedido.itens = [
        ItemPedido(
            produto=produtos[item.produto_id],
            quantidade=item.quantidade,
            valor_unitario=produtos[item.produto_id].valor,
        )
        for item in dados.itens
    ]
    if dados.entrega:
        pedido.entrega = Entrega(**dados.entrega.model_dump())
    sessao.add(pedido)
    sessao.commit()
    return _carregar_pedido(sessao, pedido.id)


def listar_pedidos(sessao: Session) -> list[Pedido]:
    consulta = select(Pedido).options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.entrega),
        selectinload(Pedido.itens).selectinload(ItemPedido.produto),
    ).order_by(Pedido.id)
    return list(sessao.scalars(consulta))


def atualizar_pedido(sessao: Session, pedido_id: int, dados: PedidoAtualizacao) -> Pedido:
    pedido = _carregar_pedido(sessao, pedido_id)
    if pedido.estado != EstadoPedido.PENDENTE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pedido finalizado não pode ser alterado")
    valores = dados.model_dump(exclude_unset=True, exclude={"entrega"})
    if "cliente_id" in valores:
        cliente = obter_cliente(sessao, valores["cliente_id"])
        if not cliente.ativo:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cliente inativo")
        pedido.cliente = cliente
    for campo, valor in valores.items():
        if campo != "cliente_id":
            setattr(pedido, campo, valor)
    if "entrega" in dados.model_fields_set:
        if pedido.entrega:
            if dados.entrega is None:
                sessao.delete(pedido.entrega)
                pedido.entrega = None
            else:
                pedido.entrega.endereco = dados.entrega.endereco
                pedido.entrega.valor = dados.entrega.valor
        elif dados.entrega:
            pedido.entrega = Entrega(**dados.entrega.model_dump())
    sessao.commit()
    return _carregar_pedido(sessao, pedido.id)


def atualizar_estado(sessao: Session, pedido_id: int, novo_estado: EstadoPedido) -> Pedido:
    pedido = _carregar_pedido(sessao, pedido_id)
    transicoes = {
        EstadoPedido.PENDENTE: {EstadoPedido.CONCLUIDO, EstadoPedido.CANCELADO},
        EstadoPedido.CONCLUIDO: set(),
        EstadoPedido.CANCELADO: set(),
    }
    if novo_estado not in transicoes[pedido.estado]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transição de estado não permitida")
    pedido.estado = novo_estado
    sessao.commit()
    return _carregar_pedido(sessao, pedido.id)


def excluir_pedido(sessao: Session, pedido_id: int) -> None:
    pedido = _carregar_pedido(sessao, pedido_id)
    if pedido.estado == EstadoPedido.PENDENTE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pedido pendente não pode ser excluído")
    sessao.delete(pedido)
    sessao.commit()
