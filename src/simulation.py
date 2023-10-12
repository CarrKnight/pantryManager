import random
from enum import Enum
from statistics import mean
from typing import List, Dict, Tuple, Union

EMERGENCY_TAKEOUT = "Emergency Takeout"


class FoodType(Enum):
    LEFTOVER = "leftover"
    PERISHABLE = "perishable"
    NON_PERISHABLE = "non-perishable"


class FoodItem:
    def __init__(self, name: str, food_type: FoodType, best_before: int, spoilage_date: int, quantity: float):
        """
        Initialize a new FoodItem object.

        Args:
            name (str): Name of the food item.
            food_type (FoodType): Type of the food item (e.g., LEFTOVER, PERISHABLE, NON_PERISHABLE).
            best_before (int): Number of days until the food's best before date.
            spoilage_date (int): Number of days until the food spoils and becomes unsafe.
            quantity (float): Quantity of the food item in kg.
        """
        self.name = name
        self.food_type = food_type
        self.best_before = best_before
        self.spoilage_date = spoilage_date
        if best_before > spoilage_date:
            raise ValueError("Cannot have best before longer than spoilage date")
        self.quantity = quantity

    def consume(self, amount: float) -> None:
        """
        Consume a portion of the food item.

        Args:
            amount (float): The amount to consume in kg.

        Raises:
            ValueError: If the specified amount to consume is greater than the available quantity.
        """
        if amount > self.quantity:
            raise ValueError("Cannot consume more than the available quantity.")
        self.quantity -= amount

    def day_passes(self) -> None:
        """
        Simulate the passing of a day, decrementing the best before and spoilage dates.
        """
        if self.best_before > 0:
            self.best_before -= 1

        if self.spoilage_date > 0:
            self.spoilage_date -= 1

    def is_past_best_before(self) -> bool:
        """
        Check if the food item is past its best before date.

        Returns:
            bool: True if the food item is past its best before date, False otherwise.
        """
        return self.best_before <= 0

    def is_expired(self) -> bool:
        """
        Check if the food item is expired (past its spoilage date).

        Returns:
            bool: True if the food item is expired, False otherwise.
        """
        return self.spoilage_date <= 0

    def __str__(self) -> str:
        return f"Name: {self.name}, Food Type: {self.food_type.name}, Best Before: {self.best_before}"


from abc import ABC, abstractmethod


class PantryStrategy(ABC):  # This indicates that PantryStrategy is an abstract base class
    @abstractmethod
    def should_discard(self, item: FoodItem) -> bool:
        """
        Determine whether a given food item should be discarded.

        Parameters:
        - item (FoodItem): The food item to be checked.

        Returns:
        - bool: True if the item should be discarded, otherwise False.
        """
        pass  # This is just a placeholder. This method needs to be implemented in all subclasses.


class StrictStrategy(PantryStrategy):
    def should_discard(self, item: FoodItem) -> bool:
        """
        In the strict strategy, items past their best before date are discarded.

        Parameters:
        - item (FoodItem): The food item to be checked.

        Returns:
        - bool: True if the item is past its best before date, otherwise False.
        """
        return item.is_past_best_before()


class LaxStrategy(PantryStrategy):
    def should_discard(self, item: FoodItem) -> bool:
        """
        In the lax strategy, items are discarded only if they are expired.

        Parameters:
        - item (FoodItem): The food item to be checked.

        Returns:
        - bool: True if the item is expired, otherwise False.
        """
        return item.is_expired()


