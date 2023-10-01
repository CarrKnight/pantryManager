import unittest
from src.simulation import FoodItem, FoodType


class TestFoodItem(unittest.TestCase):

    def test_initialization(self):  # Define a test method for initialization
        # Create a FoodItem object
        food = FoodItem(name="Banana", food_type=FoodType.PERISHABLE, spoilage_date=7, best_before=7, quantity=1.5)

        # Assert that the FoodItem attributes are set correctly
        self.assertEqual(food.name, "Banana")
        self.assertEqual(food.food_type, FoodType.PERISHABLE)
        self.assertEqual(food.spoilage_date, 7)
        self.assertEqual(food.quantity, 1.5)

    def test_consume(self):  # Define a test method for consumption
        # Create another FoodItem object
        food = FoodItem(name="Banana", food_type=FoodType.PERISHABLE, spoilage_date=7, best_before=7, quantity=1.5)

        # Consume some of the food
        food.consume(0.5)

        # Assert that the quantity was reduced correctly
        self.assertEqual(food.quantity, 1.0)

        # Try to consume more than the available quantity and assert that it raises a ValueError
        with self.assertRaises(ValueError):
            food.consume(2.0)

    def test_expiration(self):  # Define a test method for expiration
        # Create a FoodItem object
        food = FoodItem(name="Banana", food_type=FoodType.PERISHABLE,
                        spoilage_date=8,best_before=2,
                        quantity=1.5)

        # Simulate days passing until the expiration day
        for _ in range(7):
            food.day_passes()

        # Assert that the food has not yet expired
        self.assertFalse(food.is_expired())

        # Simulate one more day passing
        food.day_passes()

        # Assert that the food is now expired
        self.assertTrue(food.is_expired())

    def setUp(self):
        # Set up a sample FoodItem for testing. This will be done before each test method is run.
        self.item = FoodItem(name="Apple", food_type=FoodType.PERISHABLE, best_before=5, spoilage_date=10, quantity=1.0)

    def test_consume2(self):
        # Consume part of the food item and check if quantity updates correctly.
        self.item.consume(0.5)
        self.assertEqual(self.item.quantity, 0.5)

    def test_overconsume_raises_exception(self):
        # Ensure that trying to consume more than available raises an error.
        with self.assertRaises(ValueError):
            self.item.consume(1.5)

    def test_day_passes(self):
        # Check if the day_passes method decrements the best_before and spoilage_date values correctly.
        self.item.day_passes()
        self.assertEqual(self.item.best_before, 4)
        self.assertEqual(self.item.spoilage_date, 9)

    def test_is_past_best_before_false(self):
        # Ensure the item isn't identified as past its best before date prematurely.
        self.assertFalse(self.item.is_past_best_before())

    def test_is_past_best_before_true(self):
        # Make enough days pass to go beyond the best before date and check the result.
        for _ in range(5):
            self.item.day_passes()
        self.assertTrue(self.item.is_past_best_before())

    def test_is_expired_false(self):
        # Ensure the item isn't identified as expired prematurely.
        self.assertFalse(self.item.is_expired())

    def test_is_expired_true(self):
        # Make enough days pass to go beyond the spoilage date and check if the item is identified as expired.
        for _ in range(10):
            self.item.day_passes()
        self.assertTrue(self.item.is_expired())

if __name__ == "__main__":
    unittest.main()
