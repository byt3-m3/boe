from dataclasses import dataclass
from uuid import UUID

from eventsourcing.domain import Aggregate, event
from src.models.core import ValueObject


@dataclass
class StoreTransaction(ValueObject):
    item_id: UUID
    quantity: int


@dataclass
class InventoryItem(Aggregate):
    name: str
    price: float
    quantity: int

    @event
    def update_name(self, val: str):
        self.name = val

    @event
    def update_price(self, val: float):
        self.price = val

    @event
    def update_quantity(self, val: int):
        self.quantity = val


@dataclass
class Inventory(Aggregate):
    item_map: dict
    value: float

    def _calculate_value(self):
        value = 0
        for item_name, item in self.item_map.items():
            item: InventoryItem

            _val = item.price * item.quantity
            value += _val

        self.value = round(value, 2)

    @event
    def add_item(self, item: InventoryItem):
        if not self.item_map.get(item.name):
            self.item_map[item.id] = item

        self._calculate_value()

    @event
    def update_item_price(self, item_id, val: float):
        item: InventoryItem = self.item_map.get(item_id)
        item.update_price(val=val)
        self._calculate_value()

    @event
    def update_item_quantity(self, item_id, val: int):
        item: InventoryItem = self.item_map.get(item_id)
        item.update_quantity(val=val)
        self._calculate_value()


@dataclass
class Store(Aggregate):
    inventory: Inventory

    @event
    def save_item(self, item: InventoryItem):
        self.inventory.add_item(item=item)

    def update_item_price(self, item_id, val: float):
        self.inventory.update_item_price(
            item_id=item_id,
            val=val
        )

    def update_item_quantity(self, item_id, val: int):
        self.inventory.update_item_quantity(
            item_id=item_id,
            val=val
        )

    def process_store_transaction(self, transaction: StoreTransaction):
        item: InventoryItem = self.inventory.item_map.get(transaction.item_id)
        if item.quantity < transaction.quantity:
            raise ValueError(
                f"Invalid Transaction: Not enough quantity for item {item.quantity} - Transaction: {transaction.quantity}")

        self.inventory.update_item_quantity(
            item_id=transaction.item_id,
            val=(item.quantity - int(transaction.quantity))
        )
