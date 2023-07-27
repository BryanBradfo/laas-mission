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
from sklearn import tree

#############################
### Essentials functions ###
#############################
#import functionMain du dossier parent
import decision_tree as dt
sys.path.append("..")
from Solver import *
from User import *
import FunctionMain as fm

def main_dt(file, plot_name, nb_layers, k, k_k, tps_max, it_max, type_operation, display_sol=False, display_start=False, display_matrix=False):

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
    #### Arbre de décision : RECHERCHE DE NOUVELLES SOLUTIONS 
    ####################################################################


    ###  -------------- Iteration of the solver with the preferences
    it = 1
    tps = runtime
    list_min_obj = [min(list_obj)]
    list_min_obj_global = [min(list_obj)]
    criterion = (tps < tps_max) and (it < it_max) 

    # ----------------- Add the preferences to the model
    while criterion :
        
        print("\n--------Iteration {}---------".format(it))
        it += 1

        # --------- Compute decision trees---------------
        clf, feuilles_conditions = dt.my_decision_tree(n, m, list_layers)
        
        # --------- Call Solver constructor in Solver.py and create the variables of the model
        model, solver, starts = fm.initialize_solver(data, n, m, duration)

        # --------- Add the new constraints to the model (that solution must be different from the previous generated solutions)
        variables = fm.update_variables_new_constraint(n, m,  pref, model, solver)
        
        
        
        #----------Add new variable "order" to the model---------------
        order = model.binary_var(name="order")
        solver.add_variable(order)
        
    
        # --------- Add the new constraints to the model (concerning the order)
        list_variables = [model.start_of(variables[i//m][i%m]) for i in range(n*m)]
        constraint_list_of_tree = dt.constraint_tree(order,list_variables, feuilles_conditions)

        for constraint in constraint_list_of_tree:
            solver.add_constraint(model, constraint)
        solver.add_constraint(model, equal(order, 1))


        # ------------ Solve the model
        model, variables = solver.create_constraints(model, n, m, optimalval, T_machine)
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
    # Implementation of the decision tree

    print("\n--------Implementation of the decision tree...---------")
    print(len(feuilles_conditions)) 
    fig = plt.figure(figsize=(10,7))
    _ = tree.plot_tree(clf, 
                        class_names= ("false (0)", "true (1)" ), 
                        filled=True)
    name = "decision_tree_"+plot_name+".png"
    fig.savefig(name)
    plt.close()

    plt.plot([i for i in range(it)], list_min_obj, label='min obj', marker='o')
    plt.xlabel("Iteration")
    plt.ylabel("objective value")
    plt.title("Decision tree: Evolution of the best objective value for generate solutions")
    plt.xticks(range(it))
    plt.legend()
    name = "plot_dt_"+plot_name+".png"
    plt.savefig(name)
    plt.close()
    #Initialiser le plt

    plt.plot([i for i in range(it)], list_min_obj_global, label='min obj', marker='o')
    plt.xlabel("Iteration")
    plt.ylabel("objective value")
    plt.title("Decision tree: Global evolution of the best objective value for every generated solutions")
    plt.xticks(range(it))
    plt.legend()
    name = "plot_global_dt_"+plot_name+".png"
    plt.savefig(name)
    plt.close()

    return list_min_obj, list_min_obj_global



