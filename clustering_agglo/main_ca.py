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


def main_ca(file, plot_name, nb_layers, k, k_k, tps_max, it_max, type_operation, display_sol=False, display_start=False, display_matrix=False):

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

    list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m)

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
    it = 1
    tps = runtime
    list_min_obj = [min(list_obj)]
    list_min_obj_global = [min(list_obj)]

    criterion = (tps < tps_max) and (it < it_max) 

    # ----------------- Add the preferences to the model
    while criterion :
        it += 1
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
            #------------------ Définition du nombre de clusters par layer (liste des nb de clusters par layer)
        nb_clusters = fm.choose_best_clusters(layers)

        default_value_rayon = 5 

        for l in range(len(layers)):
            data = layers[l]
            k = nb_clusters[l]

            if l > 0:
                #------------------ If there is only one solution in the layer, we add a constraint to the model
                if(len(data)==0):
                    continue
                elif (len(data) == 1):
                    solver.add_constraint(model, fm.manhattan_distance(data[0], [model.start_of(variables[i//m][i%m]) for i in range(n*m)]) > default_value_rayon + l)
                    continue
                else :
                #------------------ Get the average of each cluster
                    k, avg, labels = fm.average_computation(data, k)

                #------------------ Get the solutions which is the closest to the average of each cluster
                    the_ones = fm.solution_average(k, data, labels, avg)
                    
                #------------------ Ajout de contraintes, les solutions doivent etre distantes des centres de clusters, en chaque layer , d'une distance supérieure au rayon du cluster + l
                    #------------------ Liste des solutions des clusters de la layer l

                    for i in range(k):
                        sol_cluster=[]
                        for j in range(len(data)):
                            if labels[j]==i:
                                sol_cluster.append(data[j])
                    #------------------ Ajout des contraintes
                        solver.add_constraint(model, fm.manhattan_distance(the_ones[i],[ model.start_of(variables[i//m][i%m]) for i in range(n*m)]) >  fm.rayon_cluster(the_ones[i], sol_cluster) + l)
                

        # ------------ Solve the model
        # msol, nb_solution, runtime = solver.solve(model, k_k, n, m, it, T_machine, optimalval, list_search_type[it%4])
        msol, nb_solution, runtime = solver.solve(model, k_k, n, m, variables)
        list = []
        if type_operation == "plus":
            for sol in msol:
                list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))

        list_min_obj.append(min(list))

        # ------------ Display the result
        fm.display_solution(msol, display_sol)

        # ---------------- Interaction with the user
        list_indice, list_obj, pref, list_layers, list_equal = fm.user_preferences(msol, user, nb_layers, n, m)

        list_min_obj_global.append(min(list_obj))

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user)


    #------------------ Condition d'arrêt ------------------
        tps += runtime
        criterion = (tps < tps_max) and (it < it_max)
        fm.stopCondition(it, it_max, tps, tps_max)


    ####################################################################
    #### Plotting the results 
    ####################################################################

    plt.plot([i for i in range(it)], list_min_obj, label='min obj', marker='o')
    plt.xlabel("Iteration")
    plt.ylabel("objective value")
    plt.title("Agglo clustering: Evolution of the best objective value for generate solutions")
    plt.xticks(range(it))
    plt.legend()
    name = "plot_ca_"+plot_name+".png"
    plt.savefig(name)
    plt.close()
    #Initialiser le plt

    plt.plot([i for i in range(it)], list_min_obj_global, label='min obj', marker='o')
    plt.xlabel("Iteration")
    plt.ylabel("objective value")
    plt.title("Agglo clustering: Global evolution of the best objective value for every generated solutions")
    plt.xticks(range(it))
    plt.legend()
    name = "plot_global_ca_"+plot_name+".png"
    plt.savefig(name)
    plt.close()

    return list_min_obj, list_min_obj_global



