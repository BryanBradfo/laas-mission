# Implementation of the decision tree

from sklearn import tree
import functions as fm

#----------------------Function: my_decision_tree----------------------#     
# Output: clf : Decision tree classifier

def my_decision_tree(n, m, list_layers):
    X_list_start_sol = []
    Y_list_layers = []
    for i in range(len(list_layers)):
        for j in range(len(list_layers[i])):
            list_start = fm.start_sol(n, m, list_layers[i][j])
            # X : Liste de solutions par layer (List de list de starts de chaque solution)
            X_list_start_sol.append(list_start)
            # Y : Liste des layers de chaque solution (List de int)
            Y_list_layers.append(i)
    
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X_list_start_sol, Y_list_layers)
    return clf

#----------------------Function: my_decision_tree_predict----------------------#
# Output: list_layers_predicted : List of predicted layers
# def my_decision_tree_predict(n, m, list_sols_starts, clf):
#     list_layers_predicted = []
#     for i in range(len(list_sols_starts)):
#         list_start = fm.start_sol(n, m, list_sols_starts[i])
#         list_layers_predicted.append(clf.predict([list_start])[0])
#     return list_layers_predicted

def my_decision_tree_predict(list_var_starts, clf):
    
    return clf.predict([list_var_starts])[0]


#______________________________________________________________________#
