from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.db import obter_sessao
from app.modules.models import EstadoPedido
from app.schemas.schemas import (
    PedidoAtualizacao,
    PedidoCriacao,
    PedidoEstadoAtualizacao,
    PedidoResposta,
)
from app.services import crud

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: PedidoCriacao, sessao: Session = Depends(obter_sessao)):
    return crud.criar_pedido(sessao, dados)


@router.get("", response_model=list[PedidoResposta])
def listar(sessao: Session = Depends(obter_sessao)):
    return crud.listar_pedidos(sessao)


@router.get("/{pedido_id}", response_model=PedidoResposta)
def detalhar(pedido_id: int, sessao: Session = Depends(obter_sessao)):
    return crud._carregar_pedido(sessao, pedido_id)


@router.patch("/{pedido_id}", response_model=PedidoResposta)
def atualizar(pedido_id: int, dados: PedidoAtualizacao, sessao: Session = Depends(obter_sessao)):
    return crud.atualizar_pedido(sessao, pedido_id, dados)


@router.patch("/{pedido_id}/estado", response_model=PedidoResposta)
def alterar_estado(
    pedido_id: int,
    dados: PedidoEstadoAtualizacao,
    sessao: Session = Depends(obter_sessao),
):
    return crud.atualizar_estado(sessao, pedido_id, EstadoPedido(dados.estado))


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(pedido_id: int, sessao: Session = Depends(obter_sessao)):
    crud.excluir_pedido(sessao, pedido_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
