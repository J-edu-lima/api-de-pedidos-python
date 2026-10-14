from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class EstadoPedido(str, Enum):
    PENDENTE = "Pendente"
    CONCLUIDO = "Concluido"
    CANCELADO = "Cancelado"


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    numero: Mapped[str] = mapped_column(String(30), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)

    pedidos: Mapped[list[Pedido]] = relationship(back_populates="cliente")


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)

    itens: Mapped[list[ItemPedido]] = relationship(back_populates="produto")


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    estado: Mapped[EstadoPedido] = mapped_column(default=EstadoPedido.PENDENTE, nullable=False)
    data_entrada: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    data_entrega: Mapped[date | None] = mapped_column(Date, nullable=True)

    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
    entrega: Mapped[Entrega | None] = relationship(
        back_populates="pedido", uselist=False, cascade="all, delete-orphan"
    )
    itens: Mapped[list[ItemPedido]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class Entrega(Base):
    __tablename__ = "entregas"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), unique=True, nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)

    pedido: Mapped[Pedido] = relationship(back_populates="entrega")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(nullable=False)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped[Pedido] = relationship(back_populates="itens")
    produto: Mapped[Produto] = relationship(back_populates="itens")