class Pantry:
    def __init__(self):
        """
              Initialize a new Pantry object.

              """
        self.items_by_type = {
            FoodType.LEFTOVER: [],
            FoodType.PERISHABLE: [],
            FoodType.NON_PERISHABLE: []
        }
        ## {type of waste: {day_number:{food_type: waste}}}
        self.waste_log: Dict[str, Dict[int, Dict[FoodType, float]]] = {
            'strategy_discards': {},  ## things we have chosen to discard
            'expired_discards': {}  ## things that have spoiled...
        }
        self.current_day: int = 0

    def add_item(self, item: FoodItem) -> None:
        """
        Add a food item to the pantry.

        Args:
            item (FoodItem): The food item to be added to the pantry.
        """
        self.items_by_type[item.food_type].append(item)
        # Sort by expiration date. Smallest (soonest to expire) first.
        self.items_by_type[item.food_type].sort(key=lambda x: x.spoilage_date)

    def step(self, strategy: PantryStrategy) -> None:
        """
        Simulate a day passing. Calls the day_passes() method on each food item,
        checks for expired items, and updates the waste log.
        """
        self.current_day += 1
        # Create two lists: one to track items that have expired, another to track items discarded by the strategy.
        expired_items = []
        strategy_discards = []
        empty_items = []  ## items that we have to throw away because they are finished and are just taking space in the pantry
        # We'll maintain a dict to track the weight of discarded items by type.
        weights_expired = {item_type: 0 for item_type in FoodType}
        weights_strategy_discarded = {item_type: 0 for item_type in FoodType}

        # Call day_passes for each item in the pantry
        for food_list in self.items_by_type.values():
            for item in food_list:
                # Decrement the expiration dates (best before and spoilage) of the food item.
                item.day_passes()
                if item.quantity <= 0.001:
                    empty_items.append(item)
                # Check if the item has passed its spoilage date and is now considered expired.
                elif item.is_expired():
                    expired_items.append(item)
                    # Directly update the weight of the expired item in the tracking dict.
                    weights_expired[item.food_type] += item.quantity
                # If the item isn't expired, use the provided strategy to decide if it should be discarded.
                elif strategy.should_discard(item):
                    strategy_discards.append(item)
                    # Directly update the weight of the strategy discarded item in the tracking dict.
                    weights_strategy_discarded[item.food_type] += item.quantity

        # Now, directly populate the waste_log using the tracking dicts without additional loops.
        self.waste_log['expired_discards'][self.current_day] = weights_expired
        self.waste_log['strategy_discards'][self.current_day] = weights_strategy_discarded

        # Finally, remove all the items (both expired and decided by strategy) from the pantry.
        # Iterate through each item in the combined list of expired and strategy discarded items.
        for item in expired_items + strategy_discards + empty_items:
            # Remove the item from the pantry's items list.
            self.items_by_type[item.food_type].remove(item)

    def get_total_by_type(self, food_type: FoodType) -> float:
        """
        Return the total weight in kg of a specified type of food in the pantry.

        Args:
            food_type (FoodType): The type of food (e.g., LEFTOVER, PERISHABLE, NON_PERISHABLE).

        Returns:
            float: The total weight in kg of the specified food type in the pantry.
        """
        return sum(item.quantity for item in self.items_by_type[food_type])

    def get_waste_log(self) -> Dict[str, Dict[int, Dict[FoodType, float]]]:
        """
        Return the waste log, showing the amount of food wasted each day, split by type.

        Returns:
            Dict[str, Dict[int, Dict[FoodType, float]]]: The waste log, split by type of waste(spoilage or thrown away) indexed by day and then by food type.
        """
        return self.waste_log

    def get_items_by_type(self, food_type: FoodType) -> List[FoodItem]:
        return self.items_by_type[food_type]

    def get_total(self):
        return sum(item.quantity for item_list in self.items_by_type.values() for item in item_list)

    def reset(self):
        self.items_by_type = {
            FoodType.LEFTOVER: [],
            FoodType.PERISHABLE: [],
            FoodType.NON_PERISHABLE: []
        }


class ConsumptionStrategy(ABC):
    """
    Abstract base class that defines the strategy for food consumption.

    When you wanna decide which food items from the pantry you're gonna eat,
    you might have a bunch of different ways to do it. This is the big picture,
    the blueprint if you will, for those strategies. Anything that subclasses
    this has gotta stick to the plan and implement the `select_food` method.
    """

    @abstractmethod
    def select_food(self, pantry: Pantry, food_type: FoodType, amount: float) -> List[Tuple[FoodItem, float]]:
        """
        Returns a list of food items (and their respective quantities) to be consumed.

        Args:
            pantry (Pantry): The pantry where we're grabbing our grub from.
            food_type (FoodType): The type of food (leftover, perishable, etc.) we're aiming to eat.
            amount (float): How much of this food type, by weight, we're planning to munch on.

        Returns:
            List[Dict[FoodItem, float]]: List of dicts. Each dict has a FoodItem as the key, and
                                         the weight of that item we're gonna eat as the value.
        """
        pass


class BasicConsumptionStrategy(ConsumptionStrategy):
    """
    A basic strategy for food consumption. It is effectively FIFO as long as the
    pantry is already sorted.

    We take what's there in the pantry for a given food type, and we consume it
    until we hit our target amount. No bells and whistles. If we're aiming to eat
    500g of leftovers, we just grab the leftovers in the order they're presented
    to us until we eat 500g.
    """

    def select_food(self, pantry: Pantry, food_type: FoodType, amount: float) -> List[Tuple[FoodItem, float]]:
        """
        Selects the food to consume based on the type and the desired amount.

        Args:
            pantry (Pantry): Where all the grub is stored.
            food_type (FoodType): The kind of food we wanna eat now.
            amount (float): The weight of food we're aiming to eat.

        Returns:
            List[Dict[FoodItem, float]]: The list of foods (and amounts) we've selected to eat.
        """
        foods_to_eat = []
        available_foods = pantry.get_items_by_type(food_type)  # Direct access, thanks to our pantry overhaul!

        # We're going down the list of available foods for this type...
        for food in available_foods:
            # If we've already picked enough food to hit our target, we stop.
            if amount <= 0:
                break

            # If the current food item has less weight than we still need to eat,
            # we eat all of it and adjust the remaining amount we need.
            if food.quantity <= amount:
                foods_to_eat.append((food, food.quantity))
                amount -= food.quantity
            else:
                # If this item has more weight than we still need,
                # we eat just a part of it and our target is reached.
                foods_to_eat.append((food, amount))
                amount = 0

        return foods_to_eat


class RandomConsumptionStrategy(ConsumptionStrategy):

    def select_food(self, pantry: Pantry, food_type: FoodType, amount: float) -> List[Tuple[FoodItem, float]]:
        """
        Randomly select food items from the pantry.

        Args:
            pantry (Pantry): The pantry from which we're selecting items.
            food_type (FoodType): The type of food we're lookin' for.
            amount (float): The amount of food we wanna eat.

        Returns:
            List[Dict[FoodItem, float]]: List of chosen food items and the quantity to eat.
        """

        # This list will store what we've decided to eat.
        foods_to_eat = []

        # Get all available food of the desired type.
        available_foods = pantry.get_items_by_type(food_type)

        # Keep looping till we've eaten enough or run outta options.
        while amount > 0 and available_foods:
            # Pick a random item from the list.
            food = random.choice(available_foods)

            # If there's less food than we wanna eat, we eat all of it.
            if food.quantity <= amount:
                foods_to_eat.append((food, food.quantity))
                amount -= food.quantity

                # Once chosen, we remove it from the list so we don't double-dip.
                available_foods.remove(food)
            else:
                # If there's more food than we need, we eat just what we want.
                foods_to_eat.append((food, amount))
                amount = 0

        return foods_to_eat  # Return the foods we've chosen.


