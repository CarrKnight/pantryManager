### a simple run where we have 100 households. Each target about 50% perishables, 50% unperishables. They are of different sizes
### they all shop once a week

## tests:
# (1) What if people switch from Strict to Lax?
# (2) What if people get more "relaxed" about safety stock
# (3) what if grocery store frequency is faster?
# (4) what if people aren't very strict about consuming older food at home first?
# (5) what if people want more perishables in their lives?
# (6) What if we manage to push perishables to last one more day on average?
import random
from simulation import *

store = GroceryStore(
    best_before_params={
        FoodType.PERISHABLE: (3, 1),
        FoodType.NON_PERISHABLE: (50, 10),
    },
    spoilage_date_params={
        FoodType.PERISHABLE: (5, 2),
        FoodType.NON_PERISHABLE: (100, 20),
    }
)
households = []

ADULT_RANGE = (1, 5)  # Assuming a household can have between 1 to 5 adults
CHILD_RANGE = (0, 5)  # Assuming a household can have between 0 to 5 children

ADULT_DAILY_CONSUMPTION = 1800
CHILD_DAILY_CONSUMPTION = 1050

for _ in range(500):
    num_adults = random.randint(*ADULT_RANGE)
    num_children = random.randint(*CHILD_RANGE)

    # Calculate the total daily consumption for perishable and non-perishable for the household
    total_perishable_consumption = (num_adults * ADULT_DAILY_CONSUMPTION + num_children * CHILD_DAILY_CONSUMPTION) * 2
    total_non_perishable_consumption = total_perishable_consumption

    household = Household(
        adults=num_adults,
        children=num_children,
        income_percentile=0.5,
        ## % of each meal being consumed at home...
        meal_generator=StandardMealGenerator(0.5),
        ## % between perishables and non-perishables
        meal_planning_strategy=ProportionalConsumptionStrategy(0.5),
        ## first in, first out, should be careful food about to expire first
        consumption_strategy=BasicConsumptionStrategy(),
        ## anything that pass "best-before"
        pantry_strategy=StrictStrategy(),
        ## follows a standard EOQ order policy (mean consumption + 1.96*sd)
        ## adjusts by looking at previous week results...
        order_policy=AdaptiveOrderPolicy(
            FixedConsumptionPolicy(
                total_perishable_consumption,
                total_non_perishable_consumption,
                7,
                0,
                0
            ),
            1.96
        ),
        grocery_store=store
    )
    ## first week pantry is full, but everything expires in a week
    household.pantry.add_item(
        FoodItem("temp", FoodType.PERISHABLE, 7, 7, total_perishable_consumption * 10))
    household.pantry.add_item(
        FoodItem("temp", FoodType.NON_PERISHABLE, 7, 7, total_perishable_consumption * 10)
    )
    households.append(
        household


    )


for week in range(100):
    print(f"week: {week}")
    for household in households:
        household.start_of_week()
    for day in range(7):
        for household in households:
            household.daily_step()

#print(households[0].history)

import pandas as pd

records = []

for idx, household in enumerate(households):
    for day, daily_record in enumerate(household.history):
        # Prefix each record with household_number and simulated_day
        # Prefix each record with household_number and simulated_day
        record = {
            'household_number': idx,
            'simulated_day': day,
            'daily_consumption_leftover': daily_record['daily_consumption'][FoodType.LEFTOVER],
            'daily_consumption_perishable': daily_record['daily_consumption'][FoodType.PERISHABLE],
            'daily_consumption_non_perishable': daily_record['daily_consumption'][FoodType.NON_PERISHABLE],
        }
        # Removing meals_eaten_today as we have split it
        daily_record_without_meals = {key: daily_record[key] for key in daily_record if key != 'daily_consumption'}
        record.update(daily_record_without_meals)
        records.append(record)

# Convert list of records to DataFrame
df = pd.DataFrame(records)

df.to_csv('simulation_results.csv', index=False)
