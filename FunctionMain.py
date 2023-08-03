
import clustering_agglo.clustering as cl
import numpy as np
from docplex.cp.model import *
from docplex.cp.model import *
from docplex.cp.config import get_default
import numpy as np
from Solver import *
from User import *

#--------------------- Read the data --------------------------------

# Function to get the main data from the file
def get_data_from_file(file):

    optimalval = -1

    data = []
    with open(file, 'r') as f:    
        for line in f:
            if line.startswith('optimalval ='):
                line_splitted = line.strip().split('=')
                # Get the optimal value of the instance
                optimalval = int(line_splitted[1])
            else:
                data.append(line.strip().split())

    n = int(data[0][0])
    m = int(data[0][1])

    T_machine = []
    T_duration = []

    for i in range(1,n+1):
        for j in range(0, 2*m, 2):
            # Vectors of the machines and the duration of the tasks
            T_machine.append(int(data[i][j]))
            T_duration.append(int(data[i][j+1]))

    duration = np.zeros((n, m))

    for i in range(n):
        for j in range(m):
            ind_machine = int(T_machine[i*m + j])
            # Matrix of the duration of the tasks per job
            duration[i][ind_machine] = T_duration[i*m + j]

    return n, m, data, T_machine, T_duration, duration, optimalval


#--------------------- Initialize the solver --------------------------------

def initialize_solver(data, n, m, duration):

    solver = Solver(data)
    model = CpoModel() 

    # --------- Create the model variables ---------
    tasks = solver.create_variables(model, n, m, duration)

    print("\nSolver initialized !")

    return model, solver, tasks


# --------------------- Display solution --------------------------------

def display_solution(msol, bool_display):
    if bool_display:
        for sol in msol:
            sol.write()


# ___________________Interaction with the user___________________________

# --------------------- User preferences --------------------------------

def user_preferences(msol, user, nbLayer, n, m, type_operation="plus", type_user="user_reg", optimalval=None):

    print("\nRanking the solutions...")	
    # The user ranks the solutions according to their preferences
    if type_user == "user_reg":
        list_obj, list_layer = user.rank_by_pref_regularity(nbLayer, msol, type_operation, n, m)
    else:
        list_obj, list_layer = user.rank_by_pref_makespan(nbLayer, msol)
    
    print("Solutions classed !")

    print("\nCreating preferences...")
    pref = user.getPreferences()
    print("Preferences created !")

    return list_obj, pref, list_layer


#---------------------- Tests on preferences---------------------------

def test(n, m, user, type_operation):

    print("\nTesting the order of the preferences...")
    pref = user.getPreferences()

    if user.test_preferences(pref, type_operation, n, m):
        print("\tThe order of the preferences is coherent")
    else:
        print("\tThe order of the preferences is not coherent")

    print("\nTesting differences between solutions...")
    matrix = user.matrix_pref(n, m, False)
    if user.test_differences_sol(matrix):
        print("\tAll the solutions are different")
    else:
        print("\tSome solutions are the same, all the solutions must be different")


#--------------------- Objective: find new solutions (different from the previous ones) ----------------------------------

def update_variables_new_constraint(n, m, pref, model, solver):

    # stop = int(input("Do you want to continue ? True(1) or False(0)"))

    bb = model.integer_var(0,1)
    solver.add_variable(bb)
    bb=1

    list_variables = solver.get_variables()
    variables = list_variables[0]

    for sol in pref:
        b = model.integer_var(0,1)
        solver.add_variable(b)
        b=0

        for i in range(n):
            for j in range(m):

                var_sol = sol.get_value("T{}-{}".format(i,j))
                b =max(b,var_sol.start != model.start_of(variables[i][j]))

        b = (b!=0)
        bb = bb * b
    # At least one feature of each solution must be different from the previous solutions
    solver.add_constraint(model, bb==1)

    return variables


def choose_best_clusters(layers):
    nb_clusters = []
    for i in range(len(layers)):
        data = layers[i]
        # print("-------------- Layer for clustering", i, "-----------------")
        # print(len(data))
        
        if len(data) > 2: 
            # Compute the number of clusters with the silhouette index
            list, k_max, leaves_max, runtime = cl.silhouette(data)
            nb_clusters.append(k_max)

            # print(len(data))
            # print("D'après l'indice de silhouette, nb clusters =", k_max ,", nb feuilles = ", leaves_max , 
            #     " runtime = ", runtime ,"s \n")
            
        else:
            # print("Pas assez de données pour faire un clustering : On a juste ", len(data), " données")
            # print("numbre de clusters = ", len(data),"\n")
            nb_clusters.append(len(data))
    return nb_clusters


#------------ Computation of the manhattan distance -------------------------

def abs_int(x,y):
    return max(x-y,y-x)

def abs_(L1,L2):
    L=[]
    for i in range(len(L1)):
        L.append(abs_int(L1[i],L2[i]))
    return L

def sum_(L):
    s=0
    for i in range(len(L)):
        s+=L[i]
    return s

def manhattan_distance(sol1, sol2):
    sol1np=np.array(sol1)
    sol2np=np.array(sol2)
    return sum_(abs_(sol1np,sol2np))

def rayon_cluster(avg, list_sol):
    rayon = 0
    for sol in list_sol:
        rayon = max(rayon, manhattan_distance(avg, sol))
    return rayon


def average_computation(data, nb_cluster):
        
    # Clustering
    k , leaves , labels, runtime = cl.my_agglo_k(data, nb_cluster, 'single')
    # print("Le k dans average computation est : ",k)

    avg=[[0 for i in range(len(data[0]))] for i in range(k)]
    card=[0 for i in range(k) ]

    for i in range(len(data)):
        # Compute the cardinality of each cluster
        card[labels[i]]+=1
        avg[labels[i]]=[avg[labels[i]][k]+data[i][k] for k in range(len(data[i]))]
    
    for i in range(k):
        # Compute the average
        avg[i]=[avg[i][k]/card[i] for k in range(len(data[0]))]

    return k, avg, labels
        

# Return the list of the solutions that are the closest to the average of its cluster
def solution_average(k, data, labels, avg):
    the_ones=[None for i in range(k)]
    for i in range(len(data)):
        if(the_ones[labels[i]]==None or manhattan_distance(data[i],avg[labels[i]])<manhattan_distance(the_ones[labels[i]],avg[labels[i]])):
                the_ones[labels[i]]=data[i]
    return the_ones


            
#___________________________________________________________________________________________________________________________________________________________________

#------------ Transformation of the CPOSolutionResult into a list of starts (features) -------------------------
def start_sol(n, m, sol):
    starts = []
    for i in range(n):
        for j in range(m):
            var_sol = sol.get_value("T{}-{}".format(i,j))
            starts.append(var_sol.start)
    return starts
#___________________________________________________________________________________________________________________________________________________________________

# For each layer, for each solution in the layer, we have a list of starts (features)
def list_list_list_start_of_tasks(n, m, list_layers):
    list_start_sol_layers = []
    for i in range(len(list_layers)):
        list_start_sol = []
        for j in range(len(list_layers[i])):
            list_start = start_sol(n, m, list_layers[i][j])
            list_start_sol.append(list_start)
        list_start_sol_layers.append(list_start_sol)
    return list_start_sol_layers
#___________________________________________________________________________________________________________________________________________________________________

#---------------------- Stopping condition ---------------------------

def stopCondition(it, it_max, tps, tps_max):
    if (it >= it_max):
        print("The user has reached the maximum number of iterations !")
    elif (tps >= tps_max):
        print("The user has reached the maximum time !")


    


    
