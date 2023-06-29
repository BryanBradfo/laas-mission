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
            list_equal.append(self.objectiveFunction(self.preferences[i]) == self.objectiveFunction(self.preferences[i+1]))

        return list_indice, list_equal


    def getPreferences(self):
        return self.preferences
    

    def matrix_pref(self, n , m, variables, bool):

        pref = self.getPreferences()
        print(pref)
        l = len(pref[0].get_all_var_solutions())
        matrix = [[None for j in range(l)] for i in range(len(pref))]
        
        print("Matrice des start des préférences : ")
    
        k=0
        for sol in pref:
            # print("-----------------")
            for i in range(n):
                for j in range(m):
                    print(variables[i][j])
                    var_sol = sol[variables[i][j]]
                    print(sol)
            
                    matrix[k][i*m + j] = var_sol.start
                    # var_sol = pref[k].get_all_var_solutions()[i*m + j]
            
                    # matrix[k][j] = var_sol.get_start()

            k+=1

        # for k in range (len(pref)):
        #     print("-----------------")
        #     matrix.append([])
        #     sol = pref[k].get_all_var_solutions()
        #     for j in range(len(sol)):
        #             matrix[k].append(sol[j].get_start())
        #             #matrix[k][j] = sol[j].get_start()
        #             # var_sol = pref[k].get_all_var_solutions()[i*m + j]
            
        #             # matrix[k][j] = var_sol.get_start()
        

        # for sol in pref:
        #     var_sol = []
        #     for i in range(n):
        #         for j in range(m):
                    
        #             var_sol.append( sol.get_all_var_solutions()[i*m + j].get_start())
        #     print("000000000000000000000000000000000000000000000000000000000000000000000000")
        #     matrix.append(var_sol)
        #     print(len(var_sol))
            
        if bool:
            print("Matrice des start des préférences : ")
            for i in range (len(matrix)):
                print("starts sol ", i, " : ", matrix[i])
        
        return matrix
    
    #Vérifier que deux solutions qui se suivent respectent bien l'ordre
    def test_preferences(self, list_sols, list_indices_pref):
        for j in range(len(list_indices_pref) - 1):
            if (self.objectiveFunction(list_sols[list_indices_pref[j]]) > self.objectiveFunction(list_sols[list_indices_pref[j+1]])):
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

