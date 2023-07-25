# Implementation of the decision tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import tree
import FunctionMain as fm
from sklearn.tree import DecisionTreeClassifier, export_text

#----------------------Function: my_decision_tree----------------------#     
# Output: clf : Decision tree classifier

# def my_decision_tree(n, m, list_layers):
#     X_list_start_sol = []
#     Y_list_layers = []
#     for i in range(len(list_layers)):
#         for j in range(len(list_layers[i])):
#             list_start = fm.start_sol(n, m, list_layers[i][j])
#             # X : Liste de solutions par layer (List de list de starts de chaque solution)
#             X_list_start_sol.append(list_start)
#             # Y : Liste des layers de chaque solution (List de int)
#             Y_list_layers.append(i)
    
#     clf = tree.DecisionTreeClassifier()
#     clf = clf.fit(X_list_start_sol, Y_list_layers)
#     return clf

#______________________________________________________________________#

def my_decision_tree2(n, m, list_layers):
    X_list_start_sol = []
    Y_list_layers = []
    for i in range(len(list_layers)):
        for j in range(len(list_layers[i])):
            list_start = fm.start_sol(n, m, list_layers[i][j])
            # X : Liste de solutions par layer (List de list de starts de chaque solution)
            X_list_start_sol.append(list_start)
            # Y : Liste des layers de chaque solution (List de int)
            Y_list_layers.append(i)
    # nb_sols = len(X_list_start_sol)
    X_train, X_test, y_train, y_test = train_test_split(X_list_start_sol, Y_list_layers, test_size=0.2, random_state=42)
    
    #With comparison of different parameters
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
    conditions = extract_conditions(tree_rules)
    return clf, conditions



# Analysez le texte pour obtenir les conditions à chaque nœud

def extract_conditions(tree_rules):
    conditions = []
    lines = tree_rules.split('\n')
    for line in lines:
        if '|---' in line:
            node_id_condition = line.split('|---')[-1].strip()
            print(node_id_condition)
            if node_id_condition.startswith('class'):
                continue
            if len(node_id_condition.split(' <= ')) == 2:
                node_id, condition = node_id_condition.split(' <= ')
                conditions.append([node_id, condition.strip(), '<='])
            elif len(node_id_condition.split(' > ')) == 2:
                node_id, condition = node_id_condition.split(' > ')
                conditions.append([node_id, condition.strip(), '>'])
    print(conditions)
    return conditions

# def extract_conditions(tree_text):
#     lines = tree_text.split('\n')
#     conditions = {}
#     for line in lines:
#         if '|---' in line:
#             node_id, condition = line.split('|---')[-1].strip().split(' <= ')
#             conditions[int(node_id)] = condition
#     return conditions

# def extract_conditions(tree_text):
#     lines = tree_text.split('\n')
#     conditions = {}
#     for line in lines:
#         if '|---' in line:
#             node_id_condition = line.split('|---')[-1].strip()
#             node_id, condition = node_id_condition.split(' <= ')
#             conditions[node_id.strip()] = condition.strip()
#     return conditions





def my_decision_tree_predict(list_var_starts, clf):
    
    return clf.predict([list_var_starts])[0]


#______________________________________________________________________#
