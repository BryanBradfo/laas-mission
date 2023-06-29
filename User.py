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
    

    def start_pref(self, n , m, variables, bool):

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


    

    def matrix_pref(self, n , m, variables, bool):

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

