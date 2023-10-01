import unittest
from simulation import FoodItem, FoodType, Pantry, StrictStrategy, LaxStrategy


class TestPantryStrategy(unittest.TestCase):

    def setUp(self):
        self.strict_strategy = StrictStrategy()
        self.lax_strategy = LaxStrategy()

    def test_strict_strategy_discards_best_before(self):
        ## This test verifies that the StrictStrategy recommends discarding a perishable
        # food item as soon as it is past its best before date.
        item = FoodItem("PerishableItem1", FoodType.PERISHABLE, 1, 5, 1.0)
        item.day_passes()  # Makes the item past its best before date.
        self.assertTrue(self.strict_strategy.should_discard(item))

    def test_lax_strategy_does_not_discard_best_before(self):
        ## This test ensures that the LaxStrategy does not recommend discarding a perishable food item just because
        # it is past its best before date, but hasn't reached its spoilage date.
        item = FoodItem("PerishableItem2", FoodType.PERISHABLE, 1, 5, 1.0)
        item.day_passes()  # Makes the item past its best before date.
        self.assertFalse(self.lax_strategy.should_discard(item))

class TestPantry(unittest.TestCase):

    def setUp(self):
        self.pantry = Pantry()

    def test_expired_items_removed(self):
        ## This test checks if items that have passed their spoilage date are automatically
        # removed from the pantry, even if using a lax strategy.
        item = FoodItem("PerishableItem3", FoodType.PERISHABLE, 1, 5, 1.0)
        self.pantry.add_item(item)
        self.pantry.step(LaxStrategy())  # To check if only expired items get removed.
        self.assertIn(item, self.pantry.items_by_type[FoodType.PERISHABLE])
        for _ in range(5):
            self.pantry.step(LaxStrategy())  # To make the item expire.
        all_items = [item for item_list in self.pantry.items_by_type.values() for item in item_list]

        self.assertNotIn(item, all_items)

    def test_strategy_discards_logged_separately_from_expired_discards(self):
        ## This test verifies that items discarded based on strategy are logged separately from items discarded
        # due to being expired. This ensures there's no double-counting.
        item1 = FoodItem("LeftoverItem1", FoodType.LEFTOVER, 1, 5, 2.0)
        item2 = FoodItem("LeftoverItem2", FoodType.LEFTOVER, 1, 1, 3.0)
        self.pantry.add_item(item1)
        self.pantry.add_item(item2)
        self.pantry.step(StrictStrategy())  # Only item1 should be discarded by strategy.
        self.assertEqual(self.pantry.waste_log['strategy_discards'][1][FoodType.LEFTOVER], item1.quantity)
        self.assertEqual(self.pantry.waste_log['expired_discards'][1][FoodType.LEFTOVER], item2.quantity)

    def test_step_removes_empty_items(self):
        # Test if empty items are removed from the pantry after calling the step method
        item1 = FoodItem("Item 1", FoodType.LEFTOVER, 2, 2, 0.0)
        item2 = FoodItem("Item 2", FoodType.PERISHABLE, 2, 2, 0.0)

        self.pantry.items_by_type[FoodType.LEFTOVER].append(item1)
        self.pantry.items_by_type[FoodType.PERISHABLE].append(item2)
        self.pantry.step(StrictStrategy())

        # Checking for leftovers and perishables.
        self.assertNotIn(item1, self.pantry.items_by_type[FoodType.LEFTOVER])
        self.assertNotIn(item2, self.pantry.items_by_type[FoodType.PERISHABLE])

    def test_total_discard_count(self):
        ## This test verifies that the total weight discarded
        # (both via strategy and expired items) equals the total weight of
        # the items added to the pantry.
        item1 = FoodItem("PerishableItem4", FoodType.PERISHABLE, 1, 5, 1.0)
        item2 = FoodItem("LeftoverItem3", FoodType.LEFTOVER, 1, 5, 1.0)
        self.pantry.add_item(item1)
        self.pantry.add_item(item2)
        self.pantry.step(StrictStrategy())  # Both items should be discarded by strategy.

        # Ensure the total discarded matches the total added to the pantry.
        total_discarded = sum(self.pantry.waste_log['strategy_discards'][1].values()) + sum(
            self.pantry.waste_log['expired_discards'][1].values())
        self.assertEqual(total_discarded, item1.quantity + item2.quantity)

    def test_inventory_is_correct_after_discards(self):
        ##  This test ensures that after items are discarded, they are no longer included in
        # the pantry's inventory count for their respective food types.
        item1 = FoodItem("PerishableItem5", FoodType.PERISHABLE, 1, 5, 1.0)
        item2 = FoodItem("LeftoverItem4", FoodType.LEFTOVER, 1, 5, 1.0)
        self.pantry.add_item(item1)
        self.pantry.add_item(item2)

        # Use the strict strategy to discard items past their best-before date.
        self.pantry.step(StrictStrategy())

        # Ensure the items are removed from the pantry's inventory.
        self.assertEqual(self.pantry.get_total_by_type(FoodType.PERISHABLE), 0)
        self.assertEqual(self.pantry.get_total_by_type(FoodType.LEFTOVER), 0)
        self.assertEqual(self.pantry.get_total(), 0)



if __name__ == '__main__':
    unittest.main()