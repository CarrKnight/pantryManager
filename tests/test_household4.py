import unittest
from simulation import StandardMealGenerator, ProportionalConsumptionStrategy, FoodType, FoodItem, Household, \
    FixedConsumptionPolicy, GroceryStore


class TestHouseholdOrderAndConsume(unittest.TestCase):

    def setUp(self):
        # Setting up the basic params and objects
        self.household = Household(
            adults=1,
            children=0,
            income_percentile=0.5,
            meal_generator=StandardMealGenerator(1),
            order_policy=FixedConsumptionPolicy(daily_consumption_perishable=1800, daily_consumption_non_perishable=1800,
                                                frequency=7, safety_stock_perishable=1800,
                                                safety_stock_non_perishable=1800),
            ## do not worry about
            grocery_store=GroceryStore(best_before_params={
                FoodType.PERISHABLE: (30, 1),
                FoodType.NON_PERISHABLE: (50, 10),
                }, spoilage_date_params={
                FoodType.PERISHABLE: (50, 2),
                FoodType.NON_PERISHABLE: (100, 20),
                })
        )

    def test_order_and_consume(self):
        # At the start, the pantry should be empty
        initial_total_food = self.household.get_total_food()
        self.assertEqual(initial_total_food, 0)

        # After 7 days, the household should place an order
        self.household.start_of_week()
        for _ in range(7):
            self.household.daily_step()

        # Check if the pantry has food now after 7 days
        total_food_after_week = self.household.get_total_food()
        self.assertGreater(total_food_after_week, 0)


        ## you will have consumed only emergency takeouts....
        total_consumed = sum([day["emergency_takeouts"] for day in self.household.history])
        self.assertAlmostEqual(total_consumed, 7 * 1600, delta=0.1)

        ## but if I step it again for 6 days, I should be able to eat more real food...
        self.household.start_of_week()
        for _ in range(7):
            self.household.daily_step()
        total_consumed = sum([day["emergency_takeouts"] for day in self.household.history[7:]])
        self.assertAlmostEqual(total_consumed, 0, delta=0.1)

        # Check if the total food consumed in the week is approximately equal to 7 * 1800g
        total_consumed = sum([day["daily_consumption"][FoodType.PERISHABLE] for day in self.household.history[7:]])
        self.assertAlmostEqual(total_consumed, 7 * 1600, delta=0.1)

    def tearDown(self):
        del self.household

if __name__ == '__main__':
    unittest.main()