class MixedConsumptionStrategy(ConsumptionStrategy):

    def __init__(self, fifo_probability: float = 0.25):
        """
        Initializes the Mixed Consumption Strategy.

        Args:
            fifo_probability (float): Chance we pick based on FIFO.
        """

        # The probability we go with FIFO.
        self.fifo_probability = fifo_probability

        # Instances of the basic (FIFO) and random strategies to use based on our roll of the dice.
        self.basic_strategy = BasicConsumptionStrategy()
        self.random_strategy = RandomConsumptionStrategy()

    def select_food(self, pantry: Pantry, food_type: FoodType, amount: float) -> List[Tuple[FoodItem, float]]:
        """
        Select food either randomly or by FIFO based on set probability.

        Args:
            pantry (Pantry): The pantry to choose from.
            food_type (FoodType): The type of food we're in the mood for.
            amount (float): How much food we're lookin' to scarf down.

        Returns:
            List[Dict[FoodItem, float]]: List of selected foods and the amount we're gonna eat.
        """

        # Roll the dice. If we're under our FIFO prob, we go FIFO.
        if random.random() < self.fifo_probability:
            return self.basic_strategy.select_food(pantry, food_type, amount)
        else:
            # Otherwise, go random.
            return self.random_strategy.select_food(pantry, food_type, amount)


class Meal:

    def __init__(self, pantry: Pantry):
        self.pantry = pantry
        self.consumption_patterns = {}

    def set_consumption_patterns(self, patterns: Dict[FoodType, float]):
        """Set up the consumption patterns for the meal.

        Args:
            patterns (Dict[FoodType, float]): The consumption pattern dict.
                Example: {FoodType.LEFTOVER: 0.5, FoodType.PERISHABLE: 0.2, FoodType.NON_PERISHABLE: 0.05}

        Returns:
            Dict[FoodType, float]: The set consumption pattern.
        """
        self.consumption_patterns = patterns
        return patterns

    def choose_food_to_eat(self,
                           consumption_strategy) -> List[Tuple[FoodItem, float]]:
        foods_to_eat = []

        for food_type, amount in self.consumption_patterns.items():
            chosen_foods = consumption_strategy.select_food(self.pantry, food_type, amount)
            foods_to_eat.extend(chosen_foods)

            # The amount left to consume can be computed as the difference
            # between the desired amount and the amount actually consumed.
            consumed_amount = sum([d[1] for d in chosen_foods])
            remaining_amount = amount - consumed_amount

            if remaining_amount > 0:
                foods_to_eat.append(
                    (FoodItem(EMERGENCY_TAKEOUT, FoodType.PERISHABLE, 0, 0, remaining_amount), remaining_amount))

        return foods_to_eat

    def consume(self,
                consumption_strategy: ConsumptionStrategy = BasicConsumptionStrategy()) -> List[Tuple[FoodItem, float]]:
        """
        Decide on the food to eat and then actually consume it.

        So here's the drill. First, we're gonna pick out what we wanna eat using that
        fancy `choose_food_to_eat()` method. Once we've decided on the menu, we dig in and
        update the quantities in the pantry. Remember, if we're still hungry and there's
        not enough in the pantry, we're gonna have some of that "Emergency Takeout".

        Returns:
            List[Dict[FoodItem, float]]:: A list of the food items we consumed.
        """

        foods_to_eat = self.choose_food_to_eat(consumption_strategy)  # Picking out our food
        consumed_foods = []

        for food_choice in foods_to_eat:
            # If it's an "Emergency Takeout", we don't have to update the pantry.
            if food_choice[0].name != "Emergency Takeout":
                food_choice[0].consume(food_choice[1])  # Digging in!
            consumed_foods.append((food_choice[0], food_choice[1]))

        return foods_to_eat


class PlannedMeal:
    """
    Represents a planned meal for a household.

    This doesn't decide the actual items that will be eaten but gives an overview of total grams
    of food that should be consumed for the meal.
    """

    def __init__(self, total_grams: float):
        """
        Initialize a PlannedMeal.

        Args:
            total_grams (float): The total grams of food planned for consumption.
        """
        self.total_grams = total_grams


class MealGenerator(ABC):
    # Some constants to represent standard food consumption per meal for adults and kids.
    ADULT_CONSUMPTION = {"breakfast": 400, "lunch": 600, "dinner": 600}
    KID_CONSUMPTION = {"breakfast": 250, "lunch": 400, "dinner": 400}

    def __init__(self):
        """
        An abstract meal generator that creates meals for a household over a week.

        """

    @abstractmethod
    def generate_weekly_meals(self, household: 'Household') -> List[List[PlannedMeal]]:
        """
        Generate a list of meals for each day of the week.

        Returns:
            Dict[str, List[Meal]]: A dictionary where keys are days of the week and values are lists of meals.
        """
        pass


