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
    


    def objectiveFunctionRegularity(self, sol, n, m):
        waiting_time = [[] for i in range(m)]
        machines = [[] for i in range(m)]
        list_obj = []

        for j in range(m):
            for i in range(n):
                machines[j].append(sol.get_value("T{}-{}".format(i,j)))
            # print(machines[j])
            machines[j] = sorted(machines[j], key=lambda k: k.start)
        
        for j in range(m):
            for i in range(len(machines[j])-1):
                waiting_time[j].append(machines[j][i+1].start - machines[j][i].end)

        for machine in range(m):
            sum = 0
            for i in range(len(waiting_time)-1):
                for j in range(i+1, len(waiting_time[i])):
                    sum += abs(waiting_time[machine][j] - waiting_time[machine][i])
            list_obj.append(sum)

        sum = 0
        for i in range(len(list_obj)):
            sum += list_obj[i]
        
        return sum


    def classerSolution_min_max(self, nbLayer, list_sol):
        list_obj = []
        list_temp_sol = []
        list_layers_fixed = [[] for i in range(nbLayer)]
        
        
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

        min_obj = min(list_obj)
        max_obj = max(list_obj)
        
        print("Le min de list_obj est", min_obj)
        print("Le max de list_obj est", max_obj)
        # print("List_obj :", list_obj)

        for sol in self.preferences:
            for i in range(0, nbLayer):
                obj_sol = self.objectiveFunction(sol)
                if ((obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1) and obj_sol < min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i < nbLayer-1)
                or (obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1)) and obj_sol <= min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i == (nbLayer-1)):
                    # print("{} est dans la layer {}".format(obj_sol, i))
                    list_layers_fixed[i].append(sol)
                # else:
                    # print("{} n'est pas dans la layer {} en effet {} est pas compris entre {} et {}".format(obj_sol, i, obj_sol, min_obj + ((i)*(max_obj-min_obj)/(nbLayer-1)),  min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1)))
                    
        list_equal = []
        k = 0
        for j in range(nbLayer):
            for i in range(k, len(self.preferences)):
                flag = self.preferences[i] in list_layers_fixed[j]
                list_equal.append(flag)
                k = i+1
                if not flag:
                    break
                    

        return list_indice, list_obj, list_layers_fixed, list_equal



    def classerSolutions(self, nbLayer, optimalVal, list_sol):
        list_obj = []
        list_temp_sol = []
        list_layers_fixed = [[] for i in range(nbLayer)]
        
        
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
        
        for sol in self.preferences:
            for i in range(0, nbLayer-1):
                obj_sol = self.objectiveFunction(sol)
                if (obj_sol >= optimalVal + (i*optimalVal/nbLayer) and obj_sol < optimalVal + (i+1)*optimalVal/nbLayer):
                    list_layers_fixed[i].append(sol)
                    
        list_equal = []
        k = 0
        for j in range(nbLayer):
            for i in range(k, len(self.preferences)):
                flag = self.preferences[i] in list_layers_fixed[j]
                list_equal.append(flag)
                k = i+1
                if not flag:
                    break
                    

        return list_indice, list_obj, list_layers_fixed, list_equal


    def classerSolutionRegularity_min_max(self, nbLayer, list_sol, n, m):
        list_obj = []
        list_temp_sol = []
        list_layers_fixed = [[] for i in range(nbLayer)]
        

        #liste de max_ends
        for sol in list_sol:
            list_temp_sol.append(sol)
            # print(self.objectiveFunctionRegularity(sol, n, m))
            list_obj.append(self.objectiveFunction(sol) * self.objectiveFunctionRegularity(sol, n, m))

        
        for pref in self.preferences:
            list_temp_sol.append(pref)
            list_obj.append(self.objectiveFunction(pref) * self.objectiveFunctionRegularity(pref, n, m))

        # #Trier les ends_max par ordre croissant
        list_indice = sorted(range(len(list_obj)), key=lambda k: list_obj[k])
        #classer les solutions par ordre de index
        self.preferences = [list_temp_sol[i] for i in list_indice]

        min_obj = min(list_obj)
        max_obj = max(list_obj)
        
        print("Le min de list_obj est", min_obj)
        print("Le max de list_obj est", max_obj)
        # print("List_obj :", list_obj)

        for sol in self.preferences:
            for i in range(0, nbLayer):
                obj_sol = self.objectiveFunction(sol) * self.objectiveFunctionRegularity(sol, n, m)
                if ((obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1) and obj_sol < min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i < nbLayer-1)
                or (obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1)) and obj_sol <= min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i == (nbLayer-1)):
                    # print("{} est dans la layer {}".format(obj_sol, i))
                    list_layers_fixed[i].append(sol)
                # else:
                    # print("{} n'est pas dans la layer {} en effet {} est pas compris entre {} et {}".format(obj_sol, i, obj_sol, min_obj + ((i)*(max_obj-min_obj)/(nbLayer-1)),  min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1)))
                    
        list_equal = []
        k = 0
        for j in range(nbLayer):
            for i in range(k, len(self.preferences)):
                flag = self.preferences[i] in list_layers_fixed[j]
                list_equal.append(flag)
                k = i+1
                if not flag:
                    break
                    

        return list_indice, list_obj, list_layers_fixed, list_equal
    


    def getPreferences(self):
        return self.preferences
    

    def start_pref(self, n , m, bool):

        pref = self.getPreferences()
        starts = []

        for k in range(len(pref)):
            for i in range(n):
                for j in range(m):
                    var_sol = pref[k].get_value("T{}-{}".format(i,j))
                    starts.append(var_sol.start)

            if bool:
                # print("Matrice des start des préférences : ")
                print(starts[k*n*m : k*n*m+n*m])

        return starts


    

    def matrix_pref(self, n , m, bool):

        pref = self.getPreferences()
        l = len(pref[0].get_all_var_solutions())
        matrix = [[None for j in range(l)] for i in range(len(pref))]
    
        for k in range(len(pref)):
            for i in range(n):
                for j in range(m):
                    var_sol = pref[k].get_value("T{}-{}".format(i,j))
                    
                    matrix[k][i*m + j] = var_sol.start
                    
        if bool:
            print("Matrice des start des préférences : ")
            for i in range (len(matrix)):
                print("starts sol ", i, " : ", matrix[i])
        
        return matrix
    

    #Vérifier que deux solutions qui se suivent respectent bien l'ordre
    def test_preferences(self, list_sols):
        for i in range(len(list_sols) - 1):
            if (self.objectiveFunction(list_sols[i]) > self.objectiveFunction(list_sols[i+1])):
               return False
        return True
    

    #Vérifier que les solutions proposées lors d'une itération sont différentes de celles de l'itération précédente
    def test_differences_sol(self, matrix):

        for i in range(len(matrix)):
            for k in range(i+1,len(matrix)):
                list = []
                for j in range(len(matrix[i])):
                    list.append(0 if (matrix[i][j] == matrix[k][j]) else 1)
                    
                value = sum(list)
                if value == 0:
                    return False, [matrix[i], matrix[k]], k, value
                
        return True

