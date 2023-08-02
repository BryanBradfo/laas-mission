import sys
import threading
import matplotlib.pyplot as plt
sys.path.append("../bdt")
import main_dt as mdt
sys.path.append("../clustering_agglo")
import main_ca as mca
sys.path.append("../Clustering_binaire")
import main_cb as mcb
sys.path.append("../neural_network")
import main_nn as mnn
sys.path.append("../optimal_value")
import main_optval as mov

import random
random.seed(10)

resultats_globaux_approche = []
resultats_globaux_files = []
list_methods = []


def main():
    #-----------------------------Parameters of every methods-----------------------------#
    #Names of files must be different
    # list_files = ['../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/ft10.txt', '../file_with_optimal_val/example.data']
    list_files = ['../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la02.txt']
    list_plot_name = ['la04', 'la03', 'la02', 'ft10', 'example']
    list_nb_layers = [5, 5, 5, 5, 5]
    list_k = [20, 20, 20, 20, 20]
    list_k_k = [15, 15, 15, 15, 15]
    list_tps_max = [100, 100, 100, 100, 100]
    list_it_max = [30, 30, 30, 10, 10]
    list_type_operation = ['fois', 'fois', 'fois', 'plus', 'plus']
    list_display_sol = [False, False, False, False, False]
    list_display_start = [False, False, False, False, False]
    list_display_matrix = [False, False, False, False, False]
    #__________________________________________________________________

    #-----------------------------Waiting results-----------------------------#
    #optimal_value_regularity[0] --> type_operation = "plus"
    #optimal_value_regularity[1] --> type_operation = "plus"
    optimal_value_regularity = [[3100, 2473, 1871], [2952432, 5052960, 3455230]]
    #___________________________________________________________________________

    #-----------------------------Lengths-----------------------------#
    n = len(list_files)
    #On a 4 principales approches: neural_network, clustering_binaire, clustering_agglo et decision_tree
    nb_approach = 4
    #Nombre d'arbre pour chaque approche decision tree
    nb_tree = [1,3]
    m = nb_approach -1 + len(nb_tree)
    #___________________________________________________________________________
    
    #-----------------------------Fill-in list_methods and preparation of where we will put ours results-----------------------------#
    for i in range(m):
        resultats_globaux_approche.append({})
        if i < len(nb_tree):
            list_methods.append('dt_'+str(nb_tree[i]))
    list_methods.append('ca')
    list_methods.append('nn')
    list_methods.append('cb')
    list_methods.append('Opt_val')

    nb_hidden_layers, nb_neurons = 1, [1,1]
    #___________________________________________________________________________

    #-----------------------------Threads creation-----------------------------#
    threads = []
    for i in range((nb_approach)*n):
        if i < n:
            for j in range(len(nb_tree)):
                t = threading.Thread(target=mdt.main_dt, args=(resultats_globaux_approche[j], list_files[i], list_nb_layers[i], list_k[i], list_k_k[i], list_tps_max[i], list_it_max[i], list_type_operation[i], nb_tree[j], list_display_sol[i], list_display_start[i], list_display_matrix[i]))
                threads.append(t)
                t.start()
        elif i < 2*n:
            t = threading.Thread(target=mca.main_ca, args=(resultats_globaux_approche[-3], list_files[i-n], list_nb_layers[i-n], list_k[i-n], list_k_k[i-n], list_tps_max[i-n], list_it_max[i-n], list_type_operation[i-n], list_display_sol[i-n], list_display_start[i-n], list_display_matrix[i-n]))
            threads.append(t)
            t.start()
        elif i < 3*n:
            t = threading.Thread(target=mnn.main_nn, args=(resultats_globaux_approche[-2],  list_files[i-2*n], list_nb_layers[i-2*n], list_k[i-2*n], list_k_k[i-2*n], nb_hidden_layers, nb_neurons, list_tps_max[i-2*n], list_it_max[i-2*n], list_type_operation[i-2*n], list_display_sol[i-2*n], list_display_start[i-2*n], list_display_matrix[i-2*n]))
            threads.append(t)
            t.start()
        elif i < 4*n:
            t = threading.Thread(target=mcb.main_cb, args=(resultats_globaux_approche[-1],  list_files[i-3*n], list_nb_layers[i-3*n], list_k[i-3*n], list_k_k[i-3*n], list_tps_max[i-3*n], list_it_max[i-3*n], list_type_operation[i-3*n], 0.80,  list_display_sol[i-3*n], list_display_start[i-3*n], list_display_matrix[i-3*n]))
            threads.append(t)
            t.start()
        
            

    
    
    for t in threads:
        t.join()
    #___________________________________________________________________________

    #-----------------------------Range results by file-----------------------------#
    for i in range(n):
        resultats_globaux_files.append([])
        for j in range(m):
            resultats_globaux_files[i].append(resultats_globaux_approche[j][list_files[i]])
    #___________________________________________________________________________

    #-----------------------------Get the max iteration of each file for all approachs-----------------------------#
    matrix = []
    for i in range(n):
        matrix.append([])
        for j in range(m):
            matrix[i].append(len(resultats_globaux_files[i][j][1]))

    max_iteration_by_file = []
    for line in range (len(matrix)):
        max_iteration_by_file.append(max(matrix[line]))
    #___________________________________________________________________________

    #-----------------------------Plot results-----------------------------#
    #Parcourir chaque fichier et plot la courbe de chaque approche
    for i in range(n):
        plt.figure(figsize=(10, 8))
        for j in range(m):
            plt.plot([k for k in range(len(resultats_globaux_files[i][j][0]))], resultats_globaux_files[i][j][0], label=list_methods[j], marker='o')

        #Print aussi le résultat même calculé dans main_opt_val (renseigné dans optimal_value_regularity)
        if list_type_operation[i] == "plus":
            plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[0][i] for k in range(max_iteration_by_file[i])], label="Opt_val_plus")
        else:
            plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[1][i] for k in range(max_iteration_by_file[i])], label="Opt_val_fois")
            
        plt.xlabel("Iteration")
        plt.ylabel("resultat_a_chaque_iteration_"+list_plot_name[i])
        plt.xticks(range(max_iteration_by_file[i]))
        plt.title("resultat_a_chaque_iteration_"+list_plot_name[i])
        plt.legend()
        plt.show()
        plt.savefig("plot_resultat_a_chaque_iteration_"+list_plot_name[i]+".png")
       
    for i in range(n):
        plt.figure(figsize=(10, 8))
        for j in range(m):
            plt.plot([i for i in range(len(resultats_globaux_files[i][j][1]))], resultats_globaux_files[i][j][1], label=list_methods[j], marker='o')
        if list_type_operation[i] == "plus":
            plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[0][i] for k in range(max_iteration_by_file[i])], label="Opt_val_plus")
        else:
            plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[1][i] for k in range(max_iteration_by_file[i])], label="Opt_val_fois")
        plt.xlabel("Iteration")
        plt.ylabel("resultat_globaux_"+list_plot_name[i])
        plt.xticks(range(max_iteration_by_file[i]))
        plt.title("resultat_globaux_"+list_plot_name[i])
        plt.legend()
        plt.show()
        plt.savefig("plot_resultat_globaux_"+list_plot_name[i]+".png")
        #___________________________________________________________________________
        


if __name__ == "__main__":
    main()


