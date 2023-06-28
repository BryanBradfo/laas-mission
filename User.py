#Constructeur de la classe User
class User:

    def __init__(self):
        self.preferences = []
        
    def objectiveFunction(self,sol):
        list_ends = []
        list_sol = sol.get_all_var_solutions()
        for i in range(len(list_sol) - 1):
                list_ends.append(list_sol[i].get_end())
        return max(list_ends)


    def classerSolutions(self, list_sol):
        list_obj = []
        list_temp_sol = []
        
        #liste de max_ends
        for sol in list_sol:
            list_temp_sol.append(sol)
            list_obj.append(self.objectiveFunction(sol))

        
        for pref in self.preferences:
            list_temp_sol.append(pref)
            list_obj.append(self.objectiveFunction(pref))


        # #Trier les ends_max par ordre croissant
        list_indice = sorted(range(len(list_obj)), key=lambda k: list_obj[k])
        #classer les solutions par ordre de index
        self.preferences = [list_temp_sol[i] for i in list_indice]
        
        list_equal = []
        for i in range(len(self.preferences) -1):
            list_equal.append(self.objectiveFunction(pref[i]) == self.objectiveFunction(pref[i+1]))

        return list_indice, list_equal


    def getPreferences(self):
        return self.preferences