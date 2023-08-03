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

# Creation of a function for a call from script folder (in order to compare each approach in a parent folder)
def main_dt(resultats_globaux, file, nb_layers, k, k_k, tps_max, it_max, type_operation, type_user="user_reg", nb_trees=1, display_sol=False, display_start=False, display_matrix=False):

    #############################
    ### Main program ###
    #############################
    #-----------------------------First iteration-----------------------------#

    print("\n--------Main program is loading...---------")

    # --------- Interaction with the solver
    data = []

    # --------- Get essential information from the file
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

    list_obj, pref, list_layers = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)

    # Vector of the start time of each task of each preference
    starts = user.start_pref(n, m, display_start)

    # Matrix of the start time of each task of each preference
    matrix = user.matrix_pref(n, m, display_matrix)

    # Testing the order of preferences and the differences between solutions
    fm.test(n, m, user, type_operation)
    
    #____________________ End first iteration____________________#

    ####################################################################
    #### Arbre de décision : RECHERCHE DE NOUVELLES SOLUTIONS 
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
    # Initialization of the list of the number of iteration for each file (for future plot)
    it_final_BDT = []

    # ----------------- The loop for the problem (until a stop criterion is reached)
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
        
        #----------Add news variables "order1" and "order_i" to the model---------------
        list_order = []
        for i in range(nb_dt):
            order = model.binary_var(name="order"+str(i+1))
            list_order.append(order)
            solver.add_variable(order)
    
        # --------- Add the new constraints to the model (concerning the order)
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
                    list.append(user.objectiveFunction(sol) + user.objectiveFunctionRegularity(sol, n, m))
            else:
                for sol in msol:
                    list.append(user.objectiveFunction(sol) * user.objectiveFunctionRegularity(sol, n, m))
        else:
            for sol in msol:
                list.append(user.objectiveFunction(sol))

        # Treating the case when there is no solution
        if len(list) == 0:
            print("No solution at iteration", it)
            list_min_obj.append(list_min_obj[-1])
            list_min_obj_global.append(list_min_obj_global[-1])
            
            #------------------ Stop criterion ------------------
            tps += runtime
            it += 1            
            criterion = (tps < tps_max) and (it < it_max) 
            fm.stopCondition(it, it_max, tps, tps_max)
            continue
        
        # ------------ Adding the min of objective function among the solutions generated to 
        # the list of objective function (for later display)
        list_min_obj.append(min(list))
        print("Objective function :", list_min_obj)

        # ------------ Display the result
        fm.display_solution(msol, display_sol)
        print("Model solved !")

        # ---------------- Interaction with the user
        list_obj, pref, list_layers = fm.user_preferences(msol, user, nb_layers, n, m, type_operation, type_user, optimalval)
        print("Il y a {} solution(s)".format(len(pref)))

        # ------------ Adding the min of objective function among all solutions generated to 
        # the list of objective function (for later display)
        list_min_obj_global.append(min(list_obj))
        print("Objective function global :", list_min_obj_global)

        # Vector of the start time of each task of each preference
        starts = user.start_pref(n, m, display_start)

        # Matrix of the start time of each task of each preference
        matrix = user.matrix_pref(n, m, display_matrix)

        # Testing the order of preferences and the differences between solutions
        fm.test(n, m, user)

    #------------------ Stop criterion ------------------
        tps += runtime
        it += 1
        print("next iteration", it)
        criterion = (tps < tps_max) and (it < it_max) 
        fm.stopCondition(it, it_max, tps, tps_max)

    it_final_BDT.append(it)

    #------------------- Results ---------------------
    resultats_globaux.update({file: [list_min_obj, list_min_obj_global]})
    return list_min_obj, list_min_obj_global


def main():
    # Main program
    print("Début du programme")
    list_min_obj, list_min_obj_global = main_dt({}, '../file_with_optimal_val/la04.txt', 2, 10, 15, 100, 10, "plus","other", 3)
    print(list_min_obj)
    print(list_min_obj_global)
    print("Fin du programme")
    

# Call the main() function if this file is the program's entry point
if __name__ == "__main__":
    main()




