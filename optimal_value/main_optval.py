import sys
# try:
#     import docplex.mp
# except:
#     if hasattr(sys, 'real_prefix'):
#         !pip install docplex -q
#     else:
#         !pip install --user docplex -q

#############################
### Import libraries ###
#############################

from docplex.cp.model import *
from docplex.cp.config import get_default
import numpy as np
import time

#############################
### Essentials functions ###
#############################
sys.path.append("..")
import FunctionMain as fm
from Solver import *
from User import *

def main_optval(resultats_globaux, file, plot_name, nb_layers, k, k_k, tps_max, it_max, type_operation, percent_explo = 0.8, display_sol=False, display_start=False, display_matrix=False):
    #############################
    ### Main program ###
    #############################

    print("\n--------Main program is loading...---------")

    # --------- Interaction with the solver
    data = []
    n, m, data, T_machine, T_duration, duration, optimalval = fm.get_data_from_file(file)

    # --------- Call Solver constructor in Solver.py and create the tasks of the model
    model, solver , tasks = fm.initialize_solver(data, n, m, duration)

    # ------------ Solve the model
    print("\nSolving the model...")

    # list_tasks = solver.get_tasks()
    # tasks = list_variables[0]

    # ------------ Add constraints to the solver

    print("\nAdding precedence constraints to the solver...")
    # Add precedence constraints
    for i in range(n):
        for j in range(1,m):
            solver.add_constraint(model, end_before_start(tasks[i][T_machine[i*m + j-1]], tasks[i][T_machine[i*m + j]]))
    print("Precedence constraints added !")

    print("\nAdding disjunctive constraints to the solver...")
    # Add disjunctive constraints 
    for machine in range(m):
        solver.add_constraint(model, no_overlap([tasks[i][machine] for i in range(n)]))
    print("Disjunctive constraints added !")

    print("\nAdding objective function to the solver...")

    # makespan = max([model.end_of(tasks[i][T_machine[i*m + m-1]]) for i in range(n)])
    # print("Makespan = ", makespan)

    # Add objective function
    waiting_time = [[] for i in range(m)]
    machines = [[] for i in range(m)]
    machinesTemp = [[] for i in range(m)]

    SortedSof = [[None for i in range(n)] for j in range(m)]
    SortedEof = [[None for i in range(n)] for j in range(m)]

    P = [[None for i in range(n)] for j in range(m)]

    list_obj = []

    for j in range(m):
        for i in range(n):

            machines[j].append(tasks[i][j])
            
            SortedSof[j][i] = model.integer_var(min=0, max=2*optimalval)
            SortedEof[j][i] = model.integer_var(min=0, max=2*optimalval)
        

    for j in range(m):
        for i in range(n-1):

            solver.add_constraint(model, SortedSof[j][i] < SortedSof[j][i+1])
            solver.add_constraint(model, SortedEof[j][i] < SortedEof[j][i+1])

            MachinesStart = [SortedSof[j][i] == model.start_of(machines[j][k]) for k in range(n)]
            solver.add_constraint(model, logical_or(MachinesStart))

            MachinesEnd = [SortedEof[j][i] == model.end_of(machines[j][k]) for k in range(n)]
            solver.add_constraint(model, logical_or(MachinesEnd))

            waiting_time[j].append(SortedSof[j][i+1] - SortedEof[j][i])


    for machine in range(m):
        sum = 0
        for i in range(len(waiting_time)-1):
            for j in range(i+1, len(waiting_time[i])):
                sum += abs(waiting_time[machine][j] - waiting_time[machine][i])
        list_obj.append(sum)

    sum = 0
    for i in range(len(list_obj)):
        sum += list_obj[i]

    solver.add_constraint(model, model.minimize(sum*optimalval))
    # solver.add_constraint(model, model.minimize(sum + makespan))

    print("\nObjective function added !")


    # Solve the model.
    msol = model.solve(TimeLimit=300, LogVerbosity="Quiet")
    # msol = model.solve(TimeLimit=60, LogVerbosity="Quiet")
    # print(type(msol)) #CpoSolveResult
    # print("objective value : ", msol.get_objective_value())
    # print("all_var_solutions : ",msol.get_all_var_solutions())
    # print("solution : ", msol.get_solution())
    # j=0
    # for i in msol:
    #     j += 1
    #     i.write()
    # # print(j)


    # ------------ Display the result
    # fm.display_solution(msol, display_sol)
    print("Model solved !")

    # # ---------------- Interaction with the user
    # print("\n--------Interaction with the user...---------")
    # print("\nCreating the user...")
    # user = User()
    # print("User created !")

    # #Get the tasks of the model
    # tasks = solver.get_tasks()

    # list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m)

    # # Vector of the start time of each task of each preference
    # starts = user.start_pref(n, m, tasks, display_start)

    # # Matrix of the start time of each task of each preference
    # matrix = user.matrix_pref(n, m, display_matrix)

    # # Testing the order of preferences and the differences between solutions
    # fm.test(n, m, user)

    # print("list layers : ",list_layers)

    return msol.get_objective_value()

def main():
    # Code principal du script
    print("Début du programme")
    opt_val = main_optval({}, '../file_with_optimal_val/la04.txt', "test0", 2, 10, 15, 100, 10, "plus")
    print(f"The optimal value is : {opt_val}")
    print("Fin du programme")

# Appeler la fonction main() si ce fichier est le point d'entrée du programme
if __name__ == "__main__":
    main()
