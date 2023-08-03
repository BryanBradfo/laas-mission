# Dans ce fichier, au moment de l'exploration avec clustering binaire on rajoute un arbre de décision
# Donc en plus des contraintes d'éloignement du clustering binaire, on aura aussi la contrainte de meilleure prédiction de l'arbre de décision

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
sys.path.append("../neural_network")
import Function_NN as nn
sys.path.append("../Clustering_binaire")
import my_clustering as my_cl
sys.path.append("../bdt")
import decision_tree as dt

def main_hyb_nn(resultats_globaux, file, nb_layers, k, k_k, nb_hidden_layers, nb_neurons, tps_max, it_max, type_operation, type_user="user_reg", nb_trees=1, percent_explo = 0.8, display_sol=False, display_start=False, display_matrix=False):

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

    list_obj, pref, list_layers= fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)

    # Vector of the start time of each task of each preference
    starts = user.start_pref(n, m, display_start)

    # Matrix of the start time of each task of each preference
    matrix = user.matrix_pref(n, m, display_matrix)

    # Testing the order of preferences and the differences between solutions
    fm.test(n, m, user, type_operation)
    
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

        # --------- Compute nb_dt decision trees---------------
        nb_dt=nb_trees
        clf, feuilles_conditions = dt.my_decision_tree(n, m, list_layers)
        list_clf = [clf]
        list_feuilles_conditions = [feuilles_conditions]
        for i in range(nb_dt-1):
            clf2, feuilles_conditions2 = dt.my_decision_tree(n, m, list_layers, None)
            list_clf.append(clf2)
            list_feuilles_conditions.append(feuilles_conditions2)


        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, starts = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
        # # --------- Add the constraints considering the clustering
        print(list_layers)
        list_rayon_layers, list_start_sol_layers, dict_sol_rayon  = my_cl.list_rayon_binaire_cluster(n, m, list_layers)
        list_rayon_layers_flatten = [item for sublist in list_rayon_layers[1:] for item in sublist]
        list_start_sol_layers_flatten = [item for sublist in list_start_sol_layers[1:] for item in sublist]
            
        for l in range(len(list_rayon_layers_flatten)):
            solver.add_constraint(model, my_cl.manhattan_binaire_distance_contrainte(list_start_sol_layers_flatten[l], [model.start_of(variables[i//m][i%m]) for i in range(n*m)]) > list_rayon_layers_flatten[l])

        #----------Add news variables "order1" and "order_i" to the model for dt---------------
        list_order = []
        for i in range(nb_dt):
            order = model.binary_var(name="order"+str(i+1))
            list_order.append(order)
            solver.add_variable(order)
    
        # --------- Add the new constraints to the model (concerning the order) for dt
        list_variables = [model.start_of(variables[i//m][i%m]) for i in range(n*m)]
        
        list_constraint_list_of_tree = []
        for i in range(nb_dt):
            print("list_feuilles_conditions[i]",list_feuilles_conditions[i])
            # Add the constraints related to the decision tree
            constraint_list_of_tree = dt.constraint_tree(list_order[i],list_variables, list_feuilles_conditions[i])
            list_constraint_list_of_tree.append(constraint_list_of_tree)

        # Nb_dt iterations
        for i in range(nb_dt):
            # Iteration in the list of constraints
            for constraint in list_constraint_list_of_tree[i]:
                solver.add_constraint(model, constraint)
            solver.add_constraint(model, list_order[i] == 1) 

                
        # ------------ Solve the model
        print("\nSolving the model...")
        model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)
        print("The number of solutions generated is :",nb_solution)
        
        # Adding the objective value of each solution to a list
        list = []
        # User choice : reg or simple
        if type_user == "user_reg":
            # Distinction between type_operation = "plus" or "fois"
            if type_operation == "plus":
                for sol in msol:
                    list.append(user.makespan(sol) + user.regularity(sol, n, m))
            else:
                for sol in msol:
                    list.append(user.makespan(sol) * user.regularity(sol, n, m))
        
        else:
            for sol in msol:
                list.append(user.makespan(sol))

        if len(list) == 0:
            print("No solution at iteration", it)
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
        list_obj, pref, list_layers = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)
        list_min_obj_global.append(min(list_obj))

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user, type_operation)

        # Get the solutions into a good format
        sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)


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
    desagreement = True

    # ----------------- Add the preferences to the model
    while criterion :
        print("\n--------Iteration {}---------".format(it))

        # Check if it exists at least one perfect neural networks based on the previous solutions 
        # independently from the scheduling problem
        list_weights = nn.find_perfect_NN(file, sol_layers, nb_hidden_layers, nb_neurons)

        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, starts = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
         # --------- Add the scheduling constraints to the model
        model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)

    
        # ---------------- Interaction with the neural network

        # Create the weights of the neural network
        weights10 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]
        weights1 = weights10 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]
        
        # Add the weights to the model
        for i in range(len(weights1)):
            for j in range(len(weights1[i])):
                for k in range(len(weights1[i][j])):
                    model.add(weights1[i][j][k])


        # Create the output variable of the neural network and add it to the model
        outputvar_NN1 = model.binary_var(name="outputvar_NN1")
        model.add(outputvar_NN1)

        # Train the neural network
        for order in range(len(sol_layers)):
            for sol in sol_layers[order]:

                # Get the output of the neural network
                output_NN1 = nn.activation_function(model, solver, sol, weights1, nb_hidden_layers, nb_neurons, optimalval)
                if order == 0:
                    solver.add_constraint(model, output_NN1 == 1)
                else:
                    solver.add_constraint(model, output_NN1 == 0)

        # Create the second neural network if there is still a desagreement and if a second nn exists
        if len(list_weights) == 2 and desagreement:
            weights20 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]
            weights2 = weights20 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]
        
            # Add the weights to the model
            for i in range(len(weights2)):
                for j in range(len(weights2[i])):
                    for k in range(len(weights2[i][j])):
                        model.add(weights2[i][j][k])

            # Create the output variable of the neural network and add it to the model
            outputvar_NN2 = model.binary_var(name="outputvar_NN2")
            model.add(outputvar_NN2)


            # Train the neural network
            for order in range(len(sol_layers)):
                for sol in sol_layers[order]:

                    # Get the output of the neural network
                    output_NN2 = nn.activation_function(model, solver, sol, weights2, nb_hidden_layers, nb_neurons, optimalval)
                    if order == 0:
                        solver.add_constraint(model, output_NN2 == 1)
                    else:
                        solver.add_constraint(model, output_NN2 == 0)


        # Compare the result of 2 different neural networks for the same solution

        # Get the start of each task (variable of the model)
        tasks_starts = []
        for i in range(n):
            for j in range(m):
                tasks_starts.append(model.start_of(variables[i][j]))

        # Add the constraints to the model that the output of the neural network must be equal to the output of the solver
        solver.add_constraint(model, outputvar_NN1 == nn.activation_function(model, solver, tasks_starts, weights1, nb_hidden_layers, nb_neurons, optimalval))


        if len(list_weights) == 2 and desagreement:
            # Add the constraints to the model that the output of the neural network must be equal to the output of the solver
            solver.add_constraint(model, outputvar_NN2 == nn.activation_function(model, solver, tasks_starts, weights2, nb_hidden_layers, nb_neurons, optimalval))
            # Find a solution where the 2 neural networks disagree
            solver.add_constraint(model, outputvar_NN1 != outputvar_NN2)
            print("Desagrement found")        
        elif not desagreement:
            # Find a solution where the neural network return 1
            solver.add_constraint(model, outputvar_NN1 == 1)
            print("Desagrement not found, we use one nn")


        # ------------ Solve the model
        print("\nSolving the model...")
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)
        
        # if no solution found, go to the next iteration and desagreement becomes 
        # False so we use only one neural network
        if nb_solution == 0:
            print("No solution found !")
            desagreement = False
            list_min_obj.append(list_min_obj[-1])
            list_min_obj_global.append(min(list_obj))
                      
            #------------------ Condition d'arrêt ------------------
            tps += runtime
            it += 1            
            criterion = (tps < tps_max) and (it < it_max) 
            fm.stopCondition(it, it_max, tps, tps_max)
            
            continue
        else:
            desagreement = True

        # Adding the objective value of each solution to a list
        list = []
        # User choice : reg or simple
        if type_user == "user_reg":
            # Distinction between type_operation = "plus" or "fois"
            if type_operation == "plus":
                for sol in msol:
                    list.append(user.makespan(sol) + user.regularity(sol, n, m))
            else:
                for sol in msol:
                    list.append(user.makespan(sol) * user.regularity(sol, n, m))
        
        else:
            for sol in msol:
                list.append(user.makespan(sol))

        
        list_min_obj.append(min(list))

        # ------------ Display the result
        fm.display_solution(msol, display_sol)

        # ---------------- Interaction with the user
        list_obj, pref, list_layers = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)

        list_min_obj_global.append(min(list_obj))

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user, type_operation)

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
    list_min_obj, list_min_obj_global = main_hyb_nn({}, '../file_with_optimal_val/la04.txt', 2, 10, 15, 1, [1,1], 100, 10, "plus", type_user ="other")
    print(list_min_obj)
    print(list_min_obj_global)

# Appeler la fonction main() si ce fichier est le point d'entrée du programme
if __name__ == "__main__":
    main()