class StandardMealGenerator(MealGenerator):

    def __init__(self, meals_at_home_ratio: float):
        """
        Initialize the standard meal generator.

        Args:
            meals_at_home_ratio (float): The probability of a meal being eaten at home for the household.
        """
        super().__init__()
        self.meals_at_home_ratio = meals_at_home_ratio

    def generate_weekly_meals(self, household: 'Household') -> List[List[PlannedMeal]]:
        """Generate planned meals for the whole week based on household size and meal preferences."""
        weekly_meals = []

        consumption_patterns = self._calculate_daily_consumption(household)

        for _ in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_meals = []

            # Calculate total consumption for the day, divided by meal type

            # For this basic generator, we'll assume the household consumes the same amount every day.
            # But you could randomize this or make it more complex if needed.
            for meal_name in ["breakfast", "lunch", "dinner"]:
                if random.random() <= self.meals_at_home_ratio:  # Only create meals that are eaten at home
                    meal = PlannedMeal(consumption_patterns[meal_name])
                    day_meals.append(meal)

            weekly_meals.append(day_meals)

        return weekly_meals

    def _calculate_daily_consumption(self, household: 'Household') -> Dict[str, float]:
        """
        Calculate total grams of food required for each meal type (breakfast, lunch, dinner) for the day.
        The distribution across meal types can be adjusted based on preference.
        """

        # We distribute the daily consumption across meals. Here, we're assuming 30% for breakfast, 40% for lunch and dinner.
        consumption_breakdown = {
            "breakfast": (self.ADULT_CONSUMPTION["breakfast"] * household.adults +
                          self.KID_CONSUMPTION["breakfast"] * household.children
                          ),
            "lunch": (self.ADULT_CONSUMPTION["lunch"] * household.adults +
                      self.KID_CONSUMPTION["lunch"] * household.children
                      ),
            "dinner": (self.ADULT_CONSUMPTION["dinner"] * household.adults +
                       self.KID_CONSUMPTION["dinner"] * household.children
                       )
        }

        return consumption_breakdown


class VariableMealGenerator(MealGenerator):
    """
    Like standard meal generator (which it delegates to) but it adds noise (normally distributed) and the chance of guests,
    which here are assumed to be adults...
    """

    def __init__(self, base_generator: MealGenerator, noise_std: float, guest_probability: float, max_guests: int):
        """
        Initialize the variable meal generator.

        Args:
            base_generator (MealGenerator): The base meal generator.
            noise_std (float): Standard deviation for the normal distribution noise.
            guest_probability (float): Probability of guests showing up for a meal.
            max_guests (int): Maximum number of guests that can show up.
        """
        super().__init__()
        self.base_generator = base_generator
        self.noise_std = noise_std
        self.guest_probability = guest_probability
        self.max_guests = max_guests

    def generate_weekly_meals(self, household: 'Household') -> List[List[PlannedMeal]]:
        weekly_meals = self.base_generator.generate_weekly_meals(household)

        for day_meals in weekly_meals:
            for meal in day_meals:

                # Add guest consumption
                if random.random() < self.guest_probability:
                    num_guests = random.randint(1, self.max_guests)
                    # Assuming guests eat the same amount as an adult for simplicity
                    # they always eat for lunch...
                    guest_consumption = num_guests * self.ADULT_CONSUMPTION["lunch"]
                    meal.total_grams += guest_consumption

                # Add normally distributed noise to consumption
                noise = 1 + random.gauss(0, self.noise_std)
                meal.total_grams *= noise

                # Ensure consumption doesn't go negative due to noise
                meal.total_grams = int(max(0, meal.total_grams))

        return weekly_meals


class MealPlanningStrategy(ABC):

    @abstractmethod
    def plan_meal(self, planned_meal: PlannedMeal, household: 'Household', pantry: Pantry) -> Meal:
        """
        Create a Meal object based on the PlannedMeal, Household, and current Pantry state.

        Args:
            planned_meal (PlannedMeal): The planned meal.
            household (Household): The household for which the meal is planned.
            pantry (Pantry): The current state of the household's pantry.

        Returns:
            Meal: The generated meal object with consumption patterns set.
        """
        pass


class FreshFirstStrategy(MealPlanningStrategy):
    """
    Always eats leftovers if there are any, then perishables, then non-perishables...
    """

    def plan_meal(self, planned_meal: PlannedMeal, household: 'Household', pantry: Pantry) -> Meal:
        meal = Meal(pantry)

        # Calculate the amount of each food type based on priority: leftovers, perishables, non-perishables.
        total_grams = planned_meal.total_grams

        leftovers = pantry.get_total_by_type(FoodType.LEFTOVER)
        perishables = pantry.get_total_by_type(FoodType.PERISHABLE)

        leftovers_to_consume = min(leftovers, total_grams)
        total_grams -= leftovers_to_consume

        perishables_to_consume = min(perishables, total_grams)
        total_grams -= perishables_to_consume

        non_perishables_to_consume = total_grams

        consumption_patterns = {
            FoodType.LEFTOVER: leftovers_to_consume,
            FoodType.PERISHABLE: perishables_to_consume,
            FoodType.NON_PERISHABLE: non_perishables_to_consume
        }

        meal.set_consumption_patterns(consumption_patterns)
        return meal


