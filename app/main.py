from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import clientes, pedidos, produtos
from app.core.config import configuracao
from app.core.db import criar_tabelas


def criar_aplicacao() -> FastAPI:
    @asynccontextmanager
    async def ciclo_de_vida(_aplicacao: FastAPI):
        criar_tabelas()
        yield

    aplicacao = FastAPI(
        title=configuracao.nome_api,
        version=configuracao.versao_api,
        lifespan=ciclo_de_vida,
    )
    aplicacao.include_router(clientes.router, prefix="/api/v1")
    aplicacao.include_router(produtos.router, prefix="/api/v1")
    aplicacao.include_router(pedidos.router, prefix="/api/v1")

    @aplicacao.get("/", tags=["Saúde"])
    def verificar_saude() -> dict[str, str]:
        return {"mensagem": "Minha API está no ar"}

    @aplicacao.get("/health", tags=["Saúde"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return aplicacao


app = criar_aplicacao()
