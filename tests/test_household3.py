import unittest

from simulation import StandardMealGenerator, ProportionalConsumptionStrategy, FoodType, FoodItem, Household


class TestHousehold(unittest.TestCase):

    def setUp(self):
        # Set up a household with 2 adults, no children, and certain strategies
        self.household = Household(2, 0, 0.5,
                                   meal_generator=StandardMealGenerator(1.0),
                                   meal_planning_strategy=ProportionalConsumptionStrategy(0.5))

        # Add 100kg of perishable and non-perishable items to the pantry
        self.cookies = FoodItem("Cookies", FoodType.NON_PERISHABLE, best_before=15, spoilage_date=20,
                                quantity=100 * 1000)
        self.vegetables = FoodItem("Vegetables", FoodType.PERISHABLE, best_before=3, spoilage_date=5,
                                   quantity=100 * 1000)

        self.household.pantry.add_item(self.cookies)
        self.household.pantry.add_item(self.vegetables)
        self.household.start_of_week()

    def test_multiple_days(self):
        days_simulated = 0
        print("Perishables remaining:", self.household.pantry.get_total_by_type(FoodType.PERISHABLE))

        # Simulate days until the perishables expire
        while True :
            consumption_record = self.household.daily_step()
            days_simulated += 1
            if self.vegetables.is_expired():
                break
            # Ensure the number of meals eaten each day
            self.assertEqual(consumption_record["meals_eaten_today"], 3)

            # For this simple test, we're not checking consumption amounts on each day
            # but you can add more detailed assertions if necessary.
            print("Perishables remaining:", self.household.pantry.get_total_by_type(FoodType.PERISHABLE))

            # Ensure there is more than 0 left...
            self.assertGreater(self.household.pantry.get_total_by_type(FoodType.PERISHABLE), 0)


        # At this point, vegetables should be expired
        self.assertTrue(self.vegetables.is_expired())

        # Depending on the consumption rate and meal patterns, you might want to check
        # the remaining quantities of perishables and non-perishables
        print("Days simulated:", days_simulated)
        self.assertTrue(days_simulated==5)
        print("Perishables remaining:", self.household.pantry.get_total_by_type(FoodType.PERISHABLE))
        self.assertEqual(self.household.pantry.get_total_by_type(FoodType.PERISHABLE), 0)
        print("Non-perishables remaining:", self.household.pantry.get_total_by_type(FoodType.NON_PERISHABLE))
        self.assertGreater(self.household.pantry.get_total_by_type(FoodType.NON_PERISHABLE), 0)


if __name__ == "__main__":
    unittest.main()