class ProportionalConsumptionStrategy(MealPlanningStrategy):

    def __init__(self, proportion_perishables: float = 0.7):
        self.proportion_perishables = proportion_perishables

    def plan_meal(self, planned_meal: PlannedMeal, household: 'Household', pantry: Pantry) -> Meal:
        meal = Meal(pantry)

        total_grams = planned_meal.total_grams

        leftovers_available = pantry.get_total_by_type(FoodType.LEFTOVER)
        perishables_available = pantry.get_total_by_type(FoodType.PERISHABLE)

        leftovers_to_consume = min(leftovers_available, total_grams)
        total_grams -= leftovers_to_consume

        # Calculate proportional consumption after consuming leftovers
        perishables_to_consume = total_grams * self.proportion_perishables
        non_perishables_to_consume = total_grams - perishables_to_consume

        # If there aren't enough perishables, fill up with non-perishables
        if perishables_available <= perishables_to_consume:
            ### 2000 left, 5000 to eat
            ### that means I can only eat 2000 perishables, and the rest is to be eaten
            to_transfer = perishables_to_consume - perishables_available
            perishables_to_consume = perishables_available

            non_perishables_to_consume += to_transfer

        consumption_patterns = {
            FoodType.LEFTOVER: leftovers_to_consume,
            FoodType.PERISHABLE: perishables_to_consume,
            FoodType.NON_PERISHABLE: non_perishables_to_consume
        }

        meal.set_consumption_patterns(consumption_patterns)
        return meal


class GroceryStore:
    def __init__(self, best_before_params: dict, spoilage_date_params: dict):
        """
        Initialize the GroceryStore with parameters for distributions.

        Args:
            best_before_params (dict): Parameters for the discrete normal distribution for the best_before by FoodType.
                                        {FoodType: (mean, std_dev)}
            spoilage_date_params (dict): Parameters for the discrete normal distribution for the spoilage_date by FoodType.
                                         {FoodType: (mean, std_dev)}
        """
        self.best_before_params = best_before_params
        self.spoilage_date_params = spoilage_date_params
        self.food_names = ["Test", "Other", "SomethingElse", "UHT"]  # Sample food names.

    def _draw_from_distribution(self, mean: float, std_dev: float) -> int:
        """Draw a discrete random value from a normal distribution."""
        return int(random.gauss(mean, std_dev))

    def get_order(self, food_type: FoodType, total_quantity: float) -> List[FoodItem]:
        """
        Get an order for a specific quantity and type of food.

        Args:
            food_type (FoodType): The type of food to be ordered.
            total_quantity (float): Total weight of food to be ordered.

        Returns:
            List[FoodItem]: A list of FoodItems making up the order.
        """
        order = []
        remaining_quantity = int(total_quantity)
        best_before_mean, best_before_std_dev = self.best_before_params[food_type]
        spoilage_date_mean, spoilage_date_std_dev = self.spoilage_date_params[food_type]
        failures = 0
        while remaining_quantity > 0 and failures < 100:
            food_name = food_type.name + " - item"
            best_before = self._draw_from_distribution(best_before_mean, best_before_std_dev)
            spoilage_date = self._draw_from_distribution(spoilage_date_mean, spoilage_date_std_dev)
            # Making sure the spoilage date is always greater than the best before date.
            spoilage_date = max(best_before + 1, spoilage_date)
            # To simulate variable quantities of different items, we'll randomly determine the quantity for this item.
            quantity = min(random.uniform(0.1 * total_quantity, 0.5 * total_quantity), remaining_quantity)
            quantity = int(quantity)
            if quantity == 0:  ## when numbers are really small, you can start missing some orders. Keep them at 0 then....
                failures += 1
            else:
                item = FoodItem(food_name, food_type, best_before, spoilage_date, quantity)
                order.append(item)

                remaining_quantity -= quantity

        return order


class OrderPolicy(ABC):
    """
    Abstract base class for defining how a household determines the quantity to order.
    """

    def __init__(self, frequency: int):
        """
        Initialize the order policy with a fixed frequency for shopping.

        Args:
            frequency: Number of days between grocery shopping trips.
        """
        self.frequency = frequency
        self.days_until_next_order = frequency  # Setting the initial value to the frequency

    @abstractmethod
    def determine_order_quantity(self, household: 'Household') -> Tuple[float, float]:
        """
        Determine the quantity of perishables and non-perishables the household should order.

        Args:
            household: The household making the order.

        Returns:
            Tuple[float, float]: The quantity of perishables and non-perishables to order, respectively.
        """
        pass

    def decrement_days_until_next_order(self):
        """
        Decrease the number of days until the next order by one.
        """
        self.days_until_next_order -= 1

    def reset_days_until_next_order(self):
        """
        Reset the days until the next order back to the original frequency.
        """
        self.days_until_next_order = self.frequency


