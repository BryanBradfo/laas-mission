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
        list_obj = {}
        i = 0
        list_obj2={}
        
        for sol in list_sol:
            list_obj2[i]=self.objectiveFunction(sol)
            i=i+1
        # return [sorted(list_obj).index(i) for i in range(len(list_obj))]


        for sol in list_sol:
            list_obj[i] = self.objectiveFunction(sol)
            i += 1

        j = i+1
        for pref in self.preferences:
            list_sol.append(pref)
            list_obj[j] = self.objectiveFunction(pref)
            j += 1

        # #Trier les ends_max par ordre croissant
        # list_obj.sort()

        # #recupérer les index des ends_max
        # index = []
        # for i in list_obj:
        #     index.append(list_obj.index(i))
        
        # print(index)

        list_obj_sorted = sorted(list_obj)
        #classer les solutions par ordre de index
        self.preferences = [list_sol[i] for i in list_obj_sorted]


    def getPreferences(self):
        return self.preferences