from simulation import *
import os
import pandas as pd

def run_simulation(where_to_save_results,
                   frequency_grocery_store=7,
                   meal_planning_strategy=FreshFirstStrategy(),
                   consumption_strategy=BasicConsumptionStrategy(),
                   pantry_strategy=StrictStrategy(), critical_value_order_policy=1.96, weeks_to_simulate=30,
                   grocery_store_improvements = 0,
                   meal_generator = StandardMealGenerator(1.0),
                   leftover_generator = FixedPercentageLeftoverGenerator(0),
                   plate_waste_generator = FixedPercentageWasteCalculator(0)
                   ):
    store = GroceryStore(
        best_before_params={
            FoodType.PERISHABLE: (3+grocery_store_improvements, 1),
            FoodType.NON_PERISHABLE: (50, 10),
        },
        spoilage_date_params={
            FoodType.PERISHABLE: (5+grocery_store_improvements, 2),
            FoodType.NON_PERISHABLE: (100, 20),
        }
    )
    households = []
    ADULT_RANGE = (1, 5)  # Assuming a household can have between 1 to 5 adults
    CHILD_RANGE = (0, 5)  # Assuming a household can have between 0 to 5 children
    ADULT_DAILY_CONSUMPTION = 1800
    CHILD_DAILY_CONSUMPTION = 1050
    NUMBER_OF_HOUSEHOLDS = 500
    WEEKS_TO_SIMULATE = weeks_to_simulate
    for _ in range(NUMBER_OF_HOUSEHOLDS):
        num_adults = random.randint(*ADULT_RANGE)
        num_children = random.randint(*CHILD_RANGE)

        # Calculate the total daily consumption for perishable and non-perishable for the household
        total_perishable_consumption = ( num_adults * ADULT_DAILY_CONSUMPTION + num_children * CHILD_DAILY_CONSUMPTION) * 2
        total_non_perishable_consumption = total_perishable_consumption

        household = Household(
            adults=num_adults,
            children=num_children,
            income_percentile=0.5, ## doesn't do anything right now....
            ## % of each meal being consumed at home...
            meal_generator=meal_generator,
            ## % between perishables and non-perishables
            meal_planning_strategy=meal_planning_strategy,
            ## first in, first out, should be careful food about to expire first
            consumption_strategy=consumption_strategy,
            ## anything that pass "best-before"
            pantry_strategy=pantry_strategy,
            ## follows a standard EOQ order policy (mean consumption + critical_value*sd)
            ## adjusts by looking at previous week results...
            order_policy=AdaptiveOrderPolicy(
                FixedConsumptionPolicy(
                    total_perishable_consumption,
                    total_non_perishable_consumption,
                    frequency_grocery_store,
                    0,
                    0
                ),
                critical_value_order_policy
            ),
            grocery_store=store,
            leftover_generator = leftover_generator,
            plate_waste_generator = plate_waste_generator
        )
        ## first week pantry is full, but everything expires in a week
        household.pantry.add_item(
            FoodItem("temp", FoodType.PERISHABLE, frequency_grocery_store-1, frequency_grocery_store-1, total_perishable_consumption * 2 ))
        household.pantry.add_item(
            FoodItem("temp", FoodType.NON_PERISHABLE, frequency_grocery_store-1, frequency_grocery_store-1, total_perishable_consumption * 2 )
        )
        households.append(
            household

        )
    for week in range(WEEKS_TO_SIMULATE):
        print(f"week: {week}")
        for household in households:
            household.start_of_week()
        for day in range(7):
            for household in households:
                household.daily_step()
    # print(households[0].history)
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
    # Extract the directory path from the file path.
    folder_path = os.path.dirname(where_to_save_results)

    # Check if the folder exists, and if not, create it.
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    df.to_csv(where_to_save_results, index=False)


##run_simulation('../output/trial_run.csv')
def main():
### initial runs (get a good handle on stuff)
    for _ in range(30):
        run_simulation('../output/basic_runs/alwaysEatAtHome_freshFirst' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(1),
                       meal_planning_strategy=FreshFirstStrategy())

        run_simulation('../output/basic_runs/alwaysEatAtHome_fiftypercentperishable'+ str(_) +".csv",
                       meal_generator = StandardMealGenerator(1),
                       meal_planning_strategy=ProportionalConsumptionStrategy(0.5))

        run_simulation('../output/basic_runs/fiftyPercentMealsAtHome_freshFirst' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.5),
                       meal_planning_strategy=FreshFirstStrategy())

        run_simulation('../output/basic_runs/fiftyPercentMealsAtHome_fiftypercentperishable' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.5),
                       meal_planning_strategy=ProportionalConsumptionStrategy(0.5))


    ## now do the real ones, assume that the baseline is always fresh first, 75% of meals at home

    for _ in range(30):
        run_simulation('../output/runs/baseline' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy())

        run_simulation('../output/runs/laxpantry' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       pantry_strategy=LaxStrategy())


        run_simulation('../output/runs/safer_pantry' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       critical_value_order_policy=2.326)

        run_simulation('../output/runs/riskier_pantry' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       critical_value_order_policy=1.64)

        run_simulation('../output/runs/frequent_grocery' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       frequency_grocery_store=3)

        run_simulation('../output/runs/infrequent_grocery' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       frequency_grocery_store=14)

        run_simulation('../output/runs/randomfridge' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       consumption_strategy=RandomConsumptionStrategy()
                       )

        run_simulation('../output/runs/bettertechnology' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       grocery_store_improvements=1
                       )
        run_simulation('../output/runs/muchbettertechnology' + str(_) +".csv",
                       meal_generator = StandardMealGenerator(0.75),
                       meal_planning_strategy=FreshFirstStrategy(),
                       grocery_store_improvements=2
                       )



if __name__ == "__main__":
    main()