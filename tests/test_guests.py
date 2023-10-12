import unittest
from unittest.mock import patch, Mock

from simulation import *


class TestVariableMealGenerator(unittest.TestCase):

    def setUp(self):
        self.household = Household(adults=2, children=2,income_percentile=0.5)
        self.base_generator = StandardMealGenerator(meals_at_home_ratio=1.0)  # All meals at home for simplicity
        self.original_gauss = random.gauss
        self.original_random = random.random

    def tearDown(self):
        # Reset the original methods after each test
        random.gauss = self.original_gauss
        random.random = self.original_random

    def test_noise_only(self):
        # Mocking gaussian noise to always return 10% increase
        random.gauss = Mock(return_value=0.1)

        # We're only testing noise here, so let's make sure guests never arrive
        random.random = Mock(return_value=1.0)

        generator = VariableMealGenerator(self.base_generator, noise_std=0.1, guest_probability=0.0, max_guests=0)
        weekly_meals = generator.generate_weekly_meals(self.household)

        # Assuming first meal is breakfast, consumption for 2 adults + 2 kids should be
        # breakfast: 2*400 + 2*250 = 1300. With 10% noise: 1300*1.1 = 1430
        self.assertEqual(weekly_meals[0][0].total_grams, 1430)


    def test_guests_only(self):
        # Mocking gaussian noise to always return no noise
        random.gauss = Mock(return_value=0.0)

        # Mocking so that guests always arrive and maximum guests always come
        random.random = Mock(return_value=0)
        random.randint = Mock(return_value=3)

        generator = VariableMealGenerator(self.base_generator, noise_std=0.1, guest_probability=1.0, max_guests=3)
        weekly_meals = generator.generate_weekly_meals(self.household)

        # Assuming first meal is breakfast. Without guests: 2*400 + 2*250 = 1300.
        # With 3 guests: 1300 + 3*600 = 2500
        self.assertEqual(weekly_meals[0][0].total_grams, 3100)


    # Add more tests as needed for combinations of noise and guests or other scenarios
