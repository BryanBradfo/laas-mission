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
sys.path.append("../hybrid_approach")
import main_hyb_1 as mha

import random
random.seed(10)

resultats_globaux_approche = []
resultats_globaux_files = []
list_methods = []


def main():
    #-----------------------------Parameters of every methods-----------------------------#
    #Names of files must be different
    # list_files = ['../file_with_optimal_val/la01.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la05.txt', '../file_with_optimal_val/la06.txt' ]
    list_files = ['../file_with_optimal_val/la01.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/la03.txt']
    list_plot_name = ['la01', 'la02', 'la03', 'la04', 'la05']
    list_nb_layers = [5, 5, 5, 5, 5]
    list_k = [20, 20, 20, 20, 20]
    list_k_k = [15, 15, 15, 15, 15]
    list_tps_max = [100, 100, 100, 100, 100]
    list_it_max = [40, 40, 40, 40, 20]
    # list_type_operation = ['fois', 'fois', 'fois', 'plus', 'plus']
    list_type_operation = ['plus', 'plus', 'plus', 'plus', 'plus']
    # list_type_user = ["other", "other", "other", "other", "other"]
    list_type_user = ["user_reg", "user_reg", "user_reg", "user_reg", "user_reg"]
    list_display_sol = [False, False, False, False, False]
    list_display_start = [False, False, False, False, False]
    list_display_matrix = [False, False, False, False, False]
    #__________________________________________________________________

    #-----------------------------Waiting results-----------------------------#
    #optimal_value_regularity[0] --> type_operation = "plus"
    #optimal_value_regularity[1] --> type_operation = "plus"
    optimal_value_regularity = [[1341, 1455, 1486, 1224, 737, 2811], [2952432, 5052960, 3455230]]
    optimal_value_simple = [666, 655, 597, 590, 593,926]
    #___________________________________________________________________________

    #-----------------------------Lengths-----------------------------#
    n = len(list_files)
    #On a 4 principales approches: neural_network, clustering_binaire, clustering_agglo et decision_tree
    nb_approach = 5
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
    # for i in range(len(nb_tree)):
    #     list_methods.append('hyb_1_'+str(nb_tree[i]))
    list_methods.append('hyb_1_')

    nb_hidden_layers, nb_neurons = 1, [1,1]
    #___________________________________________________________________________

    #-----------------------------Threads creation-----------------------------#
    threads = []
    for i in range((nb_approach)*n):
        if i < n:
            for j in range(len(nb_tree)):
                t = threading.Thread(target=mdt.main_dt, args=(resultats_globaux_approche[j], list_files[i], list_nb_layers[i], list_k[i], list_k_k[i], list_tps_max[i], list_it_max[i], list_type_operation[i], list_type_user[i], nb_tree[j], list_display_sol[i], list_display_start[i], list_display_matrix[i]))
                threads.append(t)
                t.start()
        elif i < 2*n:
            t = threading.Thread(target=mca.main_ca, args=(resultats_globaux_approche[-4], list_files[i-n], list_nb_layers[i-n], list_k[i-n], list_k_k[i-n], list_tps_max[i-n], list_it_max[i-n], list_type_operation[i-n], list_type_user[i-n], list_display_sol[i-n], list_display_start[i-n], list_display_matrix[i-n]))
            threads.append(t)
            t.start()
        elif i < 3*n:
            t = threading.Thread(target=mnn.main_nn, args=(resultats_globaux_approche[-3],  list_files[i-2*n], list_nb_layers[i-2*n], list_k[i-2*n], list_k_k[i-2*n], nb_hidden_layers, nb_neurons, list_tps_max[i-2*n], list_it_max[i-2*n], list_type_operation[i-2*n], list_type_user[i-2*n], list_display_sol[i-2*n], list_display_start[i-2*n], list_display_matrix[i-2*n]))
            threads.append(t)
            t.start()
        elif i < 4*n:
            t = threading.Thread(target=mcb.main_cb, args=(resultats_globaux_approche[-2],  list_files[i-3*n], list_nb_layers[i-3*n], list_k[i-3*n], list_k_k[i-3*n], list_tps_max[i-3*n], list_it_max[i-3*n], list_type_operation[i-3*n], list_type_user[i-3*n], 0.87,  list_display_sol[i-3*n], list_display_start[i-3*n], list_display_matrix[i-3*n]))
            threads.append(t)
            t.start()
        elif i < 5*n:
            # for j in range(len(nb_tree)):
                t = threading.Thread(target=mha.main_hyb_1, args=(resultats_globaux_approche[-1],  list_files[i-4*n], list_nb_layers[i-4*n], list_k[i-4*n], list_k_k[i-4*n], list_tps_max[i-4*n], list_it_max[i-4*n], list_type_operation[i-4*n], list_type_user[i-4*n], 1, 0.80,  list_display_sol[i-4*n], list_display_start[i-4*n], list_display_matrix[i-4*n]))
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

        #Type d'utilisateur
        if list_type_user[i] == "user_reg":
            #Print aussi le résultat même calculé dans main_opt_val (renseigné dans optimal_value_regularity)
            if list_type_operation[i] == "plus":
                plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[0][i] for k in range(max_iteration_by_file[i])], label="Opt_val_plus")
            else:
                plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[1][i] for k in range(max_iteration_by_file[i])], label="Opt_val_fois")
        else:
            plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_simple[i] for k in range(max_iteration_by_file[i])], label="Opt_val_simple")

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
        #Type d'utilisateur
        if list_type_user[i] == "user_reg":
            #Print aussi le résultat même calculé dans main_opt_val (renseigné dans optimal_value_regularity)
            if list_type_operation[i] == "plus":
                plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[0][i] for k in range(max_iteration_by_file[i])], label="Opt_val_plus")
            else:
                plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_regularity[1][i] for k in range(max_iteration_by_file[i])], label="Opt_val_fois")
        else:
            plt.plot([k for k in range(max_iteration_by_file[i])], [optimal_value_simple[i] for k in range(max_iteration_by_file[i])], label="Opt_val_simple")
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


