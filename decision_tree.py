# Implementation of the decision tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import tree
import FunctionMain as fm
from sklearn.tree import DecisionTreeClassifier, export_text
from docplex.cp.modeler import *
import numpy as np

#----------------------Function: my_decision_tree----------------------#     
def my_decision_tree(n, m, list_layers):
    X_list_start_sol = []
    Y_list_layers = []
    for i in range(len(list_layers)):
        for j in range(len(list_layers[i])):
            list_start = fm.start_sol(n, m, list_layers[i][j])
            # X : Liste de solutions par layer (List de list de starts de chaque solution)
            X_list_start_sol.append(list_start)
            # Y : Liste des layers de chaque solution (List de int)
            if i == 0:
                Y_list_layers.append(1)
            else:
                Y_list_layers.append(0)
    # nb_sols = len(X_list_start_sol)
    X_train, X_test, y_train, y_test = train_test_split(X_list_start_sol, Y_list_layers, test_size=0.2, random_state=42)
    
    #Got best decision tree by comparison of different parameters
    parameters = {'max_depth': [i for i in range(int(n*m/5), int(n*m/2), int(n*m/5))], 'min_samples_split': [i for i in range(5, 20, 5) ], 'splitter':['best', 'random']}
    best_score = -1
    for max_depth in parameters['max_depth']:
        for min_samples_split in parameters['min_samples_split']:
            for splitter in parameters['splitter']:
                clf = tree.DecisionTreeClassifier(max_depth=max_depth, min_samples_split=min_samples_split, splitter=splitter)
                clf = clf.fit(X_train, y_train)
                #prediction
                y_pred = clf.predict(X_test)
                score = accuracy_score(y_test, y_pred)
                print("Score:", score)
                if best_score < score:
                    print("Best score: " + str(score) + " with parameters: " + str({'max_depth': max_depth, 'min_samples_split': min_samples_split, 'splitter': splitter}))
                    best_score = score
                    best_parameters = {'max_depth': max_depth, 'min_samples_split': min_samples_split, 'splitter': splitter}
    clf = tree.DecisionTreeClassifier(max_depth=best_parameters['max_depth'], min_samples_split=best_parameters['min_samples_split'], splitter=best_parameters['splitter'])
    clf = clf.fit(X_train, y_train)
    tree_rules = export_text(clf)
    feuilles_conditions = []
    parcourir_arbre(clf, feuilles_conditions, 0, 0,[])
    return clf, feuilles_conditions
#______________________________________________________________________#


#----------------------Function: extract_conditions----------------------#
# Analysez le texte pour obtenir les conditions à chaque nœud

# def extract_conditions(tree_rules):
#     conditions = []
#     lines = tree_rules.split('\n')
#     i=-1
#     for line in lines:
#         if '|---' in line:
#             node_id_condition = line.split('|---')[-1].strip()
#             if node_id_condition.startswith('class'):
#                 conditions[i].append(int(node_id_condition.split(' ')[1]))
#                 continue
#             i+=1
#             if len(node_id_condition.split(' <= ')) == 2:
#                 node, condition = node_id_condition.split(' <= ')
#                 node_id = int(node.split('_')[1])
#                 condition_id = float(condition)
#                 conditions.append([node_id, condition_id, '<='])
#             elif len(node_id_condition.split(' > ')) == 2:
#                 node_id, condition = node_id_condition.split(' > ')
#                 conditions.append([node_id, condition.strip(), '>'])
#     return conditions

def parcourir_arbre(clf, feuilles_conditions, noed_actuel, profondeur, conditions_actuelles):
    arbre_decision = clf.tree_
    classes = clf.classes_
    if arbre_decision.feature[noed_actuel] == -2:  # Vérifier si c'est une feuille
        # Récupérer l'indice de la classe prédite pour cette feuille
        classe_predite_indice = np.argmax(arbre_decision.value[noed_actuel])
        # Récupérer la classe prédite à partir de l'indice
        classe_predite = classes[classe_predite_indice]
        conditions_actuelles.append(classe_predite)
        feuilles_conditions.append(conditions_actuelles.copy())
        conditions_actuelles.pop()  # Retirer la condition ajoutée avant de remonter
        return
    feature_index = arbre_decision.feature[noed_actuel]
    threshold = arbre_decision.threshold[noed_actuel]
    # Condition pour le fils gauche
    condition_left = f"{feature_index} <= {threshold}"
    conditions_actuelles.append(condition_left)
    parcourir_arbre(clf, feuilles_conditions, arbre_decision.children_left[noed_actuel], profondeur + 1, conditions_actuelles)
    conditions_actuelles.pop()  # Retirer la condition ajoutée avant de passer au fils droit
    # Condition pour le fils droit (inversion de l'opérateur)
    condition_right = f"{feature_index} > {threshold}"
    conditions_actuelles.append(condition_right)
    parcourir_arbre(clf, feuilles_conditions, arbre_decision.children_right[noed_actuel], profondeur + 1, conditions_actuelles)
    conditions_actuelles.pop()  # Retirer la condition ajoutée avant de remonter

#______________________________________________________________________#

#----------------------Function: constraint_tree----------------------#
# Créer les contraintes pour les variables du solver à partir des conditions
def constraint_tree(list_variables, conditions):
    constraints = []
    for condition in conditions:
        if len(condition) == 4:
            if condition[2] == '<=':
                less_or_equal(list_variables[condition[0]], condition[1])

            elif condition[2] == '>':
                greater(list_variables[condition[0]], condition[1])
            continue
        if condition[2] == '<=':
            less_or_equal(list_variables[condition[0]], condition[1])
        elif condition[2] == '>':
            greater(list_variables[condition[0]], condition[1])
    return constraints










def my_decision_tree_predict(list_var_starts, clf):
    
    return clf.predict([list_var_starts])[0]


#______________________________________________________________________#
