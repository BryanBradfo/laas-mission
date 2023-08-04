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
sys.path.append("../hybrid_approach")
import main_hyb_1 as mha1
import main_hyb_nn as mha2

import random
random.seed(10)

resultats_globaux_approche = []
resultats_globaux_files = []
list_methods = []

def ligne_latex(values):
    return " & ".join(str(val) for val in values) + " \\\\"

def main():
    #-----------------------------Parameters of every methods-----------------------------#
    #Names of files must be different
    list_files = ['../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la05.txt', '../file_with_optimal_val/la06.txt' ]
    # list_files = ['../file_with_optimal_val/la01.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/la03.txt']
    # list_files = ['../file_with_optimal_val/la01.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la05.txt', 
                # '../file_with_optimal_val/la06.txt',  '../file_with_optimal_val/la07.txt',  '../file_with_optimal_val/la08.txt', '../file_with_optimal_val/la09.txt', '../file_with_optimal_val/la10.txt',
                # '../file_with_optimal_val/la11.txt','../file_with_optimal_val/la12.txt','../file_with_optimal_val/la13.txt','../file_with_optimal_val/la14.txt','../file_with_optimal_val/la15.txt',
                # '../file_with_optimal_val/la16.txt','../file_with_optimal_val/la17.txt','../file_with_optimal_val/la18.txt','../file_with_optimal_val/la19.txt','../file_with_optimal_val/la20.txt',
                # '../file_with_optimal_val/la21.txt','../file_with_optimal_val/la22.txt','../file_with_optimal_val/la23.txt','../file_with_optimal_val/la24.txt','../file_with_optimal_val/la25.txt',
                # '../file_with_optimal_val/la26.txt','../file_with_optimal_val/la27.txt','../file_with_optimal_val/la28.txt','../file_with_optimal_val/la29.txt','../file_with_optimal_val/la30.txt',
                # '../file_with_optimal_val/la31.txt','../file_with_optimal_val/la32.txt','../file_with_optimal_val/la33.txt','../file_with_optimal_val/la34.txt','../file_with_optimal_val/la35.txt',
                # '../file_with_optimal_val/la36.txt','../file_with_optimal_val/la37.txt','../file_with_optimal_val/la38.txt','../file_with_optimal_val/la39.txt', '../file_with_optimal_val/la40.txt'
                # ]
    list_plot_name = ['la0' + str(i) for i in range (1,len(list_files)+1)]
    list_nb_layers = [5 for i in range (len(list_files))]
    list_k = [20 for i in range (len(list_files))]
    list_k_k = [15 for i in range (len(list_files))]
    list_tps_max = [100 for i in range (len(list_files))]
    list_it_max = [20 for i in range (len(list_files))]
    list_type_operation = ['plus' for i in range (len(list_files))]
    list_type_user = ["user_reg" for i in range (len(list_files))]
    # list_type_user = ["user_reg", "user_reg", "user_reg", "user_reg", "user_reg"]
    list_display_sol = [False for i in range (len(list_files))]
    list_display_start = [False for i in range (len(list_files))]
    list_display_matrix = [False for i in range (len(list_files))]
    #__________________________________________________________________

    #-----------------------------Waiting results-----------------------------#
    #optimal_value_regularity[0] --> type_operation = "plus"
    #optimal_value_regularity[1] --> type_operation = "fois"
    optimal_value_regularity = [[1341, 1455, 1486, 1224, 737, 2811, 2026, 1542, 1560, 2006, 4960, 2324, 2594, 3540, 6216, 19459, 13866, 15630, 18390, 16451, 30553, 30039, 22185, 24789, 25841, 26482, 23883, 34420, 42152, 38370, 44144, 33451, 38507, 40841, 46339, 69182, 76531, 80373, 75815, 66098], [2952432, 5052960, 3455230]]
    optimal_value_simple = [666, 655, 597, 590, 593,
                            926, 890, 863, 951, 958,
                            1222, 1039, 1150, 1292, 1207,
                            945, 784, 848, 842, 902,
                            1046, 927, 1032, 935, 977,
                            1218, 1235, 1216, 1152, 1355,
                            1784, 1850, 1717, 1721, 1888,
                            1268, 1397, 1196, 1233, 1222]
    #___________________________________________________________________________

    #-----------------------------Lengths-----------------------------#
    n = len(list_files)
    #___________________________________________________________________________

    #-----------------------------Approachs without hybrid approachs-----------------------------#
    #On a 4 principales approches: neural_network, clustering_binaire, clustering_agglo, decision_tree
    nb_approach = 4
    #Nombre d'arbre pour chaque approche decision tree
    nb_tree = [1,3]
    nb_dt_approach = len(nb_tree)
    m = nb_approach + (nb_dt_approach-1)*1

    #___________________________________________________________________________

    #-----------------------------Approachs with hybrid approachs-----------------------------#
    # #On a 4 principales approches: neural_network, clustering_binaire, clustering_agglo, decision_tree, hybrid method 1, hybrid method 2
    # nb_approach = 6
    # #Nombre d'arbre pour chaque approche decision tree
    # nb_tree = [1,3]
    # nb_dt_approach = len(nb_tree)
    # m = nb_approach + (nb_dt_approach-1)*3
    #___________________________________________________________________________
    
    
    #-----------------------------Fill-in list_methods and preparation of where we will put ours results-----------------------------#
    for i in range(m):
        resultats_globaux_approche.append({})
        if i < len(nb_tree):
            list_methods.append('dt_'+str(nb_tree[i]))
    list_methods.append('ca')
    list_methods.append('nn')
    list_methods.append('cb')
    for i in range(nb_dt_approach):
        list_methods.append('hyb_1_'+str(nb_tree[i]))
    for i in range(nb_dt_approach):
        list_methods.append('hyb_2_'+str(nb_tree[i]))
    list_methods.append('Opt_val')

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
            t = threading.Thread(target=mca.main_ca, args=(resultats_globaux_approche[-3], list_files[i-n], list_nb_layers[i-n], list_k[i-n], list_k_k[i-n], list_tps_max[i-n], list_it_max[i-n], list_type_operation[i-n], list_type_user[i-n], list_display_sol[i-n], list_display_start[i-n], list_display_matrix[i-n]))
            threads.append(t)
            t.start()
        elif i < 3*n:
            t = threading.Thread(target=mnn.main_nn, args=(resultats_globaux_approche[-2],  list_files[i-2*n], list_nb_layers[i-2*n], list_k[i-2*n], list_k_k[i-2*n], nb_hidden_layers, nb_neurons, list_tps_max[i-2*n], list_it_max[i-2*n], list_type_operation[i-2*n], list_type_user[i-2*n], list_display_sol[i-2*n], list_display_start[i-2*n], list_display_matrix[i-2*n]))
            threads.append(t)
            t.start()
        elif i < 4*n:
            t = threading.Thread(target=mcb.main_cb, args=(resultats_globaux_approche[-1],  list_files[i-3*n], list_nb_layers[i-3*n], list_k[i-3*n], list_k_k[i-3*n], list_tps_max[i-3*n], list_it_max[i-3*n], list_type_operation[i-3*n], list_type_user[i-3*n], 0.87,  list_display_sol[i-3*n], list_display_start[i-3*n], list_display_matrix[i-3*n]))
            threads.append(t)
            t.start()
        elif i < 5*n:
            for j in range(nb_dt_approach):
                t = threading.Thread(target=mha1.main_hyb_1, args=(resultats_globaux_approche[nb_dt_approach+3+j],  list_files[i-4*n], list_nb_layers[i-4*n], list_k[i-4*n], list_k_k[i-4*n], list_tps_max[i-4*n], list_it_max[i-4*n], list_type_operation[i-4*n], list_type_user[i-4*n], nb_tree[j], 0.85,  list_display_sol[i-4*n], list_display_start[i-4*n], list_display_matrix[i-4*n]))
                threads.append(t)
                t.start()
        elif i < 6*n:
            for j in range(nb_dt_approach):
                t = threading.Thread(target=mha2.main_hyb_nn, args=(resultats_globaux_approche[2*nb_dt_approach+3+j],  list_files[i-5*n], list_nb_layers[i-5*n], list_k[i-5*n], list_k_k[i-5*n], nb_hidden_layers, nb_neurons, list_tps_max[i-5*n], list_it_max[i-5*n], list_type_operation[i-5*n], list_type_user[i-5*n], nb_tree[j],0.6, list_display_sol[i-5*n], list_display_start[i-5*n], list_display_matrix[i-5*n]))
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
        plt.ylabel("Resultat à chaque itération pour "+list_plot_name[i])
        plt.xticks(range(max_iteration_by_file[i]))
        plt.title("resultat_a_chaque_iteration_"+list_plot_name[i])
        plt.legend()
        plt.show()
        plt.savefig("plot_resultat_a_chaque_iteration_"+list_plot_name[i]+".png")

    nombre_colonnes = m + 2

    tableau_latex = "\\begin{tabular}{" + "|c" * nombre_colonnes + "|}\n "
    tableau_latex += "  \hline \n"
    tableau_latex += " File & Optimal & DT & DT 2 & Agglomerative clustering & Binary clustering & NN \\\\ \n"
    tableau_latex += "  \hline \n" 
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

        variable_latex = []

        file = list_files[i]
        new_file = file.split("/")[-1]
        print("File: ", new_file)
        variable_latex.append(new_file)

        if list_type_user[i] == "user_reg":
            #Print aussi le résultat même calculé dans main_opt_val (renseigné dans optimal_value_regularity)
            if list_type_operation[i] == "plus":
                optimal_val = optimal_value_regularity[0][i]    
            else:
                optimal_val = optimal_value_regularity[1][i]
        else:
            optimal_val = optimal_value_simple[i]
        
        print("Optimal value: ", optimal_val)
        variable_latex.append(optimal_val)

        for j in range(len(nb_tree)):
            print( str(j) + " decision trees: ", round(optimal_val/min(resultats_globaux_files[i][j][1]),4))
            variable_latex.append(round(optimal_val/min(resultats_globaux_files[i][j][1]),4))

        print("Agglomertaive clustering", round(optimal_val/min(resultats_globaux_files[i][len(nb_tree)][1]),4))
        variable_latex.append(round(optimal_val/min(resultats_globaux_files[i][len(nb_tree)][1]),4))
        print("Neural network ", round(optimal_val/min(resultats_globaux_files[i][len(nb_tree)+1][1]),4))
        variable_latex.append(round(optimal_val/min(resultats_globaux_files[i][len(nb_tree)+1][1]),4))
        print("Binary clustering", round(optimal_val/min(resultats_globaux_files[i][len(nb_tree)+2][1]),4))
        variable_latex.append(round(optimal_val/min(resultats_globaux_files[i][len(nb_tree)+2][1]),4))
        
  
        colonnes = [variable_latex[i:i + nombre_colonnes] for i in range(0, len(variable_latex), nombre_colonnes)]

        tableau_latex += "  "
        for colonne in colonnes:
            tableau_latex += ligne_latex(colonne) + "\n"
        tableau_latex += " \hline \n"
    tableau_latex += "\\end{tabular}"

    # Écrire le tableau dans le fichier tableau_results.txt
    with open("tableau_results.txt", "w") as fichier:
        fichier.write(tableau_latex)

if __name__ == "__main__":
    main()




