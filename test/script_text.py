import sys
import threading
import matplotlib.pyplot as plt
sys.path.append("../bdt")
import main_dt as mdt
sys.path.append("../clustering_agglo")
import main_ca as mca
sys.path.append("../Clustering_binaire")
import main_cb as mcb

resultats_globaux_approche = []
resultats_globaux_files = []


def main():
    #Names of files must be different
    # list_files = ['../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/ft10.txt', '../file_with_optimal_val/example.data']
    list_files = ['../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la03.txt']
    list_plot_name = ['la04', 'la03', 'la02', 'ft10', 'example']
    list_nb_layers = [5, 5, 5, 5, 5]
    list_methods = ['dt1','dt2', 'ca', 'cb'] #to change
    list_k = [20, 20, 20, 20, 20]
    list_k_k = [15, 15, 15, 15, 15]
    list_tps_max = [100, 100, 100, 100, 100]
    list_it_max = [10, 10, 10, 10, 10]
    list_type_operation = ['plus', 'plus', 'plus', 'plus', 'plus']
    list_display_sol = [False, False, False, False, False]
    list_display_start = [False, False, False, False, False]
    list_display_matrix = [False, False, False, False, False]
    n = len(list_files)
    #Nombre d'arbre pour chaque approche decision tree
    nb_tree = [1,2]
    m = 2 + len(nb_tree)
    for i in range(m):
        resultats_globaux_approche.append({})

    threads = []
    for i in range(3*n):
        if i < n:
            for j in range(len(nb_tree)):
                t = threading.Thread(target=mdt.main_dt, args=(resultats_globaux_approche[j], list_files[i], list_plot_name[i], list_nb_layers[i], list_k[i], list_k_k[i], list_tps_max[i], list_it_max[i], list_type_operation[i], nb_tree[j], list_display_sol[i], list_display_start[i], list_display_matrix[i]))
                threads.append(t)
                t.start()
        elif i < 2*n:
            t = threading.Thread(target=mca.main_ca, args=(resultats_globaux_approche[-2], list_files[i-n], list_plot_name[i-n], list_nb_layers[i-n], list_k[i-n], list_k_k[i-n], list_tps_max[i-n], list_it_max[i-n], list_type_operation[i-n], list_display_sol[i-n], list_display_start[i-n], list_display_matrix[i-n]))
            threads.append(t)
            t.start()
        else:
            t = threading.Thread(target=mcb.main_cb, args=(resultats_globaux_approche[-1], list_files[i-2*n], list_plot_name[i-2*n], list_nb_layers[i-2*n], list_k[i-2*n], list_k_k[i-2*n], list_tps_max[i-2*n], list_it_max[i-2*n], list_type_operation[i-2*n], list_display_sol[i-2*n], list_display_start[i-2*n], list_display_matrix[i-2*n]))
            threads.append(t)
            t.start()

    
    for t in threads:
        t.join()
    
    for i in range(n):
        resultats_globaux_files.append([])
        for j in range(m):
            resultats_globaux_files[i].append(resultats_globaux_approche[j][list_files[i]])
    
    # Plot une à une les images des approches pour chaque fichier
    # print(resultats_globaux_files)




    # Faire un subplot des images des approches pour chaque fichier

    # for i in range(n):
    #     plt.figure(figsize=(10, 8))
    #     for j in range(m):
    #         plt.subplot(2, m/2+1, j+1)
    #         plt.plot([i for i in range(len(resultats_globaux_files[i][j][0]))], resultats_globaux_files[i][j][0], label=list_plot_name[i])

    matrix = []
    for i in range(n):
        matrix.append([])
        for j in range(m):
            matrix[i].append(len(resultats_globaux_files[i][j][1]))

    max_iteration_by_file = []
    for line in range (len(matrix)):
        max_iteration_by_file.append(max(matrix[line]))

    for i in range(n):
        plt.figure(figsize=(10, 8))
        for j in range(m):
            # plt.subplot(2, m/2+1, j+1)
            plt.plot([i for i in range(len(resultats_globaux_files[i][j][1]))], resultats_globaux_files[i][j][1], label=list_methods[j])
        plt.xlabel("Iteration")
        plt.ylabel("Objective function")
        plt.xticks(range(max_iteration_by_file[i]))
        plt.legend()
        plt.show()
            # plt.plot([i for i in range(max_iteration_by_file[i])], resultats_globaux_files[i][j][1], label=list_plot_name[i])


if __name__ == "__main__":
    main()


