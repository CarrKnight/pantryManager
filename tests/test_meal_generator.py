import unittest
import random

from simulation import Household, StandardMealGenerator, PlannedMeal


class TestStandardMealGenerator(unittest.TestCase):

    def setUp(self):
        """Set up a standard household and generator for testing."""
        self.household = Household(adults=2, children=2, income_percentile=1)
        self.generator = StandardMealGenerator(meals_at_home_ratio=0.8)

    def test_weekly_meal_structure(self):
        """Test if planned meals are generated for each day of the week."""
        weekly_meals = self.generator.generate_weekly_meals(self.household)

        self.assertEqual(len(weekly_meals), 7)  # One list of meals for each day of the week
        for day_meals in weekly_meals:
            self.assertGreaterEqual(len(day_meals), 0)
            self.assertLessEqual(len(day_meals), 3)  # Max 3 meals a day: breakfast, lunch, dinner

    def test_planned_meal_content(self):
        """Test if each planned meal has a defined total grams."""
        weekly_meals = self.generator.generate_weekly_meals(self.household)

        for day_meals in weekly_meals:
            for meal in day_meals:
                self.assertTrue(isinstance(meal, PlannedMeal))
                self.assertGreater(meal.total_grams, 0)

    def test_meal_generator_ratio(self):
        """Test if meals are generated approximately in line with the meals_at_home_ratio."""
        # Note: This test can still fail due to randomness, but over a large sample, it should be mostly accurate.
        generator_high_ratio = StandardMealGenerator(meals_at_home_ratio=1)
        generator_low_ratio = StandardMealGenerator(meals_at_home_ratio=0)

        weekly_meals_high_ratio = generator_high_ratio.generate_weekly_meals(self.household)
        weekly_meals_low_ratio = generator_low_ratio.generate_weekly_meals(self.household)

        # Assuming meals are always at home for high ratio
        for day_meals in weekly_meals_high_ratio:
            self.assertEqual(len(day_meals), 3)  # All three meals

        # Assuming meals are never at home for low ratio
        for day_meals in weekly_meals_low_ratio:
            self.assertEqual(len(day_meals), 0)  # No meals at home
