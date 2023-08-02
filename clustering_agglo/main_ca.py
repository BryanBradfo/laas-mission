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
import clustering as cl
sys.path.append("..")
from Solver import *
from User import *
import FunctionMain as fm


# Creation of a function for a call from script folder (in order to compare each approach in a parent folder)
def main_ca(resultats_globaux, file, nb_layers, k, k_k, tps_max, it_max, type_operation, display_sol=False, display_start=False, display_matrix=False):

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

    # ----------- Interaction with the user
    print("\n--------Interaction with the user...---------")
    print("\nCreating the user...")
    user = User()
    print("User created !")

    # Get the variables of the model
    variables = solver.get_variables()

    # Return multiple lists of the preferences of the user
    list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m, type_operation)

    # Vector of the start time of each task of each preference
    starts = user.start_pref(n, m, display_start)

    # Matrix of the start time of each task of each preference
    matrix = user.matrix_pref(n, m, display_matrix)

    # Testing the order of preferences and the differences between solutions
    fm.test(n, m, user)
    
    #____________________ End first iteration____________________#


    ####################################################################
    #### NOUVELLES SOLUTIONS ET NOUVEAUX CLUSTERING A CHAQUE ITERATION
    ####################################################################


    ###  -------------- Iteration of the solver with the preferences
    # Initialization of the counter of iteration
    it = 1
    # Initialization of the counter of time
    tps = runtime
    # Initialization of the list of the objective function (that we would like to plot later)
    list_min_obj = [min(list_obj)]
    # Initialization of the list of the objective function globally (that we would like to plot later)
    list_min_obj_global = [min(list_obj)]
    # Initialization of the stop criterion
    criterion = (tps < tps_max) and (it < it_max) 

    # ----------------- The loop for the problem (until a stop criterion is reached)
    while criterion :

        print("\n--------Iteration {}---------".format(it))

        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, tasks = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
        # --------- Add the constraints considering the clustering
        if it > 1:
            model, variables = solver.create_constraints(model, n, m, list_min_obj_global[it-1], T_machine)
        else :
            model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)
        
        #------------------ Layers creation 
        layers = cl.create_layers_fixed(list_layers)

        # Get the list of number of clusters for each layer
        nb_clusters = fm.choose_best_clusters(layers)

        # The default value of the radius of the clusters if there is only one solution in the layer
        default_value_rayon = 5 

        # Iterating on layers
        for l in range(len(layers)):
            data = layers[l]
            k = nb_clusters[l]

            if l > 0:
                #------------------ If there is no solution in the layer, we skip this layer we add a constraint to the model
                if(len(data)==0):
                    continue
                #------------------ If there is only one solution in the layer, we add a constraint to the model
                elif (len(data) == 1):
                    solver.add_constraint(model, fm.manhattan_distance(data[0], [model.start_of(variables[i//m][i%m]) for i in range(n*m)]) > default_value_rayon + l)
                    continue
                else :
                #------------------ Get the average of each cluster
                    k, avg, labels = fm.average_computation(data, k)

                #------------------ Get the solutions which is the closest to the average of each cluster
                    the_ones = fm.solution_average(k, data, labels, avg)
                    
                #------------------ Add constraints: solutions must be distant from cluster centers, in each layer, by a distance greater than the cluster radius + l
                    #------------------ List of layer l cluster solutions
                    for i in range(k):
                        sol_cluster=[]
                        for j in range(len(data)):
                            if labels[j]==i:
                                sol_cluster.append(data[j])
                    #------------------ Adding constraints
                        solver.add_constraint(model, fm.manhattan_distance(the_ones[i],[ model.start_of(variables[i//m][i%m]) for i in range(n*m)]) >  fm.rayon_cluster(the_ones[i], sol_cluster) + l)
                

        # ------------ Solve the model
        # msol, nb_solution, runtime = solver.solve(model, k_k, n, m, it, T_machine, optimalval, list_search_type[it%4])
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)

        # Adding the objective value of each solution to a list
        list = []

        # Distinction between type_operation = "plus" or "fois"
        if type_operation == "plus":
            for sol in msol:
                list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))
        
        # If there is no solution generated, we add the last objective value to the list
        if len(list) == 0:
            print("Aucune solution générée à l'itération ", it)
            list_min_obj.append(list_min_obj[-1])
            list_min_obj_global.append(list_min_obj_global[-1])
            
            #------------------ Stop criterion ------------------
            tps += runtime
            it += 1            
            criterion = (tps < tps_max) and (it < it_max) 
            fm.stopCondition(it, it_max, tps, tps_max)
            continue
        
        # ------------ Adding the min of objective function among the solutions generated to the list of objective function (for later display)
        list_min_obj.append(min(list))

        # ------------ Display the result
        fm.display_solution(msol, display_sol)

        # ---------------- Interaction with the user
        list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m, type_operation)

        # ------------ Adding the min of objective function among all solutions generated to the list of objective function (for later display)
        list_min_obj_global.append(min(list_obj))

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user)

    #------------------ Stop criterion ------------------
        tps += runtime
        criterion = (tps < tps_max) and (it < it_max)
        fm.stopCondition(it, it_max, tps, tps_max)
        it += 1

    # Add to a dictionary (which is a global variable) for a plot in a parent file
    resultats_globaux.update({file: [list_min_obj, list_min_obj_global]})
    return list_min_obj, list_min_obj_global

def main():
    # Main program
    print("Début du programme")
    list_min_obj, list_min_obj_global = main_ca({}, '../file_with_optimal_val/la04.txt', 2, 10, 15, 100, 10, "plus")
    
    # # Plot the two plots (optional)
    # plt.figure(fig1.number)
    # plt.show()

    # plt.figure(fig2.number)
    # plt.show()

# Call the main() function if this file is the program's entry point
if __name__ == "__main__":
    main()