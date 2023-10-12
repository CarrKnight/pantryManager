from simulation_runners import run_simulation
from simulation import *

for _ in range(30):
    # run_simulation('../output/runs_oct11/baseline' + str(_) + ".csv",
    #                meal_generator=StandardMealGenerator(0.75),
    #                meal_planning_strategy=FreshFirstStrategy())
    # ## guests....
    # run_simulation('../output/runs_oct11/guests' + str(_) + ".csv",
    #                meal_generator=VariableMealGenerator(StandardMealGenerator(0.75),
    #                                                     0,
    #                                                     .25,
    #                                                     3),
    #                meal_planning_strategy=FreshFirstStrategy())
    # run_simulation('../output/runs_oct11/noise' + str(_) + ".csv",
    #                meal_generator=VariableMealGenerator(StandardMealGenerator(0.75),
    #                                                     .15,
    #                                                     0,
    #                                                     3),
    #                meal_planning_strategy=FreshFirstStrategy())
    run_simulation('../output/runs_oct11/noiseandguests' + str(_) + ".csv",
                   meal_generator=VariableMealGenerator(StandardMealGenerator(0.75),
                                                        .15,
                                                        .25,
                                                        3),
                   meal_planning_strategy=FreshFirstStrategy())
    # ## 5% leftovers
    # run_simulation('../output/runs_oct11/leftovers' + str(_) + ".csv",
    #                meal_generator=StandardMealGenerator(0.75),
    #                meal_planning_strategy=FreshFirstStrategy(),
    #                leftover_generator=FixedPercentageLeftoverGenerator(0.05))
