import pytest


def test_inventory_add_item(inventory, inventory_item):
    inventory.add_item(item=inventory_item)
    assert inventory.value == 50


def test_inventory_item_update_name(inventory_item):
    inventory_item.update_name(val="NEW_NAME")
    assert inventory_item.name == "NEW_NAME"


def test_inventory_item_update_price(inventory_item):
    inventory_item.update_price(val=4.50)
    assert inventory_item.price == 4.50


def test_inventory_item_update_quantity(inventory_item):
    inventory_item.update_quantity(val=50)
    assert inventory_item.quantity == 50


def test_store_update_item_price(store, inventory_item):
    store.update_item_price(item_id=inventory_item.id, val=6.0)
    assert store.inventory.value == 60


def test_store_update_item_quantity(store, inventory_item):
    store.update_item_quantity(item_id=inventory_item.id, val=5)
    assert store.inventory.value == 25


def test_store_process_store_transaction(store, store_transaction):
    assert store.inventory.value == 50
    store.process_store_transaction(
        transaction=store_transaction
    )
    assert store.inventory.value == 45


def test_store_process_store_transaction_1(store, store_transaction):
    store_transaction.quantity = 30

    with pytest.raises(ValueError):
        store.process_store_transaction(
            transaction=store_transaction
        )

