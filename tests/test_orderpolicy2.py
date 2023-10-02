import unittest
from simulation import FoodType, Household, OrderPolicy, FixedConsumptionPolicy, HistoricalConsumptionPolicy


class TestOrderPolicy(unittest.TestCase):

    def setUp(self):
        """Setup method to create necessary objects for our tests."""
        self.fixed_policy = FixedConsumptionPolicy(
            daily_consumption_perishable=1.0,
            daily_consumption_non_perishable=0.5,
            frequency=7,
            safety_stock_perishable=1.0,
            safety_stock_non_perishable=1.0
        )

    def test_decrement_and_reset(self):
        """Test that we can safely decrement and reset the 'days until next order' without impacting order outputs."""

        # Initial conditions check
        self.assertEqual(self.fixed_policy.days_until_next_order, 7)

        # Decrementing
        self.fixed_policy.decrement_days_until_next_order()
        self.assertEqual(self.fixed_policy.days_until_next_order, 6)

        # Resetting
        self.fixed_policy.reset_days_until_next_order()
        self.assertEqual(self.fixed_policy.days_until_next_order, 7)

        # Ensure this does not affect the order outputs
        household = Household(adults=2, children=1, income_percentile=0.5)
        quantity = self.fixed_policy.determine_order_quantity(household)
        self.assertEqual(quantity, (8.0, 4.5))  # Expected values based on initial setup

    def test_too_few_observations(self):
        """Test that the HistoricalConsumptionPolicy resorts to FixedConsumptionPolicy when observations are too few."""

        household = Household(adults=2, children=1, income_percentile=0.5)
        historical_policy = HistoricalConsumptionPolicy(self.fixed_policy)

        # With no observations in household history
        quantity = historical_policy.determine_order_quantity(household)
        self.assertEqual(quantity, (8.0, 4.5))  # Expected values based on initial setup

        # With 6 observations in household history (still less than 7)
        for _ in range(6):
            household.history.append({
                "daily_consumption": {
                    FoodType.PERISHABLE: 0.9,
                    FoodType.NON_PERISHABLE: 0.4
                }
            })
        quantity = historical_policy.determine_order_quantity(household)
        self.assertEqual(quantity, (8.0, 4.5))  # Expected values based on initial setup

    # You can further expand with more tests if you'd like.
