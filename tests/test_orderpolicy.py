import unittest

from simulation import Household, FixedConsumptionPolicy, HistoricalConsumptionPolicy, FoodType


class TestOrderPolicy(unittest.TestCase):

    def setUp(self):
        self.household = Household(adults=2, children=2, income_percentile=0.6)

    def test_fixed_consumption_policy(self):
        policy = FixedConsumptionPolicy(daily_consumption_perishable=1.0, daily_consumption_non_perishable=0.5,
                                        frequency=7, safety_stock_perishable=1.0,
                                        safety_stock_non_perishable=1.0)

        order_quantity_perishable, order_quantity_non_perishable = policy.determine_order_quantity(self.household)

        self.assertEqual(order_quantity_perishable, 8.0)
        self.assertEqual(order_quantity_non_perishable, 4.5)

    def test_historical_consumption_policy(self):
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

        order_quantity_perishable, order_quantity_non_perishable = policy.determine_order_quantity(self.household)

        self.assertAlmostEqual(order_quantity_perishable, 7.3, places=1)  # 0.9*7 + 1(ss)
        self.assertAlmostEqual(order_quantity_non_perishable, 3.8, places=1)  # 0.4*7 + 1(ss)

