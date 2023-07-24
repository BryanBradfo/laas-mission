import clustering as cl
import numpy as np
from docplex.cp.model import *
import FunctionMain as fm

#------------Calcul de la distance de binaire-------------------------

def int_diff(x,y):
    return int(x!=y)
#___________________________________________________________________________________________________________________________________________________________________

#---------------------Calcul de la distance de manhattan binaire---------------------
def manhattan_binaire_distance(sol1, sol2):
    sol1np=np.array(sol1)
    sol2np=np.array(sol2)
    sum = 0
    for i in range(len(sol1)):
        sum += int_diff(sol1[i], sol2[i])
    return sum
#___________________________________________________________________________________________________________________________________________________________________
#---------------------Calcul de la distance de manhattan binaire (solution-variable)---------------------
def manhattan_binaire_distance_contrainte(sol1, var):
    sum = 0
    for i in range(len(sol1)):
        sum += diff(sol1[i], var[i])
    return sum
#___________________________________________________________________________________________________________________________________________________________________



#---------------------Calcul du rayon binaire de chaque solution---------------------
def rayon_binaire_cluster(sol, list_sol):
    
    rayon = manhattan_binaire_distance(sol, list_sol[0])
    for sol2 in list_sol:
        rayon = min(rayon, manhattan_binaire_distance(sol, sol2))
    if rayon >= 1 : return rayon - 1
    return rayon
#___________________________________________________________________________________________________________________________________________________________________

#---------------------Liste du rayon binaire de chaque solution en fonction du layer---------------------
def list_rayon_binaire_cluster(n, m, list_layers):
    list_rayon_layers = []
    list_sol_rayon = []
    list_start_sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)

    
    for i in range(len(list_layers)):
        #Remplissage de la liste des starts des solutions des layers différents
        #De celui de la solution dont on calcule le rayon
        list_other_sol = []
        for j in range(len(list_layers)):
            if j != i:
                list_pas_i = list_start_sol_layers[j]
                for sol_pas_i in list_pas_i:
                    list_other_sol.append(sol_pas_i)

        #Calcul du rayon de chaque solution du layer i et ajout dans la liste des rayons du layer i
        list_rayon = []
        for sol in list_start_sol_layers[i]:
            r = rayon_binaire_cluster(sol, list_other_sol)
            list_rayon.append(r)
            list_sol_rayon.append([sol, r])
        list_rayon_layers.append(list_rayon)
    return list_rayon_layers, list_start_sol_layers, list_sol_rayon
#___________________________________________________________________________________________________________________________________________________________________

#---------------------centroides des clusters---------------------
# def centroides_clusters(n, m, list_clusters_layers, list_sol_rayon):

#     list_centroides_layers = []
#     for i in range(len(list_clusters_layers)):
#         list_centroides = []
#         for j in range(len(list_clusters_layers[i])):
#             list_sol = list_clusters_layers[i][j]
#             list_sol_rayon = []
#             for sol in list_sol:
#                 start_sol = start_sol(n, m, sol)

#                 list_sol_rayon.append()
#             list_centroides.append(list_sol[list_sol_rayon.index(max(list_sol_rayon))])
#         list_centroides_layers.append(list_centroides)
#     return list_centroides_layers

def centroides_clusters(n, m, list_clusters_layers):

    list_centroides_layers = []
    for i in range(len(list_clusters_layers)):
        list_centroides = []
        for j in range(len(list_clusters_layers[i])):
            list_sol = list_clusters_layers[i][j]
            list_sol_rayon = []
            for sol in list_sol:
                list_sol_rayon.append(sol[1])
                centroide = list_sol[list_sol_rayon.index(max(list_sol_rayon))][0]
                start_centroide = fm.start_sol(n, m, centroide)
            list_centroides.append(start_centroide)
        list_centroides_layers.append(list_centroides)
    return list_centroides_layers
#________________________________________________________________________
  #---------------------Clustering binaire---------------------
# def my_clustering_binaire(n, m, list_rayon_layers, list_layers):
#     list_cluster_layers = []
#     list_start_sol_layers = list_list_list_start_of_tasks(n, m, list_layers)
#     for i in range(len(list_layers)):
#         list_layer = []
#         list_cluster = []
#         layer_sol_i = list_layers[i]
#         if len(layer_sol_i)> 1:
#             layer_i = list_start_sol_layers[i]
#             for j in range(len(layer_i)):
#                 sol1_starts = layer_i[j]
#                 sol1 = layer_sol_i[j]
#                 for k in range(j+1, len(layer_i)):
#                     sol2_starts = layer_i[k]
#                     sol2 = layer_sol_i[k]
#                     dist = manhattan_binaire_distance(n, m, sol1_starts, sol2_starts)
#                     if dist <= list_rayon_layers[i][j] or dist <= list_rayon_layers[i][k]:
#                         for indice, cluster in enumerate(list_layer):
#                             if sol1 in cluster:
#                                 list_layer[indice].append(sol2)
#                                 break
#                             elif sol2 in cluster:
#                                 list_layer[indice].append(sol1)
#                                 break
                        
#                         # if sol1 not in list_cluster: list_cluster.append(sol1)
#                         # if sol2 not in list_cluster: list_cluster.append(sol2)
#                         # list_layer.append(list_cluster)
#             list_cluster_layers.append(list_layer)
#         else:
#             list_cluster.append(layer_sol_i[0])
#             list_cluster_layers.append(list_cluster)
        
            
#     return list_cluster_layers
def concatener(liste_de_listes):
    resultats = []
    liste = liste_de_listes
    while liste:
        courante = liste.pop(0)
        fusionnee = list(courante)
        resultat = list(courante)
        i = 0
        while i < len(liste):
            sous_liste = liste[i]
            if any(item in fusionnee for item in sous_liste):
                fusion = fusionnee + sous_liste
                resultat = []
                for element in fusion:
                    if element not in resultat:
                        resultat.append(element)
                liste.pop(i)
            else:
                i += 1
        resultats.append(resultat)
    return resultats


def my_clustering_binaire(n, m, list_rayon_layers, list_layers):
    list_cluster_layers = []
    list_start_sol_layers = fm.list_list_list_start_of_tasks(n, m, list_layers)
    for i in range(len(list_layers)):
        list_layer_temp = []
        layer_sol_i = list_layers[i]
        layer_i = list_start_sol_layers[i]
        # print("len :", len(layer_i))
        for j in range(len(layer_i)):
            sol1_starts = layer_i[j]
            sol1 = layer_sol_i[j]
            list_cluster_temp = [[sol1, list_rayon_layers[i][j]]]
            for k in range(j+1, len(layer_i)):
                sol2_starts = layer_i[k]
                sol2 = layer_sol_i[k]
                # print(i, j, k)
                dist = manhattan_binaire_distance(sol1_starts, sol2_starts)
                # print(dist <= list_rayon_layers[i][j] or dist <= list_rayon_layers[i][k])
                if dist <= list_rayon_layers[i][j] or dist <= list_rayon_layers[i][k]:
                    list_cluster_temp.append([sol2, list_rayon_layers[i][k]])
            list_layer_temp.append(list_cluster_temp)
        list_layer = concatener(list_layer_temp)         
        list_cluster_layers.append(list_layer)
        
            
    return list_cluster_layers

#___________________________________________________________________________________________________________________________________________________________________
