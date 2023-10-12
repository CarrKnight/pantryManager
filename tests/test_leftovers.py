import unittest

from simulation import *


class TestPlateWasteCalculator(unittest.TestCase):

    def setUp(self):
        self.food_item_1 = FoodItem("Bread", FoodType.PERISHABLE, 5, 7, 1.0)  # 1 kg of Bread
        self.food_item_2 = FoodItem("Apple", FoodType.PERISHABLE, 3, 4, 0.5)  # 0.5 kg of Apple

    def test_plate_waste_percentage(self):
        calculator = FixedPercentageWasteCalculator(0.1)  # 10% of the food is wasted
        consumed_items = [(self.food_item_1, 0.5), (self.food_item_2, 0.3)]

        waste = calculator.compute_plate_waste(consumed_items)

        self.assertEqual(waste, [(self.food_item_1, 0.05), (self.food_item_2, 0.03)])

    def test_total_waste(self):
        calculator = FixedPercentageWasteCalculator(0.2)  # 20% of the food is wasted
        consumed_items = [(self.food_item_1, 1.0), (self.food_item_2, 0.5)]

        waste = calculator.compute_plate_waste(consumed_items)

        self.assertAlmostEqual(sum([item[1] for item in waste]), 0.3,places=4)


class TestPerishableLeftoversCalculator(unittest.TestCase):

    def setUp(self):
        self.food_item_1 = FoodItem("Bread", FoodType.PERISHABLE, 5, 7, 1.0)
        self.food_item_2 = FoodItem("Apple", FoodType.PERISHABLE, 3, 4, 0.5)

    def test_leftovers_after_waste(self):
        calculator = FixedPercentageLeftoverGenerator(0.2)  # 20% of uneaten food is leftover

        consumed_items = [(self.food_item_1, 0.7), (self.food_item_2, 0.4)]
        plate_waste = [(self.food_item_1, 0.1), (self.food_item_2, 0.05)]

        leftovers = calculator.compute_leftovers(consumed_items, plate_waste)

        self.assertAlmostEqual(leftovers, 0.22)  # No non-perishable leftovers



if __name__ == '__main__':
    unittest.main()