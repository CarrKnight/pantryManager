import unittest
from simulation import  *

# Assuming you've already imported everything necessary at the beginning of your test file.

class TestOrderPolicyWithPantryAdjustment(unittest.TestCase):

    def setUp(self):
        self.household = Household(adults=2, children=2, income_percentile=0.6)

    def test_fixed_consumption_policy_with_pantry(self):
        policy = FixedConsumptionPolicy(daily_consumption_perishable=1.0, daily_consumption_non_perishable=0.5,
                                        frequency=7, safety_stock_perishable=1.0,
                                        safety_stock_non_perishable=1.0)

        # Simulate some items already in pantry
        self.household.pantry.add_item(FoodItem("test1",FoodType.PERISHABLE, 100,100,3.0))
        self.household.pantry.add_item(FoodItem("test2",FoodType.NON_PERISHABLE,100,100,2.0))

        order_quantity_perishable, order_quantity_non_perishable = policy.determine_order_quantity(self.household)

        self.assertEqual(order_quantity_perishable, 8.0 - 3.0)  # 8.0 (order without pantry) - 3.0 (in pantry)
        self.assertEqual(order_quantity_non_perishable, 4.5 - 2.0)  # 4.5 (order without pantry) - 2.0 (in pantry)

    def test_historical_consumption_policy_with_pantry(self):
        base_policy = FixedConsumptionPolicy(daily_consumption_perishable=1.0, daily_consumption_non_perishable=0.5,
                                             frequency=7, safety_stock_perishable=1.0,
                                             safety_stock_non_perishable=1.0)
        policy = HistoricalConsumptionPolicy(base_policy)

        # Simulate 14 days of consumption with 0.9 for perishable and 0.4 for non-perishable daily.
        for i in range(14):
            self.household.history.append({
                "daily_consumption": {
                    FoodType.PERISHABLE: 0.9,
                    FoodType.NON_PERISHABLE: 0.4
                }
            })

        # Simulate some items already in pantry
        self.household.pantry.add_item(FoodItem("test1",FoodType.PERISHABLE, 100,100,2.0))
        self.household.pantry.add_item(FoodItem("test2",FoodType.NON_PERISHABLE,100,100,1.0))


        order_quantity_perishable, order_quantity_non_perishable = policy.determine_order_quantity(self.household)

        self.assertAlmostEqual(order_quantity_perishable, 7.3 - 2.0,
                               places=1)  # 7.3 (order without pantry) - 2.0 (in pantry)
        self.assertAlmostEqual(order_quantity_non_perishable, 3.8 - 1.0,
                               places=1)  # 3.8 (order without pantry) - 1.0 (in pantry)