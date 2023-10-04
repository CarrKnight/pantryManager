import unittest
from simulation import StandardMealGenerator, ProportionalConsumptionStrategy, FoodType, FoodItem, Household, \
    FixedConsumptionPolicy, GroceryStore, AdaptiveOrderPolicy


class TestAdaptiveOrderPolicy(unittest.TestCase):

    def setUp(self):
        self.base_policy = FixedConsumptionPolicy(daily_consumption_perishable=1800, daily_consumption_non_perishable=1800,
                                                  frequency=7, safety_stock_perishable=1800,
                                                  safety_stock_non_perishable=1800)
        self.household = Household(
            adults=1,
            children=0,
            income_percentile=0.5,
            meal_generator=StandardMealGenerator(1),
            meal_planning_strategy=ProportionalConsumptionStrategy(0.5),
            order_policy=AdaptiveOrderPolicy(self.base_policy),
            ## I'm assuming grocery_store would be similar, so reusing it here.
            grocery_store=GroceryStore(best_before_params={
                FoodType.PERISHABLE: (30, 1),
                FoodType.NON_PERISHABLE: (50, 10),
            }, spoilage_date_params={
                FoodType.PERISHABLE: (50, 2),
                FoodType.NON_PERISHABLE: (100, 20),
            })
        )

    def test_adaptive_order_consistent_consumption(self):
        self.household.pantry.add_item(FoodItem("starter",FoodType.NON_PERISHABLE,7,7,10000))
        self.household.pantry.add_item(FoodItem("starter",FoodType.PERISHABLE,7,7,10000))
        # Simulate consistent consumption for 7 days
        self.household.start_of_week()
        for _ in range(7):
            self.household.daily_step()
        self.household.pantry.reset()

        perishable_order, non_perishable_order = self.household.order_policy.determine_order_quantity(self.household)

        # For consistent consumption, the order quantities should closely match the base policy
        self.assertAlmostEqual(perishable_order, self.household.order_policy.daily_consumption_perishable * 7 +
                               self.household.order_policy.safety_stock_perishable, delta=0.1)
        self.assertAlmostEqual(non_perishable_order, self.household.order_policy.daily_consumption_non_perishable * 7 +
                               self.household.order_policy.safety_stock_non_perishable, delta=0.1)

    def test_adaptive_order_varying_consumption(self):
        # Simulate varying consumption: for simplicity, let's alternate between 1500g and 2100g daily
        for _ in range(7):
            if _ % 2 == 0:
                perishable_consumed = 1500
                non_perishable_consumed = 1500
            else:
                perishable_consumed = 2100
                non_perishable_consumed = 2100

            daily_record = {
                "meals_eaten_today": 0,  # Assuming no meals eaten directly for this test
                "daily_consumption": {
                    FoodType.PERISHABLE: perishable_consumed,
                    FoodType.NON_PERISHABLE: non_perishable_consumed
                },
                "emergency_takeouts": 0,  # Assuming no emergency takeouts for this test
                "total_perishable_bought": 0,  # No purchase in this step
                "total_nonperishable_bought": 0  # No purchase in this step
            }
            self.household.history.append(daily_record)
        perishable_order, non_perishable_order = self.household.order_policy.determine_order_quantity(self.household)

        # We expect the order quantities to be different than the base policy due to variations
        self.assertNotEqual(perishable_order, self.base_policy.daily_consumption_perishable * 7 + self.base_policy.safety_stock_perishable)
        self.assertNotEqual(non_perishable_order, self.base_policy.daily_consumption_non_perishable * 7 + self.base_policy.safety_stock_non_perishable)

    def tearDown(self):
        del self.household
        del self.base_policy