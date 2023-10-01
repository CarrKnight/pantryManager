import unittest

from simulation import Pantry, FoodItem, Meal, FoodType


class TestMeal(unittest.TestCase):

    def setUp(self):
        # Set up a fresh pantry before each test.
        self.pantry = Pantry()

        # Toss a few food items in there.
        self.pasta = FoodItem("Pasta", FoodType.NON_PERISHABLE, 100, 200, 1.0)  # 1kg of pasta.
        self.rice = FoodItem("Rice", FoodType.NON_PERISHABLE, 300, 600, 0.8)  # 0.8kg of rice.
        self.chicken = FoodItem("Chicken", FoodType.PERISHABLE, 3, 5, 0.5)  # Half a kilo of chicken.
        self.beef = FoodItem("Beef", FoodType.PERISHABLE, 4, 7, 0.7)  # 0.7kg of beef.
        self.pizza = FoodItem("Pizza", FoodType.LEFTOVER, 2, 3, 0.25)  # Quarter kilo of leftover pizza.
        self.lasagna = FoodItem("Lasagna", FoodType.LEFTOVER, 1, 3, 0.3)  # 0.3kg of lasagna.

        self.pantry.add_item(self.pasta)
        self.pantry.add_item(self.rice)
        self.pantry.add_item(self.chicken)
        self.pantry.add_item(self.beef)
        self.pantry.add_item(self.pizza)
        self.pantry.add_item(self.lasagna)

    def test_consumption_pattern_set(self):
        """Make sure we're setting the consumption patterns right, you know?"""
        meal = Meal(self.pantry)
        patterns = {FoodType.LEFTOVER: 0.1, FoodType.PERISHABLE: 0.3, FoodType.NON_PERISHABLE: 0.05}
        returned_patterns = meal.set_consumption_patterns(patterns)

        self.assertEqual(patterns, returned_patterns)

    def test_fully_eat_multiple_items(self):
        """Let's see if we're eating everything of the same type when it's all in the menu."""
        meal = Meal(self.pantry)
        patterns = {FoodType.PERISHABLE: 1.5}  # This should clear both the chicken and beef out.
        meal.set_consumption_patterns(patterns)
        consumed = meal.consume()
        consumed_list = [d[0] for d in consumed]


        # Expecting chicken, beef, and maybe some emergency grub.
        self.assertIn(self.chicken, consumed_list)
        self.assertIn(self.beef, consumed_list)

        # Make sure they're really gone from the pantry.
        self.assertTrue(all(item.quantity == 0 for item in consumed_list if item.name != "Emergency Takeout"))

    def test_partially_eat_multiple_items(self):
        """What if we're not that hungry and we just nibble? Let's find out."""
        meal = Meal(self.pantry)
        patterns = {FoodType.NON_PERISHABLE: 1.2}  # We're eating all of the pasta but not all of the rice
        meal.set_consumption_patterns(patterns)
        consumed = meal.consume()
        consumed_list = [d[0] for d in consumed]

        # Expecting some pasta and rice.
        self.assertIn(self.pasta, consumed_list)
        self.assertIn(self.rice, consumed_list)

        # Make sure both were eaten
        self.assertTrue(self.pasta.quantity < 1.0)
        self.assertTrue(self.rice.quantity < 0.8)

        # Check we didn't eat 'em all.
        self.assertTrue(self.pasta.quantity == 0)
        self.assertTrue(self.rice.quantity > 0)