from copy import deepcopy

from data import CLIENTES, ETAPAS_INICIAIS, PEDIDOS, PRODUTOS


class OrderStore:
    def __init__(self):
        self.pedidos = deepcopy(PEDIDOS)
        self.clientes = deepcopy(CLIENTES)
        self.produtos = deepcopy(PRODUTOS)
        self.etapas = dict(ETAPAS_INICIAIS)
        self.cliente_por_id = {cliente["id"]: cliente for cliente in self.clientes}
        self.produto_por_id = {produto["id"]: produto for produto in self.produtos}

    def lane_orders(self, key: str, query: str = "") -> list[dict]:
        if key == "finalizados":
            candidates = [order for order in self.pedidos if order["estado"] != "Pendente"]
        else:
            candidates = [
                order
                for order in self.pedidos
                if order["estado"] == "Pendente" and self.etapas.get(order["id"]) == key
            ]
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return candidates
        return [
            order
            for order in candidates
            if normalized_query
            in self.cliente_por_id.get(order["cliente_id"], {}).get("nome", "").casefold()
        ]

    def move_order(self, order_id: int, destination: str) -> bool:
        order = self._pending_order(order_id)
        if order is None:
            return False
        if destination == "finalizados":
            order["estado"] = "Concluido"
            self.etapas.pop(order_id, None)
        elif destination in ("novos", "andamento"):
            self.etapas[order_id] = destination
        else:
            return False
        return True

    def cancel_order(self, order_id: int) -> bool:
        order = self._pending_order(order_id)
        if order is None:
            return False
        order["estado"] = "Cancelado"
        self.etapas.pop(order_id, None)
        return True

    def add_order(self, order: dict) -> int:
        order["id"] = max((item["id"] for item in self.pedidos), default=100) + 1
        self.pedidos.insert(0, order)
        self.etapas[order["id"]] = "novos"
        return order["id"]

    def add_customer(self, customer: dict) -> int:
        customer["id"] = max(self.cliente_por_id, default=0) + 1
        self.clientes.append(customer)
        self.cliente_por_id[customer["id"]] = customer
        return customer["id"]

    def add_product(self, product: dict) -> int:
        product["id"] = max(self.produto_por_id, default=0) + 1
        self.produtos.append(product)
        self.produto_por_id[product["id"]] = product
        return product["id"]

    def delete_customer(self, customer_id: int) -> bool:
        if self._has_pending_customer(customer_id):
            return False
        customer = next((item for item in self.clientes if item["id"] == customer_id), None)
        if customer is None:
            return False
        self.clientes.remove(customer)
        return True

    def delete_product(self, product_id: int) -> bool:
        if self._has_pending_product(product_id):
            return False
        product = next((item for item in self.produtos if item["id"] == product_id), None)
        if product is None:
            return False
        self.produtos.remove(product)
        return True

    def _pending_order(self, order_id: int) -> dict | None:
        order = next((item for item in self.pedidos if item["id"] == order_id), None)
        return order if order and order["estado"] == "Pendente" else None

    def _has_pending_customer(self, customer_id: int) -> bool:
        return any(
            order["estado"] == "Pendente" and order["cliente_id"] == customer_id
            for order in self.pedidos
        )

    def _has_pending_product(self, product_id: int) -> bool:
        return any(
            order["estado"] == "Pendente"
            and any(item["produto_id"] == product_id for item in order["itens"])
            for order in self.pedidos
        )
