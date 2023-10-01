import unittest

from simulation import FoodType, Pantry, FoodItem, RandomConsumptionStrategy, Meal


class TestRandomization(unittest.TestCase):

    def setUp(self):
        # Start with a fresh pantry for each test.
        self.pantry = Pantry()

        # Load it up with three non-perishables with the same spoil dates but different quantities.
        self.rice_small = FoodItem("Small Rice", FoodType.NON_PERISHABLE, 365, 730, 0.7)
        self.rice_medium = FoodItem("Medium Rice", FoodType.NON_PERISHABLE, 365, 730, 1.0)
        self.rice_large = FoodItem("Large Rice", FoodType.NON_PERISHABLE, 365, 730, 1.5)

        self.rice_small.original_quantity=self.rice_small.quantity
        self.rice_medium.original_quantity=self.rice_medium.quantity
        self.rice_large.original_quantity=self.rice_large.quantity

        # Toss 'em in.
        self.pantry.add_item(self.rice_small)
        self.pantry.add_item(self.rice_medium)
        self.pantry.add_item(self.rice_large)

    def test_random_vs_fifo(self):
        """Check if the random strategy really is random."""

        # Track how many times each item was chosen first.
        first_pick_counts = {self.rice_small: 0, self.rice_medium: 0, self.rice_large: 0}

        # Let's run our random strategy a bunch of times to see if there's any pattern.
        for _ in range(1000):  # Run it 1000 times for good measure.
            strategy = RandomConsumptionStrategy()
            meal = Meal(self.pantry)
            meal.set_consumption_patterns({FoodType.NON_PERISHABLE: 0.6})
            foods_eaten = meal.consume(strategy)

            # See which of our three rice bags was eaten first.
            first_food_eaten = next(iter(foods_eaten[0]))
            first_pick_counts[first_food_eaten] += 1

            # Reset the pantry to its original state for the next loop.
            for food in [self.rice_small, self.rice_medium, self.rice_large]:
                food.quantity = food.original_quantity

        # Now let's check if each type of rice was picked a reasonable number of times.
        # If one rice type is overwhelmingly chosen, we'd suspect it ain't random.
        # But if they're all in the ballpark, looks like our strategy is behaving.
        self.assertTrue(200 < first_pick_counts[self.rice_small] < 800)  # Expecting something in this range.
        self.assertTrue(200 < first_pick_counts[self.rice_medium] < 800)
        self.assertTrue(200 < first_pick_counts[self.rice_large] < 800)


    def test_you_eat_multiple_correctly(self):
        strategy = RandomConsumptionStrategy()
        meal = Meal(self.pantry)
        meal.set_consumption_patterns({FoodType.NON_PERISHABLE: 2.6})
        foods_eaten = meal.consume(strategy)

        foods_eaten = [d[0] for d in foods_eaten]
        self.assertTrue(self.rice_small in foods_eaten)

