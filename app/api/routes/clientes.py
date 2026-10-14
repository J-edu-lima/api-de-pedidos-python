from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.db import obter_sessao
from app.schemas.schemas import ClienteAtualizacao, ClienteCriacao, ClienteResposta
from app.services import crud

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: ClienteCriacao, sessao: Session = Depends(obter_sessao)):
    return crud.criar_cliente(sessao, dados)


@router.get("", response_model=list[ClienteResposta])
def listar(sessao: Session = Depends(obter_sessao)):
    return crud.listar_clientes(sessao)


@router.get("/{cliente_id}", response_model=ClienteResposta)
def detalhar(cliente_id: int, sessao: Session = Depends(obter_sessao)):
    return crud.obter_cliente(sessao, cliente_id)


@router.patch("/{cliente_id}", response_model=ClienteResposta)
def atualizar(cliente_id: int, dados: ClienteAtualizacao, sessao: Session = Depends(obter_sessao)):
    return crud.atualizar_cliente(sessao, cliente_id, dados)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(cliente_id: int, sessao: Session = Depends(obter_sessao)):
    crud.excluir_cliente(sessao, cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
