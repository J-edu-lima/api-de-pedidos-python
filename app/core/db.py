from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import configuracao


class Base(DeclarativeBase):
    pass


argumentos_engine = {}
if configuracao.url_banco.startswith("sqlite"):
    argumentos_engine["connect_args"] = {"check_same_thread": False}

engine = create_engine(configuracao.url_banco, **argumentos_engine)
SessaoLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def obter_sessao() -> Generator[Session, None, None]:
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()


def criar_tabelas() -> None:
    from app.modules import models

    Base.metadata.create_all(bind=engine)
