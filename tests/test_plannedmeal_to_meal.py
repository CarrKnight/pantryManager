import unittest

from simulation import Pantry, FoodItem, Household, FreshFirstStrategy, PlannedMeal, ProportionalConsumptionStrategy, \
    FoodType


class TestMealPlanningStrategies(unittest.TestCase):

    def setUp(self):
        # Let's set up a basic pantry and household for the tests
        self.pantry = Pantry()
        # Assume the pantry has 300g leftovers, 500g perishables, and 200g non-perishables.
        self.pantry.add_item(FoodItem("Leftover Pizza", FoodType.LEFTOVER, 1, 3, 300))
        self.pantry.add_item(FoodItem("Fresh Salad", FoodType.PERISHABLE, 1, 3, 500))
        self.pantry.add_item(FoodItem("Canned Beans", FoodType.NON_PERISHABLE, 365, 365, 200))

        self.household = Household(adults=2, children=1,income_percentile=0.5)

    def test_fresh_first_strategy(self):
        strategy = FreshFirstStrategy()
        planned_meal = PlannedMeal(500)  # 500 grams planned consumption
        meal = strategy.plan_meal(planned_meal, self.household, self.pantry)

        # Check if the meal prioritizes leftovers, then perishables, then non-perishables
        self.assertEqual(meal.consumption_patterns[FoodType.LEFTOVER], 300)  # All leftovers
        self.assertEqual(meal.consumption_patterns[FoodType.PERISHABLE], 200)  # The remaining amount from perishables
        self.assertEqual(meal.consumption_patterns[FoodType.NON_PERISHABLE], 0)  # No non-perishables consumed

    def test_proportional_consumption_strategy(self):
        strategy = ProportionalConsumptionStrategy(0.7)
        planned_meal = PlannedMeal(500)  # 500 grams planned consumption
        meal = strategy.plan_meal(planned_meal, self.household, self.pantry)

        # Check if the meal prioritizes leftovers, then tries to maintain proportion
        self.assertEqual(meal.consumption_patterns[FoodType.LEFTOVER], 300)  # All leftovers
        # 140 is 70% of remaining 200 grams
        self.assertEqual(meal.consumption_patterns[FoodType.PERISHABLE], 140)
        # 60 is 30% of remaining 200 grams
        self.assertEqual(meal.consumption_patterns[FoodType.NON_PERISHABLE], 60)