class FixedConsumptionPolicy(OrderPolicy):
    """
    A simple order policy where the household orders based on fixed daily consumption rates and a fixed duration until the next order.
    """

    def __init__(self, daily_consumption_perishable: int, daily_consumption_non_perishable: int,
                 frequency: int, safety_stock_perishable: int, safety_stock_non_perishable: int):
        """
        Initialize the fixed consumption policy.

        Args:
            daily_consumption_perishable: Expected daily consumption for perishables.
            daily_consumption_non_perishable: Expected daily consumption for non-perishables.
            frequency: Days between shopping trips.
            safety_stock_perishable: Additional safety stock for perishables to order.
            safety_stock_non_perishable: Additional safety stock for non-perishables to order.
        """
        super().__init__(frequency)
        self.daily_consumption_perishable = daily_consumption_perishable
        self.daily_consumption_non_perishable = daily_consumption_non_perishable
        self.safety_stock_perishable = safety_stock_perishable
        self.safety_stock_non_perishable = safety_stock_non_perishable

    def determine_order_quantity(self, household: 'Household') -> Tuple[float, float]:
        """
        Determine order quantity based on fixed daily consumption rates, days until next order, and safety stock.

        Args:
            household: The household making the order.

        Returns:
            Tuple[float, float]: The quantity of perishables and non-perishables to order, respectively.
        """
        order_quantity_perishable = (self.daily_consumption_perishable * self.frequency) + self.safety_stock_perishable
        order_quantity_non_perishable = (
                                                    self.daily_consumption_non_perishable * self.frequency) + self.safety_stock_non_perishable

        # Adjusting for items already in pantry
        order_quantity_perishable -= household.pantry.get_total_by_type(FoodType.PERISHABLE)
        order_quantity_non_perishable -= household.pantry.get_total_by_type(FoodType.NON_PERISHABLE)

        return max(0, order_quantity_perishable), max(0, order_quantity_non_perishable)


class HistoricalConsumptionPolicy(FixedConsumptionPolicy):
    """
    Adapts the FixedConsumptionPolicy based on a household's recent consumption history.
    """

    def __init__(self, base_policy: FixedConsumptionPolicy):
        """
        Initialize the historical consumption policy.

        Args:
            base_policy: The fixed consumption policy that this decorator adapts based on historical data.
        """
        self.base_policy = base_policy

    def determine_order_quantity(self, household: 'Household') -> Tuple[float, float]:
        """
        Determine order quantity based on household's recent consumption history.

        Args:
            household: The household making the order.

        Returns:
            Tuple[float, float]: The quantity of perishables and non-perishables to order, respectively.
        """
        # If there's less than 7 days of history, just use the base policy
        if len(household.history) < 7:
            return self.base_policy.determine_order_quantity(household)
        last_week_consumption_perishable = mean(
            [day["daily_consumption"][FoodType.PERISHABLE] for day in household.history[-7:]])
        last_week_consumption_non_perishable = mean(
            [day["daily_consumption"][FoodType.NON_PERISHABLE] for day in household.history[-7:]])

        self.base_policy.daily_consumption_perishable = last_week_consumption_perishable
        self.base_policy.daily_consumption_non_perishable = last_week_consumption_non_perishable

        return self.base_policy.determine_order_quantity(household)


class AdaptiveOrderPolicy(FixedConsumptionPolicy):
    """
    Adapts the FixedConsumptionPolicy based on a household's recent consumption history.
    Uses weekly averages and standard deviations to determine the order quantity.
    """

    def __init__(self, base_policy: FixedConsumptionPolicy, delta: float = 1.96):
        """
        Initialize the adaptive order policy.

        Args:
            base_policy: The fixed consumption policy that this adaptive policy extends.
            delta: Represents the cycle service level targeted.
        """
        super().__init__(
            daily_consumption_perishable=base_policy.daily_consumption_perishable,
            daily_consumption_non_perishable=base_policy.daily_consumption_non_perishable,
            frequency=base_policy.frequency,
            safety_stock_perishable=base_policy.safety_stock_perishable,
            safety_stock_non_perishable=base_policy.safety_stock_non_perishable
        )
        self.delta = delta

    def _calculate_std_dev(self, data: list) -> float:
        """
        Compute the standard deviation for a given list of data.
        """
        n = len(data)
        if n <= 1:
            return 0

        mean_val = sum(data) / n
        variance = sum((x - mean_val) ** 2 for x in data) / (n - 1)
        std_dev = variance ** 0.5
        return std_dev

    def determine_order_quantity(self, household: 'Household') -> Tuple[float, float]:
        """
        Determine order quantity based on household's recent consumption history.

        Args:
            household: The household making the order.

        Returns:
            Tuple[float, float]: The quantity of perishables and non-perishables to order, respectively.
        """
        # If there's less than 7 days of history, just use the base policy
        if len(household.history) < 7:
            return super().determine_order_quantity(household)

        # Calculate weekly averages
        last_week_consumption_perishable = sum(
            [day["daily_consumption"][FoodType.PERISHABLE] for day in household.history[-7:]]) / 7
        last_week_consumption_non_perishable = sum(
            [day["daily_consumption"][FoodType.NON_PERISHABLE] for day in household.history[-7:]]) / 7

        # Calculate weekly standard deviations
        std_dev_perishable = self._calculate_std_dev(
            [day["daily_consumption"][FoodType.PERISHABLE] for day in household.history[-7:]])
        std_dev_non_perishable = self._calculate_std_dev(
            [day["daily_consumption"][FoodType.NON_PERISHABLE] for day in household.history[-7:]])

        # Update daily consumption rates
        self.daily_consumption_perishable = last_week_consumption_perishable
        self.daily_consumption_non_perishable = last_week_consumption_non_perishable

        # Update safety stocks
        self.safety_stock_perishable = self.delta * std_dev_perishable
        self.safety_stock_non_perishable = self.delta * std_dev_non_perishable

        return super().determine_order_quantity(household)


