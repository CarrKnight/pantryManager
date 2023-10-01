import unittest

from simulation import Household, FoodItem, FoodType, StandardMealGenerator


class TestHousehold(unittest.TestCase):

    def setUp(self):
        self.household = Household(adults=2, children=1, income_percentile=0.6)
        self.household.meal_generator = StandardMealGenerator(1.0)

        # Adding some items to pantry
        self.bread = FoodItem("Bread", FoodType.PERISHABLE, best_before=3, spoilage_date=5, quantity=0.5)
        self.cookies = FoodItem("Cookies", FoodType.NON_PERISHABLE, best_before=15, spoilage_date=20, quantity=0.3)
        self.leftover_pizza = FoodItem("Pizza", FoodType.LEFTOVER, best_before=2, spoilage_date=3, quantity=0.4)

        self.household.pantry.add_item(self.bread)
        self.household.pantry.add_item(self.cookies)
        self.household.pantry.add_item(self.leftover_pizza)

    def test_start_of_week(self):
        """Test the start_of_week method."""
        self.household.start_of_week()
        self.assertIsNotNone(self.household.weekly_meals)  # Ensures weekly meals are generated
        self.assertEqual(len(self.household.weekly_meals), 7)  # Ensure there are 7 days' worth of meals

    def test_daily_step(self):
        """Test the daily_step method."""
        self.household.start_of_week()

        # Mock pantry's initial state.
        initial_pantry_total = self.household.get_total_food()
        self.assertGreater(initial_pantry_total,0)
        self.household.daily_step()

        # One day's meals should be consumed.
        self.assertEqual(len(self.household.weekly_meals), 6)

        # Ensure pantry quantity has decreased due to consumption.
        self.assertTrue(self.household.get_total_food() < initial_pantry_total)
        ## there really shouldn't be enough to feed yourself...

        
        # Ensure that waste log is updated (assuming the Pantry's step method updates it daily).
##        self.assertIn(1, self.household.get_waste_log())  # Checking if day 1 exists in waste log

    def tearDown(self):
        del self.household


