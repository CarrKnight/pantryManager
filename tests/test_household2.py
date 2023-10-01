import unittest

from simulation import StandardMealGenerator, ProportionalConsumptionStrategy, FoodType, FoodItem, Household


class TestHousehold(unittest.TestCase):

    def setUp(self):
        # Set up a household with 2 adults, no children, and certain strategies
        self.household = Household(2, 0, 0.5,
                                   meal_generator=StandardMealGenerator(1.0),
                                   meal_planning_strategy=ProportionalConsumptionStrategy(0.5))

        # Add 100kg of perishable and non-perishable items to the pantry
        cookies = FoodItem("Cookies", FoodType.NON_PERISHABLE, best_before=15, spoilage_date=20, quantity=100 * 1000)
        vegetables = FoodItem("Vegetables", FoodType.PERISHABLE, best_before=3, spoilage_date=5, quantity=100 * 1000)

        self.household.pantry.add_item(cookies)
        self.household.pantry.add_item(vegetables)
        self.household.start_of_week()

    def test_daily_step(self):
        # Take a daily step and record the consumption
        consumption_record = self.household.daily_step()

        # Assertions

        # As we've set the strategy to evenly consume perishables and non-perishables,
        # and given that there are 3 meals a day for 2 adults,
        # we should see a certain pattern in the consumption.
        # This will be based on the logic of your ProportionalConsumptionStrategy and the StandardMealGenerator.
        # Assuming each meal per adult is 1kg (this might vary based on your MealGenerator settings),
        # We should consume 1kg per meal per adult, half of it being perishable and the other half non-perishable.

        self.assertEqual(consumption_record["meals_eaten_today"], 3)
        self.assertEqual(consumption_record["daily_consumption"][FoodType.PERISHABLE], 1.6 * 1000)  # 1.5kg
        self.assertEqual(consumption_record["daily_consumption"][FoodType.NON_PERISHABLE], 1.6 * 1000)  # 1.5k

        self.assertEqual(self.household.pantry.get_total_by_type(FoodType.PERISHABLE),98400)
        self.assertEqual(self.household.pantry.get_total_by_type(FoodType.NON_PERISHABLE),98400)
        self.assertEqual(self.household.pantry.get_total_by_type(FoodType.LEFTOVER),0)


if __name__ == "__main__":
    unittest.main()