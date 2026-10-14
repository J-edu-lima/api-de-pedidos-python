from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.db import obter_sessao
from app.schemas.schemas import ProdutoAtualizacao, ProdutoCriacao, ProdutoResposta
from app.services import crud

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.post("", response_model=ProdutoResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: ProdutoCriacao, sessao: Session = Depends(obter_sessao)):
    return crud.criar_produto(sessao, dados)


@router.get("", response_model=list[ProdutoResposta])
def listar(sessao: Session = Depends(obter_sessao)):
    return crud.listar_produtos(sessao)


@router.get("/{produto_id}", response_model=ProdutoResposta)
def detalhar(produto_id: int, sessao: Session = Depends(obter_sessao)):
    return crud.obter_produto(sessao, produto_id)


@router.patch("/{produto_id}", response_model=ProdutoResposta)
def atualizar(produto_id: int, dados: ProdutoAtualizacao, sessao: Session = Depends(obter_sessao)):
    return crud.atualizar_produto(sessao, produto_id, dados)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(produto_id: int, sessao: Session = Depends(obter_sessao)):
    crud.excluir_produto(sessao, produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
