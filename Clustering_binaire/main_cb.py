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
import matplotlib.pyplot as plt

#############################
### Essentials functions ###
#############################
#import functionMain du dossier parent
sys.path.append("..")
from Solver import *
from User import *
import FunctionMain as fm
import my_clustering as my_cl

def main_cb(resultats_globaux, file, nb_layers, k, k_k, tps_max, it_max, type_operation, type_user="user_reg", percent_explo = 0.8, display_sol=False, display_start=False, display_matrix=False):

    #############################
    ### Main program ###
    #############################
    #-----------------------------First iteration-----------------------------#

    print("\n--------Main program is loading...---------")

    # --------- Interaction with the solver
    data = []
    n, m, data, T_machine, T_duration, duration, optimalval = fm.get_data_from_file(file)

    # --------- Call Solver constructor in Solver.py and create the variables of the model
    model, solver, starts = fm.initialize_solver(data, n, m, duration)

    model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)

    # ------------ Solve the model
    print("\nSolving the model...")
    msol, nb_solution, runtime = solver.solve(model, k, n, m, variables)


    # ------------ Display the result
    fm.display_solution(msol, display_sol)
    print("Model solved !")

    # ---------------- Interaction with the user
    print("\n--------Interaction with the user...---------")
    print("\nCreating the user...")
    user = User()
    print("User created !")

    #Get the variables of the model
    variables = solver.get_variables()

    list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)

    # Vector of the start time of each task of each preference
    starts = user.start_pref(n, m, display_start)

    # Matrix of the start time of each task of each preference
    matrix = user.matrix_pref(n, m, display_matrix)

    # Testing the order of preferences and the differences between solutions
    fm.test(n, m, user)
    
    #____________________ End first iteration____________________#


    ####################################################################
    #### Exploration: RECHERCHE DE NOUVELLES SOLUTIONS 
    ####################################################################


    ###  -------------- Iteration of the solver with the preferences
    it = 1
    tps = runtime
    list_min_obj = [min(list_obj)]
    list_min_obj_global = [min(list_obj)]
    it_max_exploration = percent_explo*it_max
    tps_max_exploration = percent_explo*tps_max
    criterion = (tps < tps_max_exploration) and (it < it_max_exploration) 

    # ----------------- Add the preferences to the model
    while criterion :
        print("\n--------Iteration {}---------".format(it))

        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, starts = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
        # # --------- Add the constraints considering the clustering
        
        list_rayon_layers, list_start_sol_layers, dict_sol_rayon  = my_cl.list_rayon_binaire_cluster(n, m, list_layers)
        list_rayon_layers_flatten = [item for sublist in list_rayon_layers[1:] for item in sublist]
        list_start_sol_layers_flatten = [item for sublist in list_start_sol_layers[1:] for item in sublist]
            
        for l in range(len(list_rayon_layers_flatten)):
            solver.add_constraint(model, my_cl.manhattan_binaire_distance_contrainte(list_start_sol_layers_flatten[l], [model.start_of(variables[i//m][i%m]) for i in range(n*m)]) > list_rayon_layers_flatten[l])
                
                
        # --------- Add the constraints considering the clustering
        model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)

        # ------------ Solve the model
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)
        
        # Adding the objective value of each solution to a list
        list = []
        # User choice : reg or simple
        if type_user == "user_reg":
            # Distinction between type_operation = "plus" or "fois"
            if type_operation == "plus":
                for sol in msol:
                    list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
            else:
                for sol in msol:
                    list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))
        
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol))

        if len(list) == 0:
            print("Aucune solution générée à l'itération ", it)
            list_min_obj.append(list_min_obj[-1])
            list_min_obj_global.append(list_min_obj_global[-1])
            
            #------------------ Condition d'arrêt ------------------
            tps += runtime
            it += 1            
            criterion = (tps < tps_max_exploration) and (it < it_max_exploration) 
            fm.stopCondition(it, it_max_exploration, tps, tps_max_exploration)
            continue

        list_min_obj.append(min(list))

        # ------------ Display the result
        fm.display_solution(msol, display_sol)
        # ---------------- Interaction with the user
        list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)
        list_min_obj_global.append(min(list_obj))

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user)

    #------------------ Condition d'arrêt ------------------
        tps += runtime
        it += 1
        criterion = (tps < tps_max_exploration) and (it < it_max_exploration) 
        fm.stopCondition(it, it_max_exploration, tps, tps_max_exploration)
    it_final_exploration = it


    ####################################################################
    #### Exploitation: RECHERCHE DE NOUVELLES SOLUTIONS 
    ####################################################################


    ###  -------------- Iteration of the solver with the preferences

    criterion = (tps < tps_max) and (it < it_max) 
    # ----------------- Add the preferences to the model
    while criterion :
        print("\n--------Iteration {}---------".format(it))

        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, starts = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
        # # --------- Add the constraints considering the clustering
        
        list_rayon_layers, list_start_sol_layers, dict_sol_rayon  = my_cl.list_rayon_binaire_cluster(n, m, list_layers)
        
        list_cluster_layers = my_cl.my_clustering_binaire(n, m, list_rayon_layers, list_layers)

        list_centroides_layers = my_cl.centroides_clusters(n, m, list_cluster_layers)

        sum = 0
        for i in range(len(list_centroides_layers)): #On parcourt les layers
            sum_temp = 0
            for j in range(len(list_centroides_layers[i])): #On parcourt les clusters
                sum_temp += my_cl.manhattan_binaire_distance_contrainte(list_centroides_layers[i][j], [model.start_of(variables[i//m][i%m]) for i in range(n*m)])
            sum_temp *= len(list_centroides_layers)-i 
        sum += sum_temp
        model.add(minimize(sum))
    

        # ------------ Solve the model
        model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)
        
        # Adding the objective value of each solution to a list
        list = []
        # User choice : reg or simple
        if type_user == "user_reg":
            # Distinction between type_operation = "plus" or "fois"
            if type_operation == "plus":
                for sol in msol:
                    list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
            else:
                for sol in msol:
                    list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))
        
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol))
        if len(list) == 0:
            print("No solution at iteration", it)
            list_min_obj.append(list_min_obj[-1])
            list_min_obj_global.append(list_min_obj_global[-1])
            
            #------------------ Condition d'arrêt ------------------
            tps += runtime
            it += 1            
            criterion = (tps < tps_max) and (it < it_max) 
            fm.stopCondition(it, it_max, tps, tps_max)
            continue
        
        list_min_obj.append(min(list))

        # ------------ Display the result
        fm.display_solution(msol, display_sol)

        # ---------------- Interaction with the user
        list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)

        list_min_obj_global.append(min(list_obj))

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user)

    #------------------ Condition d'arrêt ------------------
        tps += runtime
        it +=1
        criterion = (tps < tps_max) and (it < it_max) 
        fm.stopCondition(it, it_max, tps, tps_max)

    #-------------------Results------------------------------
    resultats_globaux.update({file: [list_min_obj, list_min_obj_global]})
    return list_min_obj, list_min_obj_global


def main():
    # Code principal du script
    print("Début du programme")
    list_min_obj, list_min_obj_global = main_cb({}, '../file_with_optimal_val/la04.txt', 2, 10, 15, 100, 10, "plus", type_user ="other")
    print(list_min_obj)
    print(list_min_obj_global)

# Appeler la fonction main() si ce fichier est le point d'entrée du programme
if __name__ == "__main__":
    main()
