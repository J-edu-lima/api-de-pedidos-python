from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.modules.models import EstadoPedido


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ClienteCriacao(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    numero: str = Field(min_length=1, max_length=30)


class ClienteAtualizacao(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    numero: str | None = Field(default=None, min_length=1, max_length=30)


class ClienteResposta(SchemaBase):
    id: int
    nome: str
    numero: str
    ativo: bool


class ProdutoCriacao(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = None
    valor: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class ProdutoAtualizacao(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = None
    valor: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class ProdutoResposta(SchemaBase):
    id: int
    nome: str
    descricao: str | None
    valor: Decimal
    ativo: bool


class EntregaCriacao(BaseModel):
    endereco: str = Field(min_length=1, max_length=255)
    valor: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)


class EntregaResposta(SchemaBase):
    endereco: str
    valor: Decimal


class ItemPedidoCriacao(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class ItemPedidoResposta(SchemaBase):
    id: int
    produto_id: int
    quantidade: int
    valor_unitario: Decimal
    produto: ProdutoResposta


class PedidoCriacao(BaseModel):
    cliente_id: int = Field(gt=0)
    itens: list[ItemPedidoCriacao] = Field(min_length=1)
    entrega: EntregaCriacao | None = None
    data_entrega: date | None = None


class PedidoAtualizacao(BaseModel):
    cliente_id: int | None = Field(default=None, gt=0)
    entrega: EntregaCriacao | None = None
    data_entrega: date | None = None


class PedidoEstadoAtualizacao(BaseModel):
    estado: EstadoPedido


class PedidoResposta(SchemaBase):
    id: int
    cliente_id: int
    cliente: ClienteResposta
    estado: EstadoPedido
    data_entrada: datetime
    data_entrega: date | None
    entrega: EntregaResposta | None
    itens: list[ItemPedidoResposta]

    @computed_field
    @property
    def valor_total(self) -> Decimal:
        total_itens = sum(
            (item.valor_unitario * item.quantidade for item in self.itens), Decimal("0.00")
        )
        return total_itens + (self.entrega.valor if self.entrega else Decimal("0.00"))

