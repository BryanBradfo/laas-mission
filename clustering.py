#Clustering agglomératif des solutions
import numpy as np
import matplotlib.pyplot as plt
import scipy . cluster . hierarchy as shc

import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn import cluster
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score

def create_layers(list_equal, data_pref):
    print("Clustering ...")
    print(data_pref)

    data_pref_layer = []
    layer_1 = [data_pref[0]]
    data_pref_layer.append(layer_1)
    k=0
    for i in range(len(list_equal)):
        if list_equal[i] == True:
            data_pref_layer[k].append(data_pref[i+1])
        else:
            k+=1
            layer = []
            layer.append(data_pref[i+1])
            data_pref_layer.append(layer)
    
    return data_pref_layer


# ----------------- Code clustering de Brenda --------------------

def clustAggloDist(data, dist_deb, dist_max, pas):
    
    silhouette_scores = []
    davies_bouldin_scores = []
    number_clusters = []
    runtimes = []
    iterations = []
    distances = []
    for dist in np.arange(dist_deb, dist_max, pas):
        # set distance_threshold (0 ensures we compute the full tree )
        #print("______________________________________dist = ", dist)
        tps1 = time.time()
        model = cluster.AgglomerativeClustering(distance_threshold =dist , linkage ='single', n_clusters = None )
        #print(data)
        model = model.fit(data)
        tps2 = time.time()
        labels = model.labels_
        k = model.n_clusters_
        leaves = model.n_leaves_
        data_lenght = len(data)
        if data_lenght > 2:
            if k>1:
                    if k<data_lenght-1:
                        #Methode coefficient de silhouette
                        silhouette_scores.append(silhouette_score(data, labels))
                        #Methode coefficient de Davies-Bouldin
                        davies_bouldin_scores.append(davies_bouldin_score(data, labels))
                    else:
                        silhouette_scores.append(-2)
                        davies_bouldin_scores.append(2)
            else:
                silhouette_scores.append(-1)
                davies_bouldin_scores.append(1)
        else:
            silhouette_scores.append(-3)
            davies_bouldin_scores.append(3)
        
        runtime = round (( tps2 - tps1 )*1000 ,2)
        runtimes.append(runtime)
        number_clusters.append(k)
        distances.append(dist)

        #print("nb clusters =",k,", nb feuilles = ", leaves , " runtime = ", runtime ,"ms dist = ", dist )
        #Se fixer sur 1 data
    return silhouette_scores, davies_bouldin_scores, number_clusters, runtimes, iterations, distances

def myPlot(x, silhouette_scores, davies_bouldin_scores, number_cluster, distance):
    # create plot
    y = silhouette_scores
    plt.subplot(1, 2, 1)
    plt.plot(x, y, label="Silhouette Score", marker='o')
    plt.xlabel("Distance")
    plt.ylabel("Scores")
    plt.title("Scores en fonction de la distance")
    plt.legend()
    
    y = davies_bouldin_scores
    plt.subplot(1, 2, 2)
    plt.plot(x, y, label="davies_bouldin Scores", marker='o')
    plt.xlabel("Distance")
    plt.ylabel("Scores")
    plt.title("Scores en fonction de la distance")
    plt.legend()
    plt.show()

    #Afficher le pic de la courbe de silhouette
    print("Le pic de la courbe de silhouette est : ", max(silhouette_scores))
    print("Le nombre de clusters correspondant est : ", number_cluster[silhouette_scores.index(max(silhouette_scores))])
    print("La distance correspondante est : ", distance[silhouette_scores.index(max(silhouette_scores))])
    print("")    
       
    #Afficher le pic de la courbe de davies_bouldin
    print("Le pic de la courbe de davies_bouldin est : ", min(davies_bouldin_scores))
    print("Le nombre de clusters correspondant est : ", number_cluster[davies_bouldin_scores.index(min(davies_bouldin_scores))])
    print("La distance correspondante est : ", distance[davies_bouldin_scores.index(min(davies_bouldin_scores))])
    print("")


def clustering(data_pref_layer,d_deb, d_max, pas):

    i = 0
    silhouette_scores = []
    davies_bouldin_scores = []
    number_clusters = []
    distances = []
    for data in data_pref_layer:
        silhouette_scores_data, davies_bouldin_scores_data, number_clusters_data, runtimes, iterations, distances_data = clustAggloDist(data, d_deb, d_max, pas)
        silhouette_scores.append(silhouette_scores_data)
        davies_bouldin_scores.append(davies_bouldin_scores_data)
        number_clusters.append(number_clusters_data)
        distances.append(distances_data)
        i+=1

    for i in range(0, len(data_pref_layer)):
        print("--------------Layer", i, "-----------------")
        print(len(data_pref_layer[i]))
        x = [i for i in np.arange(d_deb, d_max, pas)]
        myPlot(x, silhouette_scores[i], davies_bouldin_scores[i], number_clusters[i], distances[i])
        print("__________________________________________________________")

# ----------------- Code clustering de Alice --------------------


def my_agglo_threshold( datanp , threshold, linkage):
       tps1 = time.time()
       model = cluster.AgglomerativeClustering(distance_threshold = threshold ,
                                                 linkage =linkage, n_clusters = None )
       model = model.fit( datanp )

       tps2 = time.time()
       labels = model.labels_
       k = model.n_clusters_
       leaves = model.n_leaves_

       return k , leaves , labels, tps2 - tps1



# indice de silhouette

def silhouette(datanp, r1, r2):
    list = []
    listk = []
    listleaves = []
    for d in range (r1,r2):

        k, leaves, labels, runtime = my_agglo_threshold(datanp, d, 'single')
            
        listk.append(k)
        listleaves.append(leaves)

        if k>1 and k<len(datanp)-1:
            silhouette_avg = silhouette_score(datanp, labels)
        else:
            silhouette_avg = -1
        list.append(silhouette_avg)

    maxd = np.max(list)
    indice = list.index(maxd)

    plt.plot([d for d in range(r1,r2)], list, marker='o')
    plt.title("Silhouette")
    plt.xlabel("Distance")
    plt.ylabel("Silhouette")
    plt.show()

    return list, listk[indice], listleaves[indice], runtime

    


