import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, obter_sessao
from app.main import app
from app.modules import models


@pytest.fixture
def cliente_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessao_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def obter_sessao_de_teste():
        sessao = sessao_local()
        try:
            yield sessao
        finally:
            sessao.close()

    app.dependency_overrides[obter_sessao] = obter_sessao_de_teste
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
