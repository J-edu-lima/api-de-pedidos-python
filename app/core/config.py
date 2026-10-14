import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuracao:
    url_banco: str = os.getenv("URL_BANCO", "sqlite:///./pedidos.db")
    nome_api: str = "API de Pedidos"
    versao_api: str = "1.0.0"


configuracao = Configuracao()
