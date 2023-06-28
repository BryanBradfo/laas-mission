from User import *

#Vérifier que deux solutions qui se suivent respectent bien l'ordre
def test_preferences(user, list_sols, list_indices_pref):
        for j in len(list_indices_pref) - 1:
            if (user.objectiveFunction(list_sols[list_indices_pref[j]])>objectiveFunction(list_sols[list_indices_pref[j+1]])):
               return False
        return True

#Vérifier que les solutions proposées lors d'une itération sont différentes de celles de l'itération précédente
def test_differences_iterations (list_sols_old, list_sols_new):
    for sol in list_sols_new:

        if sol in list_sols_old:
            return False
    return True
    
