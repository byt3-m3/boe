from uuid import UUID

from src.domains.store_domain.store_models import (
    StoreTransaction,
    InventoryItem,
    Inventory,
    Store
)


class StoreDomainFactory:
    @staticmethod
    def build_store_transaction(item_id: UUID, quantity: int) -> StoreTransaction:
        return StoreTransaction(
            item_id=item_id,
            quantity=quantity
        )

    @staticmethod
    def build_inventory_item(name: str, price: float, quantity: int) -> InventoryItem:
        return InventoryItem(
            name=name,
            price=price,
            quantity=quantity
        )

    @staticmethod
    def build_empty_inventory() -> Inventory:
        return Inventory(
            item_map={},
            value=0
        )

    @staticmethod
    def build_inventory(item_map: dict) -> Inventory:
        inventory = Inventory(
            item_map={},
            value=0
        )

        for name, item in item_map.items():
            inventory.add_item(item=item)

        return inventory

    @staticmethod
    def build_store(inventory: Inventory) -> Store:
        return Store(
            inventory=inventory
        )