class PlateWasteCalculator(ABC):

    @abstractmethod
    def compute_plate_waste(self, consumed_items: List[Tuple[FoodItem, float]]) -> List[Tuple[FoodItem, float]]:
        """
        Compute the plate waste for a given meal based on the list of consumed items.

        Args:
            consumed_items (List[Tuple[FoodItem, float]]): List of tuples with FoodItems and their consumed quantities.

        Returns:
            List[Tuple[FoodItem, float]]: List of tuples with FoodItems and their wasted quantities.
        """
        pass


class FixedPercentageWasteCalculator(PlateWasteCalculator):

    def __init__(self, waste_percentage: float):
        self.waste_percentage = waste_percentage

    def compute_plate_waste(self, consumed_items: List[Tuple[FoodItem, float]]) -> List[Tuple[FoodItem, float]]:
        wasted_items = []
        for food_item, amount in consumed_items:
            wasted_amount = amount * self.waste_percentage
            wasted_items.append((food_item, wasted_amount))
        return wasted_items


class LeftoversCalculator(ABC):

    @abstractmethod
    def compute_leftovers(self, consumed_items: List[Tuple[FoodItem, float]],
                          plate_waste: List[Tuple[FoodItem, float]]) -> Dict[FoodType, float]:
        """
        Compute the leftovers for a given meal based on the list of consumed items and plate waste.

        Args:
            consumed_items (List[Tuple[FoodItem, float]]): List of tuples with FoodItems and their consumed quantities.
            plate_waste (List[Tuple[FoodItem, float]]): List of tuples with FoodItems and their wasted quantities.

        Returns:
            Dict[FoodType, float]: Dictionary indicating the amount of leftovers per food type in kg.
        """
        pass


class PerishableLeftoversGenerator(LeftoversCalculator):

    def __init__(self, leftover_percentage: float):
        self.leftover_percentage = leftover_percentage

    def compute_leftovers(self, consumed_items: List[Tuple[FoodItem, float]],
                          plate_waste: List[Tuple[FoodItem, float]]) -> Dict[FoodType, float]:
        leftovers = {FoodType.LEFTOVER: 0, FoodType.PERISHABLE: 0, FoodType.NON_PERISHABLE: 0}
        for food_item, amount in consumed_items:
            if food_item.food_type == FoodType.PERISHABLE:
                leftovers[FoodType.LEFTOVER] += amount * self.leftover_percentage
        return leftovers


class LeftoversGenerator(ABC):

    @abstractmethod
    def compute_leftovers(self, consumed_items: List[Tuple[FoodItem, float]],
                          plate_waste: List[Tuple[FoodItem, float]]) -> float:
        """
        Compute the leftovers for a given meal based on the list of consumed items and plate waste.

        Args:
            consumed_items (List[Tuple[FoodItem, float]]): List of tuples with FoodItems and their consumed quantities.
            plate_waste (List[Tuple[FoodItem, float]]): List of tuples with FoodItems and their wasted quantities.

        Returns:
            Dict[FoodType, float]: Dictionary indicating the amount of leftovers per food type in kg.
        """
        pass


class FixedPercentageLeftoverGenerator(LeftoversGenerator):
    """
    Very simple: each meal eaten produces a fixed percentage of leftovers....
    """

    def __init__(self, leftover_percentage: float):
        self.leftover_percentage = leftover_percentage

    def compute_leftovers(self, consumed_items: List[Tuple[FoodItem, float]],
                          plate_waste: List[Tuple[FoodItem, float]]) -> float:
        leftovers = 0
        for food_item, amount in consumed_items:
                leftovers += amount * self.leftover_percentage
        return leftovers


