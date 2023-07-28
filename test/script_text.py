import sys
import threading
sys.path.append("../bdt")
import main_dt as mdt
sys.path.append("../clustering_agglo")
import main_ca as mca
sys.path.append("../Clustering_binaire")
import main_cb as mcb

def main():
    # list_files = ['../file_with_optimal_val/la04.txt', '../file_with_optimal_val/la03.txt', '../file_with_optimal_val/la02.txt', '../file_with_optimal_val/ft10.txt', '../file_with_optimal_val/example.data']
    list_files = ['../file_with_optimal_val/la04.txt']
    list_plot_name = ['la04', 'la03', 'la02', 'ft10', 'example']
    list_nb_layers = [5, 5, 5, 5, 5]
    list_k = [20, 20, 20, 20, 20]
    list_k_k = [15, 15, 15, 15, 15]
    list_tps_max = [100, 100, 100, 100, 100]
    list_it_max = [10, 10, 10, 10, 10]
    list_type_operation = ['plus', 'plus', 'plus', 'plus', 'plus']
    list_display_sol = [False, False, False, False, False]
    list_display_start = [False, False, False, False, False]
    list_display_matrix = [False, False, False, False, False]

    n = len(list_files)

    threads = []
    for i in range(3*n):
        if i < n:
            t = threading.Thread(target=mdt.main_dt, args=(list_files[i], list_plot_name[i], list_nb_layers[i], list_k[i], list_k_k[i], list_tps_max[i], list_it_max[i], list_type_operation[i], list_display_sol[i], list_display_start[i], list_display_matrix[i]))
            threads.append(t)
        elif i < 2*n:
            t = threading.Thread(target=mca.main_ca, args=(list_files[i-n], list_plot_name[i-n], list_nb_layers[i-n], list_k[i-n], list_k_k[i-n], list_tps_max[i-n], list_it_max[i-n], list_type_operation[i-n], list_display_sol[i-n], list_display_start[i-n], list_display_matrix[i-n]))
            threads.append(t)
        else:
            t = threading.Thread(target=mcb.main_cb, args=(list_files[i-2*n], list_plot_name[i-2*n], list_nb_layers[i-2*n], list_k[i-2*n], list_k_k[i-2*n], list_tps_max[i-2*n], list_it_max[i-2*n], list_type_operation[i-2*n], list_display_sol[i-2*n], list_display_start[i-2*n], list_display_matrix[i-2*n]))
            threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # for t in threads:
    #     print(t.result)
    



