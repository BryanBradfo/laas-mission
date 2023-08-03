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




def main_nn(resultats_globaux, file, nb_layers, k, k_k, nb_hidden_layers, nb_neurons, tps_max, it_max, type_operation, type_user="user_reg", display_sol=False, display_start=False, display_matrix=False):
    #############################
    ### Main program ###
    #############################

    print("\n--------Main program is loading...---------")

    # --------- Interaction with the solver
    data = []
    n, m, data, T_machine, _, duration, optimalval = fm.get_data_from_file(file)

    # --------- Call Solver constructor in Solver.py and create the variables of the model
    model, solver, _ = fm.initialize_solver(data, n, m, duration)

    # --------- Add the scheduling constraints to the model
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
    
    # Ask the user to enter his preferences and get the preferences
    list_obj, pref, list_layers = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)

    # Vector of the start time of each task of each preference
    starts = user.start_pref(n, m, display_start)

    # Matrix of the start time of each task of each preference
    matrix = user.matrix_pref(n, m, display_matrix)

    # Testing the order of preferences and the differences between solutions
    fm.test(n, m, user)

    print("list layers : ",list_layers)

    # Get the solutions into a good format
    sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)


    #____________________ End first iteration____________________#



    #############################################
    #### New iterations with neural network  ####
    #############################################

    ###  -------------- Iteration of the solver with the preferences
    it = 1
    tps = runtime
    # List of the objective value of the best solutions found at each iteration
    list_min_obj = [min(list_obj)]
    # List of the objective value of the best solutions found so far
    list_min_obj_global = [min(list_obj)]

    # Stopping criterion
    criterion = (tps < tps_max) and (it < it_max) 
    desagreement = True

    # ----------------- Add the preferences to the model
    while criterion :
        print("\n--------Iteration {}---------".format(it))

        # Check if it exists at least one perfect neural networks based on the previous solutions 
        # independently from the scheduling problem
        list_weights = nn.find_perfect_NN(file, sol_layers, nb_hidden_layers, nb_neurons)

        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, _ = fm.initialize_solver(data, n, m, duration)

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
        print("The number of solutions generated is :",nb_solution)

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
                    list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
            else:
                for sol in msol:
                    list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))
        
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol))
        
  
        list_min_obj.append(min(list))

        # ------------ Display the result
        fm.display_solution(msol, display_sol)
        print("Model solved !")

        # ---------------- Interaction with the user
        list_obj, pref, list_layers = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)
        print("Il y a {} solution(s)".format(len(pref)))

        sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)

        list_min_obj_global.append(min(list_obj))
        print("Objective function global :", list_min_obj_global)

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user, type_operation)

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
    list_min_obj, list_min_obj_global = main_nn({}, '../file_with_optimal_val/la04.txt', 2, 10, 15, 1, [1,1], 100, 10, "plus", type_user ="other")
    
    print(list_min_obj)
    print(list_min_obj_global)


# Appeler la fonction main() si ce fichier est le point d'entrée du programme
if __name__ == "__main__":
    main()