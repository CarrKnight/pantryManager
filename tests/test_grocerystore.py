import unittest

from simulation import GroceryStore, FoodType


class TestGroceryStore(unittest.TestCase):

    def setUp(self):
        self.store = GroceryStore(
            best_before_params={
                FoodType.PERISHABLE: (3, 1),
                FoodType.NON_PERISHABLE: (50, 10),
            },
            spoilage_date_params={
                FoodType.PERISHABLE: (5, 2),
                FoodType.NON_PERISHABLE: (100, 20),
            }
        )

    def test_order_quantity(self):
        """Check if the total quantity of the order matches the request."""
        order = self.store.get_order(FoodType.PERISHABLE, 2000)
        self.assertEqual(sum(item.quantity for item in order), 2000)

    def test_non_perishable_dates(self):
        """Check if the non-perishable dates are in the expected range."""
        order = self.store.get_order(FoodType.NON_PERISHABLE, 2000)
        for item in order:
            self.assertGreaterEqual(item.best_before, 20)
            self.assertLessEqual(item.best_before, 80)
            self.assertGreaterEqual(item.spoilage_date, 40)
            self.assertLessEqual(item.spoilage_date, 160)

    def test_perishable_dates(self):
        """Check if the perishable dates are in the expected range."""
        order = self.store.get_order(FoodType.PERISHABLE, 2000)
        for item in order:
            self.assertGreaterEqual(item.best_before, 0.1)
            self.assertLessEqual(item.best_before, 6)
            self.assertGreaterEqual(item.spoilage_date, 1)
            self.assertLessEqual(item.spoilage_date, 11)

