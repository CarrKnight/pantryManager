import unittest

from simulation import Pantry, FoodItem, RandomConsumptionStrategy, Meal, FoodType, MixedConsumptionStrategy


class TestStrategies(unittest.TestCase):

    def setUp(self):
        # Preparing a pantry for each test.
        self.pantry = Pantry()

        # A few food items for testing purposes.
        self.bread = FoodItem("Bread", FoodType.PERISHABLE, best_before=3, spoilage_date=5, quantity=0.5)
        self.rice = FoodItem("Rice", FoodType.NON_PERISHABLE, 365, 730, 1.0)
        self.pizza = FoodItem("Pizza", FoodType.LEFTOVER, 2, 3, 0.25)

        # Toss 'em in the pantry.
        self.pantry.add_item(self.bread)
        self.pantry.add_item(self.rice)
        self.pantry.add_item(self.pizza)

    def test_random_strategy(self):
        """Let's see if our random strategy really picks food."""
        strategy = RandomConsumptionStrategy()
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.PERISHABLE: 0.3})
        foods_eaten = meal.consume(strategy)

        # Basically, we wanna see if our random strategy actually consumed something.
        self.assertTrue(len(foods_eaten) > 0)

    def test_random_strategy_multiple(self):
        """Can our random strategy handle eating a lot?"""
        strategy = RandomConsumptionStrategy()
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.PERISHABLE: 0.5})
        foods_eaten = meal.consume(strategy)

        # We're mainly checkin' if the function does its job.
        # That is, returns a list of dicts with FoodItems.
        self.assertTrue(len(foods_eaten) > 0)

    def test_random_strategy_empty(self):
        """What if we don't wanna eat anything?"""
        strategy = RandomConsumptionStrategy()
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.PERISHABLE: 0})
        foods_eaten = meal.consume(strategy)

        # If we said we ain't hungry, we shouldn't have any food to eat.
        self.assertEqual(len(foods_eaten), 0)

    def test_mixed_strategy_fifo(self):
        """Testing the FIFO part of the mixed strategy."""
        strategy = MixedConsumptionStrategy(1.0)  # Always use FIFO.
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.LEFTOVER: 0.2})
        foods_eaten = meal.consume(strategy)

        # We're checking that our only leftover, pizza, was eaten first.
        foods_eaten = [d[0] for d in foods_eaten]

        self.assertTrue(any(food for food in foods_eaten if food == self.pizza))

    def test_mixed_strategy_random(self):
        """Testing the random part of the mixed strategy."""
        strategy = MixedConsumptionStrategy(0.0)  # Always go random.
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.NON_PERISHABLE: 0.8})
        foods_eaten = meal.consume(strategy)

        # The only non-perishable here is rice, so we should've definitely eaten some of it.
        foods_eaten = [d[0] for d in foods_eaten]

        self.assertTrue(any(food for food in foods_eaten if food == self.rice))

    def test_mixed_strategy_mixed(self):
        """Let's make the mixed strategy really mixed up."""
        strategy = MixedConsumptionStrategy(0.5)  # 50-50 shot.
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.PERISHABLE: 0.4, FoodType.LEFTOVER: 0.2})
        foods_eaten = meal.consume(strategy)

        # We've set our meal to eat both perishables and leftovers.
        # So we should've eaten a bit of both.
        foods_eaten = [d[0] for d in foods_eaten]

        self.assertTrue(any(food for food in foods_eaten if food == self.bread))
        self.assertTrue(any(food for food in foods_eaten if food == self.pizza))