class Household:
    def __init__(self, adults: int, children: int, income_percentile: float,
                 meal_generator: MealGenerator = StandardMealGenerator(0.5),
                 meal_planning_strategy: MealPlanningStrategy = FreshFirstStrategy(),
                 consumption_strategy: ConsumptionStrategy = BasicConsumptionStrategy(),
                 pantry_strategy: PantryStrategy = LaxStrategy(),
                 order_policy: OrderPolicy = FixedConsumptionPolicy(20000, 20000, 7, 0, 0),
                 grocery_store: GroceryStore = None,
                 leftover_generator: LeftoversGenerator = FixedPercentageLeftoverGenerator(0),
                 plate_waste_generator: PlateWasteCalculator = FixedPercentageWasteCalculator(0)
                 ):
        """
        Represents a household, with its characteristics and pantry.

        Args:
            adults (int): Number of adults in the household.
            children (int): Number of children in the household.
            income_percentile (float): Household income as a percentile (0.0 - 1.0).
            meal_generator: Instance to generate meal plans for the household.
            meal_planning_strategy: Strategy to translate meal plans into actual meals based on pantry contents.
            consumption_strategy: Strategy to decide which specific items to consume from the pantry.
        """

        # Basic household demographics.
        self.adults = adults
        self.children = children
        self.income_percentile = income_percentile

        # Initializing the household's pantry.
        self.pantry = Pantry()
        # Initialize the daily stats history
        self.history = []

        # Strategies and generators for meal planning and consumption.
        self.meal_planning_strategy = meal_planning_strategy
        self.meal_generator = meal_generator
        self.consumption_strategy = consumption_strategy
        self.pantry_strategy = pantry_strategy
        self.leftover_generator = leftover_generator
        self.plate_waste_generator = plate_waste_generator

        # Add an order policy and a link to a grocery store.
        self.order_policy = order_policy
        self.grocery_store = grocery_store

        # Dictionary to keep track of total food consumption by type.
        self.daily_consumption = {
            FoodType.LEFTOVER: 0,
            FoodType.PERISHABLE: 0,
            FoodType.NON_PERISHABLE: 0
        }
        self.daily_emergency_takeouts = 0
        self.daily_plate_waste = 0
        self.daily_leftovers_generated = 0

    def get_total_food(self) -> float:
        """Fetch the total weight of all food in the pantry."""
        return self.pantry.get_total()

    def get_food_by_type(self, food_type: FoodType) -> float:
        """Fetch the total weight of a specific type of food in the pantry."""
        return self.pantry.get_total_by_type(food_type)

    def get_waste_log(self) -> Dict[str, Dict[int, Dict[FoodType, float]]]:
        """Retrieve a log of all the wasted food."""
        return self.pantry.get_waste_log()

    def start_of_week(self):
        """
        Perform tasks that happen at the start of the week.

        This includes generating the weekly meal plans using the household's meal generator.
        Orders, restocking, or other operations could also be added here in the future.
        """
        self.weekly_meals = self.meal_generator.generate_weekly_meals(self)

    def daily_step(self) -> Dict[str, Union[int, Dict[FoodType, float]]]:
        """
        Simulate a day in the life of the household.

        This method performs the daily operations related to meals:
        1. Fetches the meal plan for the day from the weekly plans.
        2. For each planned meal, uses the meal planning strategy to decide the actual meal based on pantry contents.
        3. Consumes the planned items from the pantry.
        4. Keeps a track of the total consumption by food type.
        """

        ## reset meal list
        self.meals_eaten_today = 0
        self.daily_consumption = {
            FoodType.LEFTOVER: 0,
            FoodType.PERISHABLE: 0,
            FoodType.NON_PERISHABLE: 0
        }
        self.daily_emergency_takeouts = 0
        self.daily_plate_waste = 0
        self.daily_leftovers_generated = 0

        meals_today = self.weekly_meals.pop(0)
        for planned_meal in meals_today:
            actual_meal = self.meal_planning_strategy.plan_meal(planned_meal, self, self.pantry)
            consumption = actual_meal.consume(self.consumption_strategy)

            self.meals_eaten_today += 1

            ## some of the consumption will be leftovers and waste....
            ## plate waste...
            plate_waste = self.plate_waste_generator.compute_plate_waste(consumption)
            for wasted in plate_waste:
                self.daily_plate_waste += wasted[1]
            ## leftovers....
            leftovers_here = self.leftover_generator.compute_leftovers(consumption, plate_waste)
            ## put the leftovers in the fridge
            if leftovers_here>0:
                self.pantry.add_item(FoodItem("leftover",FoodType.LEFTOVER,
                                          2,2,leftovers_here))
                self.daily_leftovers_generated+=leftovers_here
            for food_item, amount in consumption:
                self.daily_consumption[food_item.food_type] += amount
                if food_item.name == EMERGENCY_TAKEOUT:
                    self.daily_emergency_takeouts += amount

        ### expire stuff.....
        self.pantry.step(self.pantry_strategy)
        ## now do ordering, if needed
        # Decrement days until the next order.
        self.order_policy.decrement_days_until_next_order()

        total_perishable_bought = 0
        total_nonperishable_bought = 0
        # Check if it's time to place an order.
        if self.order_policy.days_until_next_order == 0:
            # Place an order using the order policy's determine_order_quantity() method.
            perishable_quantity, non_perishable_quantity = self.order_policy.determine_order_quantity(self)

            # Order from the grocery store.
            perishable_order = self.grocery_store.get_order(FoodType.PERISHABLE, perishable_quantity)
            non_perishable_order = self.grocery_store.get_order(FoodType.NON_PERISHABLE, non_perishable_quantity)

            # Add ordered items to the pantry.
            for item in perishable_order:
                total_perishable_bought += item.quantity
                self.pantry.add_item(item)
            for item in non_perishable_order:
                self.pantry.add_item(item)
                total_nonperishable_bought += item.quantity

            # Reset the days until next order.
            self.order_policy.reset_days_until_next_order()

        daily_record = {
            "meals_eaten_today": self.meals_eaten_today,
            "daily_consumption": self.daily_consumption,
            "emergency_takeouts": self.daily_emergency_takeouts,
            "total_perishable_bought": total_perishable_bought,
            "total_nonperishable_bought": total_nonperishable_bought,
            "expired_discards": sum(
                value for value in self.pantry.waste_log['expired_discards'][self.pantry.current_day].values()),
            "strategy_discards": sum(
                value for value in self.pantry.waste_log['strategy_discards'][self.pantry.current_day].values()),
            "total_food_stored": self.pantry.get_total(),
            "perishables_stored": self.pantry.get_total_by_type(FoodType.PERISHABLE),
            "non_perishables_stored": self.pantry.get_total_by_type(FoodType.NON_PERISHABLE),
            "leftovers_stored": self.pantry.get_total_by_type(FoodType.LEFTOVER),
            "daily_plate_waste": self.daily_plate_waste,
            "daily_leftovers_generated": self.daily_leftovers_generated
        }
        self.history.append(daily_record)

        return daily_record
