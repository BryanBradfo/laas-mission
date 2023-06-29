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

def clustAggloDist(data, dist_deb, dist_max, pas):
    dist = dist_deb
    silhouette_scores = []
    davies_bouldin_scores = []
    number_clusters = []
    runtimes = []
    iterations = []
    while dist<dist_max:
        # set distance_threshold (0 ensures we compute the full tree )
        print("______________________________________dist = ", dist)
        tps1 = time.time()
        model = cluster.AgglomerativeClustering(distance_threshold =dist , linkage ='single', n_clusters = None )
        model = model.fit(data)
        tps2 = time.time()
        labels = model.labels_
        k = model.n_clusters_
        leaves = model.n_leaves_
        
        if k>1 and k<len(data)-1:
                #Methode coefficient de silhouette
                silhouette_scores.append(silhouette_score(data, labels))
                #Methode coefficient de Davies-Bouldin
                davies_bouldin_scores.append(davies_bouldin_score(data, labels))
        else:
            silhouette_scores.append(-1)
            davies_bouldin_scores.append(1)
        
        runtime = round (( tps2 - tps1 )*1000 ,2)
        runtimes.append(runtime)
        number_clusters.append(k)

        print("nb clusters =",k,", nb feuilles = ", leaves , " runtime = ", runtime ,"ms dist = ", dist )
        dist+=pas#Se fixer sur 1 data
    return silhouette_scores, davies_bouldin_scores, number_clusters, runtimes, iterations

def myPlot(x, silhouette_scores, davies_bouldin_scores):
    # create plot
    y = silhouette_scores
    plt.subplot(2, 1, 1)
    plt.plot(x, y, label="Silhouette Score")
    plt.xlabel("Nombre de clusters")
    plt.ylabel("Scores")
    plt.title("Scores par nombre de clusters")
    plt.legend()
    plt.show()
    #Afficher le pic de la courbe de silhouette
    print("Le pic de la courbe de silhouette est : ", max(silhouette_scores))
    print("Le nombre de clusters correspondant est : ", silhouette_scores.index(max(silhouette_scores))+2)
    print("")
    
    y = davies_bouldin_scores
    plt.subplot(2, 1, 1)
    plt.plot(x, y, label="davies_bouldin Scores")
    plt.xlabel("Nombre de clusters")
    plt.ylabel("Scores")
    plt.title("Scores par nombre de clusters")
    plt.legend()
    plt.show()
    
       
    #Afficher le pic de la courbe de davies_bouldin
    print("Le pic de la courbe de davies_bouldin est : ", min(davies_bouldin_scores))
    print("Le nombre de clusters correspondant est : ", davies_bouldin_scores.index(min(davies_bouldin_scores))+2)
    print("")


def clustering(data_pref_layer,d_deb, d_max, pas):

    i = 0
    silhouette_scores = []
    davies_bouldin_scores = []
    for data in data_pref_layer:
        silhouette_scores_data, davies_bouldin_scores_data, number_clusters, runtimes, iterations = clustAggloDist(data, d_deb, d_max, pas)
        silhouette_scores.append(silhouette_scores_data)
        davies_bouldin_scores.append(davies_bouldin_scores_data)
        i+=1

    for i in range(0, len(data_pref_layer)):
        print("Jeu de donnees ", i)
        x = [i/100 for i in range(d_deb*100, d_max*100, pas*100)]
        myPlot(x, silhouette_scores[i], davies_bouldin_scores[i])
    


