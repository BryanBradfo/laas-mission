
import clustering as cl
import numpy as np
from docplex.cp.model import *
from docplex.cp.config import get_default
import numpy as np
from Solver import *
from User import *
#---------------------Lecture des données--------------------------------
def lire_fichier(file):
    optimalval = -1

    data = []
    with open(file, 'r') as f:    
        for line in f:
            if line.startswith('optimalval ='):
                line_splitted = line.strip().split('=')
                optimalval = int(line_splitted[1])
            else:
                data.append(line.strip().split())

    n = int(data[0][0])
    m = int(data[0][1])

    T_machine = []
    T_duration = []

    for i in range(1,n+1):
        for j in range(0, 2*m, 2):
            T_machine.append(int(data[i][j]))
            T_duration.append(int(data[i][j+1]))

    duration = np.zeros((n, m))

    for i in range(n):
        for j in range(m):
            ind_machine = int(T_machine[i*m + j])
            duration[i][ind_machine] = T_duration[i*m + j]
    return n, m, data, T_machine, T_duration, duration, optimalval
#--------------------------------------------------------------------------
#---------------------Solutions à trouver différentes des anciennes----------------------------------
def constraintNewOldSolutionDifferent(n, m, pref, model, solver):
     

    # stop = int(input("Do you want to continue ? True(1) or False(0)"))

    bb = integer_var(0,1)
    solver.add_variable(bb)
    bb=1

    list_variables = solver.get_variables()
    variables = list_variables[0]

    for sol in pref:
        b = integer_var(0,1)
        solver.add_variable(b)
        b=0

        for i in range(n):
            for j in range(m):

                var_sol = sol.get_value("T{}-{}".format(i,j))
                #a = model.interval_var(start = sol[variables[i][j]].start, end= sol[variables[i][j]].end, size=int(duration[i][j]), name="a{}{}".format(i,j))
                #b =max(b,logical_or((model.start_of(a) != model.start_of(variables[i][j])), (model.end_of(a) != model.end_of(variables[i][j]))))
                
                b =max(b,logical_or(var_sol.start != model.start_of(variables[i][j]), var_sol.end != model.end_of(variables[i][j])))
        b = (b!=0)
        bb = bb * b
    solver.add_constraint(bb==1)
#--------------------------------------------------------------------------

#------------Calcul de la distance de manhattan-------------------------
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

def theOnes(n, m, data, nb_cluster):
        if(len(data)==1):
            return data[0]
        k = nb_cluster

        k , leaves , labels, runtime = cl.my_agglo_k(data, k, 'single')

        avg=[[0 for i in range(len(data[0]))] for i in range(k)]
        card=[0 for i in range(k) ]

        for i in range(len(data)):
            card[labels[i]]+=1
            avg[labels[i]]=[avg[labels[i]][k]+data[i][k] for k in range(len(data[i]))]
        
        for i in range(k):
            avg[i]=[avg[i][k]/card[i] for k in range(len(data[0]))]
        
        the_ones=[None for i in range(k)]
        for i in range(len(data)):
            if(the_ones[labels[i]]==None or manhattan_distance(data[i],avg[labels[i]])<manhattan_distance(the_ones[labels[i]],avg[labels[i]])):
                    the_ones[labels[i]]=data[i]
        return the_ones
            
#___________________________________________________________________________________________________________________________________________________________________

#------------Interaction with the user-------------------------

#----------------------Test Ordre Preferences---------------------------
def testOrderPreferences(user):
    print("\nTesting order of preferences...")
    pref = user.getPreferences()
    if user.test_preferences(pref):
        print("\tL'ordre des préférences est cohérente")
    else:
        print("\tL'ordre des préférences n'est pas cohérente")
#---------------------------------------------------------------------
#----------------------Conditions d'arrêt---------------------------
def testDifferentSolutions(n, m, user):
    print("\nTesting differences between solutions...")
    matrix = user.matrix_pref(n, m, False)
    if user.test_differences_sol(matrix):
        print("\tToutes les solutions sont différentes")
    else:
        print("\tLes solutions ne sont pas toutes différentes")
#---------------------------------------------------------------------

def interactionUtilisateur(n, m, variables, msol, user, verbose):
    print("\n--------Interaction with the user...---------")

    print("\nClassing solutions...")	
    list_indice, list_equal, list_obj = user.classerSolutions(msol)
    print(list_obj)
    # print(list_indice)
    print(list_equal)
    # print(list_indice)
    print("Solutions classed !")

    print("\nCreating preferences...")
    pref = user.getPreferences()
    print("Preferences created !")

    print("\nDisplaying preferences...")

    starts = user.start_pref(n, m, variables, verbose)

    matrix = user.matrix_pref(n, m, verbose)

    return starts, matrix, list_indice, list_equal, list_obj, pref
#---------------------------------------------------------------------


#----------------------Conditions d'arrêt---------------------------
def stopCondition(it, it_max, tps, tps_max):
    if (it == it_max):
        print("The user has reached the maximum number of iterations !")
    elif (tps >= tps_max):
        print("The user has reached the maximum time !")
#---------------------------------------------------------------------


def definirNbClusters(layers):
    nb_clusters = []
    for i in range(len(layers)):
        data = layers[i]
        print("-------------- Layer", i, "-----------------")
        # print(len(data))
        
        if len(data) > 2:
            list, k_max, leaves_max, runtime = cl.silhouette(data)
            nb_clusters.append(k_max)

            # print(len(data))
            print("D'après l'indice de silhouette, nb clusters =", k_max ,", nb feuilles = ", leaves_max , 
                " runtime = ", runtime ,"s \n")
            
        else:
            print("Pas assez de données pour faire un clustering : On a juste ", len(data), " données")
            print("numbre de clusters = ", len(data),"\n")
            nb_clusters.append(len(data))
    return nb_clusters


    
