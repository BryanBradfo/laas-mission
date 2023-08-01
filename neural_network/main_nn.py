import sys

#############################
### Import libraries ###
#############################

from docplex.cp.model import *
import matplotlib.pyplot as plt

#############################
### Essentials functions ###
#############################
import Function_NN as nn
sys.path.append("..")
from Solver import *
from User import *
import FunctionMain as fm


def main_nn(resultats_globaux, file, nb_layers, k, k_k, nb_hidden_layers, nb_neurons, tps_max, it_max, type_operation, display_sol=False, display_start=False, display_matrix=False):
    #############################
    ### Main program ###
    #############################

    print("\n--------Main program is loading...---------")

    # --------- Interaction with the solver
    data = []
    n, m, data, T_machine, _, duration, optimalval = fm.get_data_from_file(file)

    # --------- Call Solver constructor in Solver.py and create the variables of the model
    model, solver, _ = fm.initialize_solver(data, n, m, duration)

    model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)

    # ------------ Solve the model
    print("\nSolving the model...")
    msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)

    # ------------ Display the result
    # fm.display_solution(msol, display_sol)
    print("Model solved !")

    # ---------------- Interaction with the user
    print("\n--------Interaction with the user...---------")
    print("\nCreating the user...")
    user = User()
    print("User created !")

    #Get the variables of the model

    list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m)

    # Vector of the start time of each task of each preference
    starts = user.start_pref(n, m, display_start)

    # Matrix of the start time of each task of each preference
    matrix = user.matrix_pref(n, m, display_matrix)

    # Testing the order of preferences and the differences between solutions
    fm.test(n, m, user)

    print("list layers : ",list_layers)

    sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)


    #____________________ End first iteration____________________#

    ##############################################################################
    #### NOUVELLES SOLUTIONS ET NOUVEAUX RESEAUX DE NEURONES A CHAQUE ITERATION  #
    ##############################################################################

    ###  -------------- Iteration of the solver with the preferences
    it = 1
    tps = runtime
    list_min_obj = [min(list_obj)]
    list_min_obj_global = [min(list_obj)]

    criterion = (tps < tps_max) and (it < it_max) 


    # ----------------- Add the preferences to the model
    while criterion :
        print("\n--------Iteration {}---------".format(it))

        list_weights = nn.find_perfect_NN(file, sol_layers, nb_hidden_layers, nb_neurons)
        print(list_weights)

        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, _ = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
        model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)

        # ---------------- Interaction with the neural network

        # Create the weights of the neural network
        weights10 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]
        weights1 = weights10 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]
        
        for i in range(len(weights1)):
            for j in range(len(weights1[i])):
                for k in range(len(weights1[i][j])):
                    model.add(weights1[i][j][k])


        outputvar_NN1 = model.binary_var(name="outputvar_NN1")
        model.add(outputvar_NN1)


        if len(list_weights) == 2:
            weights20 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]
            weights2 = weights20 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]
        
            for i in range(len(weights2)):
                for j in range(len(weights2[i])):
                    for k in range(len(weights2[i][j])):
                        model.add(weights2[i][j][k])

            outputvar_NN2 = model.binary_var(name="outputvar_NN2")
            model.add(outputvar_NN2)


        # Add the constraint that the weights of the neural network must be different from the previous one
            bb = model.integer_var(0,1)
            solver.add_variable(bb)
            bb=1

            list_variables = solver.get_variables()
            variables = list_variables[0]

            b = model.integer_var(0,1)
            solver.add_variable(b)
            b=0

            for i in range(len(weights1)):
                for j in range(len(weights1[i])):
                    for k in range(len(weights1[i][j])):

                        b =max(b, weights1[i][j][k] != weights2[i][j][k])

            b = (b!=0)
            bb = bb * b
            solver.add_constraint(model, bb==1)

        # Train the neural network
            for order in range(len(sol_layers)):
                for sol in sol_layers[order]:

                    output_NN1 = nn.activation_function(model, solver, sol, weights1, nb_hidden_layers, nb_neurons, optimalval)
                    output_NN2 = nn.activation_function(model, solver, sol, weights2, nb_hidden_layers, nb_neurons, optimalval)
                    if order == 0:
                        solver.add_constraint(model, output_NN1 == 1)
                        solver.add_constraint(model, output_NN2 == 1)
                    else:
                        solver.add_constraint(model, output_NN1 == 0)
                        solver.add_constraint(model, output_NN2 == 0)


        # Compare the result of 2 different neural networks for the same solution

        tasks_starts = []
        for i in range(n):
            for j in range(m):
                tasks_starts.append(model.start_of(variables[i][j]))

        solver.add_constraint(model, outputvar_NN1 == nn.activation_function(model, solver, tasks_starts, weights1, nb_hidden_layers, nb_neurons, optimalval))
        print(outputvar_NN1)

        if len(list_weights) == 2:
            solver.add_constraint(model, outputvar_NN2 == nn.activation_function(model, solver, tasks_starts, weights2, nb_hidden_layers, nb_neurons, optimalval))
            print(outputvar_NN2)
            solver.add_constraint(model, outputvar_NN1 != outputvar_NN2)

            # if it > 5:
            #     solver.add_constraint(model, outputvar_NN1 == 1)
            #     solver.add_constraint(model, outputvar_NN2 == 1)
            # else:
            #     solver.add_constraint(model, outputvar_NN1 != outputvar_NN2)
        else:
            solver.add_constraint(model, outputvar_NN1 == 1)
        

        # ------------ Solve the model
        print("\nSolving the model...")
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)
        print("The number of solutions generated is :",nb_solution)

        list = []
        if type_operation == "plus":
            for sol in msol:
                list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))

        if len(list) == 0:
            print("Aucune solution générée à l'itération ", it)
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
        print("Model solved !")

        # ---------------- Interaction with the user
        list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m)
        print("Il y a {} solution(s)".format(len(pref)))

        sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)

        list_min_obj_global.append(min(list_obj))
        print("Objective function global :", list_min_obj_global)

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user)

    #------------------ Condition d'arrêt ------------------
        tps += runtime
        it += 1
        criterion = (tps < tps_max) and (it < it_max)
        fm.stopCondition(it, it_max, tps, tps_max)
        


    resultats_globaux.update({file: [list_min_obj, list_min_obj_global]})
    return list_min_obj, list_min_obj_global


def main():
    # Code principal du script
    print("Début du programme")
    list_min_obj, list_min_obj_global = main_nn({}, '../file_with_optimal_val/la04.txt', 2, 10, 15, 1, [1,1], 100, 10, "plus")
    
    print(list_min_obj)
    print(list_min_obj_global)
    # # Afficher les deux plots à l'écran (optionnel)
    # plt.figure(fig1.number)
    # plt.show()

    # plt.figure(fig2.number)
    # plt.show()


# Appeler la fonction main() si ce fichier est le point d'entrée du programme
if __name__ == "__main__":
    main()