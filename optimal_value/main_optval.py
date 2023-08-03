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

def main_optval(resultats_globaux, file, time_limit=500, type_operation="plus", type_user="user_reg"):
    #############################
    ### Main program ###
    #############################

    print("\n--------Main program is loading...---------")

    # --------- Interaction with the solver
    data = []
    n, m, data, T_machine, T_duration, duration, optimalval = fm.get_data_from_file(file)

    if type_user == "user_reg":
        # --------- Call Solver constructor in Solver.py and create the tasks of the model
        model, solver , tasks = fm.initialize_solver(data, n, m, duration)

        # ------------ Solve the model
        print("\nSolving the model...")
        
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

        makespan = max([model.end_of(tasks[i][T_machine[i*m + m-1]]) for i in range(n)])
        print("Makespan = ", makespan)

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

        if type_operation == "plus":
            # solver.add_constraint(model, model.minimize(sum + optimalval))
            solver.add_constraint(model, model.minimize(sum + makespan))
        else:
            # solver.add_constraint(model, model.minimize(sum * optimalval))
            solver.add_constraint(model, model.minimize(sum * makespan))

        print("\nObjective function added !")


        # Solve the model.
        msol = model.solve(TimeLimit=time_limit, LogVerbosity="Quiet", SearchType='DepthFirst')
        print("Model solved !")
        msol.get_solve_status()
        resultats_globaux.update({file: [msol.get_objective_value()]})
        return msol.get_objective_value()
    else:
        resultats_globaux.update({file: [optimalval]})    


def main():
    # Code principal du script
    print("Début du programme")

    #Liste des fichiers dont on veut trouver la solution optimale
    list_files = ['../file_with_optimal_val/la01.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la05.txt', '../file_with_optimal_val/la06.txt', '../file_with_optimal_val/la07.txt', '../file_with_optimal_val/la08.txt', '../file_with_optimal_val/la09.txt', '../file_with_optimal_val/la10.txt', '../file_with_optimal_val/la11.txt', '../file_with_optimal_val/la12.txt', '../file_with_optimal_val/la13.txt', '../file_with_optimal_val/la14.txt', '../file_with_optimal_val/la15.txt', '../file_with_optimal_val/la16.txt', '../file_with_optimal_val/la17.txt', '../file_with_optimal_val/la18.txt', '../file_with_optimal_val/la19.txt', '../file_with_optimal_val/la20.txt', '../file_with_optimal_val/la21.txt', '../file_with_optimal_val/la22.txt', '../file_with_optimal_val/la23.txt', '../file_with_optimal_val/la24.txt', '../file_with_optimal_val/la25.txt', '../file_with_optimal_val/la26.txt', '../file_with_optimal_val/la27.txt', '../file_with_optimal_val/la28.txt', '../file_with_optimal_val/la29.txt', '../file_with_optimal_val/la30.txt', '../file_with_optimal_val/la31.txt', '../file_with_optimal_val/la32.txt', '../file_with_optimal_val/la33.txt', '../file_with_optimal_val/la34.txt', '../file_with_optimal_val/la35.txt', '../file_with_optimal_val/la36.txt', '../file_with_optimal_val/la37.txt', '../file_with_optimal_val/la38.txt', '../file_with_optimal_val/la39.txt', '../file_with_optimal_val/la40.txt']
    
    #Paramètres de la fonction main_optval_regularity
    tps_max = 6000
    type_operations = ["plus", "fois"]
    type_user = "user_reg"
    #Lancement des threads
    n = len(list_files)
    if type_user == "user_reg":
        opt_val = [{}, {}]
        threads = []
        for i in range(2*n):
            if i < n:
                t = threading.Thread(target=main_optval, args=(opt_val[0], list_files[i], tps_max, type_operations[0], type_user))
                threads.append(t)
                t.start()
            else:
                t = threading.Thread(target=main_optval, args=(opt_val[1], list_files[i-n], tps_max, type_operations[1], type_user))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()
    else:
        opt_val = [{}]
        for i in range(n):
            main_optval(opt_val[0], list_files[i], tps_max, type_operations[0], type_user)

    
    #Affichage des résultats
    print("Résultats :")
    if len(opt_val) == 1:
        print("Optimal value : ", opt_val[0])
    else:
        print("Plus : ", opt_val[0])
        print("Fois : ", opt_val[1])
        fichier_txt = "Plus: "
        fichier_txt += "\n"
        fichier_txt += str(opt_val[0])
        fichier_txt += "\n"
        fichier_txt += "\n"
        fichier_txt += "Fois:"
        fichier_txt += "\n"
        fichier_txt += str(opt_val[1])
        fichier_txt += "\n"
        print("Fin du programme")

    with open("resultats.txt", "a") as file:
        file.write(fichier_txt)

# Appeler la fonction main() si ce fichier est le point d'entrée du programme
if __name__ == "__main__":
    main()
