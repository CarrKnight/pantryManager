import unittest

from simulation import Pantry, FoodItem, FoodType, Meal, StrictStrategy, BasicConsumptionStrategy


class TestMeal(unittest.TestCase):

    def setUp(self):
        # Set up a fresh pantry before each test.
        self.pantry = Pantry()

        # Toss a few food items in there.
        self.pasta = FoodItem("Pasta", FoodType.NON_PERISHABLE, 365, 730, 1.0)  # 1kg of pasta.
        self.chicken = FoodItem("Chicken", FoodType.PERISHABLE, 3, 5, 0.5)  # Half a kilo of chicken.
        self.pizza = FoodItem("Pizza", FoodType.LEFTOVER, 2, 3, 0.25)  # Quarter kilo of leftover pizza.

        self.pantry.add_item(self.pasta)
        self.pantry.add_item(self.chicken)
        self.pantry.add_item(self.pizza)

    def test_consumption_pattern_set(self):
        """Check if we're setting up consumption patterns right."""
        meal = Meal(self.pantry)
        patterns = {FoodType.LEFTOVER: 0.1, FoodType.PERISHABLE: 0.3, FoodType.NON_PERISHABLE: 0.05}
        returned_patterns = meal.set_consumption_patterns(patterns)

        self.assertEqual(patterns, returned_patterns)

    def test_choose_food_to_eat(self):
        """See if we're picking the right grub from the pantry."""
        meal = Meal(self.pantry)
        patterns = {FoodType.LEFTOVER: 0.1, FoodType.PERISHABLE: 0.3, FoodType.NON_PERISHABLE: 0.05}
        meal.set_consumption_patterns(patterns)
        foods_to_eat = meal.choose_food_to_eat(BasicConsumptionStrategy())

        # Since this is a bit random, we're mainly checking if the function does its job.
        # That is, returns a list of FoodItems.
        self.assertTrue(len(foods_to_eat) == 3)

    def test_consume_food(self):
        """Time to eat and see if the quantities drop."""
        meal = Meal(self.pantry)
        patterns = {FoodType.LEFTOVER: 0.1, FoodType.PERISHABLE: 0.3, FoodType.NON_PERISHABLE: 0.05}
        meal.set_consumption_patterns(patterns)
        meal.consume()

        # Here's a basic check. After consumption, total pantry weight should drop.
        self.assertLess(self.pantry.get_total(), 1.75)  # 1.75kg is the total weight before any consumption.

    def test_full_consumption_removal(self):
        """If we eat everything of a type, it should be gone from the pantry."""
        meal = Meal(self.pantry)
        # Let's say we're super hungry for leftovers.
        patterns = {FoodType.LEFTOVER: 1, FoodType.PERISHABLE: 0.3, FoodType.NON_PERISHABLE: 0.05}
        meal.set_consumption_patterns(patterns)
        meal.consume()

        # We said we're gonna eat 1kg of leftovers, and we only have 0.25kg pizza.
        # So, after the meal, there should be no pizza left in the pantry.
        self.pantry.step(StrictStrategy())
        leftovers_in_pantry = any(item.food_type == FoodType.LEFTOVER for item in self.pantry.items_by_type[FoodType.LEFTOVER])
        self.assertFalse(leftovers_in_pantry)


if __name__ == "__main__":
    unittest.main()