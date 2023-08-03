#Constructeur de la classe User
class User:

    def __init__(self):
        self.preferences = []
    

    # Function to compute the makespan of a solution
    def makespan(self,sol):
        list_ends = []
        list_sol = sol.get_all_var_solutions()
        for i in range(len(list_sol) - 1):
                if "T" in list_sol[i].expr.name :
                    # get the tasks ends
                    list_ends.append(list_sol[i].get_end())
                
        return max(list_ends)
    

    # Function to compute the regualrity of the waiting time between tasks for each machine of a solution 
    def regularity(self, sol, n, m):
        waiting_time = [[] for i in range(m)]
        machines = [[] for i in range(m)]
        list_obj = []

        for j in range(m):
            for i in range(n):
                # Add the tasks associated to the machine j
                machines[j].append(sol.get_value("T{}-{}".format(i,j)))
            # Sort the tasks by start time
            machines[j] = sorted(machines[j], key=lambda k: k.start)
        
        for j in range(m):
            for i in range(len(machines[j])-1):
                # Compute and add the waiting time between the task i and the task i+1 for the machine j
                waiting_time[j].append(machines[j][i+1].start - machines[j][i].end)

        for machine in range(m):
            sum = 0
            for i in range(len(waiting_time)-1):
                for j in range(i+1, len(waiting_time[i])):
                    # Compute the sum of the absolute value of the difference between the waiting time of 
                    # the task i and the task j which represents the regularity of the waiting time between tasks for the machine j
                    sum += abs(waiting_time[machine][j] - waiting_time[machine][i])
            list_obj.append(sum)

        sum = 0
        for i in range(len(list_obj)):
            # Compute the sum of each machine of a solution
            sum += list_obj[i]
        
        return sum


    # Function to rank the all the solutions by makespan (simulation of the user's preferences)
    def rank_by_pref_makespan(self, nbLayer, list_sol):
        list_obj = []
        list_temp_sol = []
        list_layers_fixed = [[] for i in range(nbLayer)]
        
        
        #liste de max_ends
        for sol in list_sol:
            list_temp_sol.append(sol)
            # Compute the makespan of each solution
            list_obj.append(self.makespan(sol))

        
        for pref in self.preferences:
            list_temp_sol.append(pref)
            # Compute the makespan of each preferences (previous solutions)
            list_obj.append(self.makespan(pref))

        # Sort the solutions by makespan
        list_indice = sorted(range(len(list_obj)), key=lambda k: list_obj[k])
        # Sort the preferences and the solutions by the same order
        self.preferences = [list_temp_sol[i] for i in list_indice]

        min_obj = min(list_obj)
        max_obj = max(list_obj)
        
        print("Le min de list_obj est", min_obj)
        print("Le max de list_obj est", max_obj)

        for sol in self.preferences:
            for i in range(0, nbLayer):
                obj_sol = self.makespan(sol)
                # Class the solutions in different layers depending on their makespan
                if ((obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1) and obj_sol < min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i < nbLayer-1)
                or (obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1)) and obj_sol <= min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i == (nbLayer-1)):
                    list_layers_fixed[i].append(sol)
                    

        return list_obj, list_layers_fixed



    # Function to rank the all the solutions by regularity and makespan (simulation of the user's preferences)
    def rank_by_pref_regularity(self, nbLayer, list_sol, type_operation, n, m):
        list_obj = []
        list_temp_sol = []
        list_layers_fixed = [[] for i in range(nbLayer)]
        
        # Compute the regularity and the makespan of each solution
        if type_operation == "plus":
            for sol in list_sol:
                list_temp_sol.append(sol)
                list_obj.append(self.makespan(sol) + self.regularity(sol, n, m))
            
            for pref in self.preferences:
                list_temp_sol.append(pref)
                list_obj.append(self.makespan(pref) + self.regularity(pref, n, m))

        else:
            for sol in list_sol:
                list_temp_sol.append(sol)
                list_obj.append(self.makespan(sol) * self.regularity(sol, n, m))

            for pref in self.preferences:
                list_temp_sol.append(pref)
                list_obj.append(self.makespan(pref) * self.regularity(pref, n, m))

        # Sort the solutions by makespan
        list_indice = sorted(range(len(list_obj)), key=lambda k: list_obj[k])
        # Sort the preferences and the solutions by the same order
        self.preferences = [list_temp_sol[i] for i in list_indice]

        min_obj = min(list_obj)
        max_obj = max(list_obj)
        
        print("Le min de list_obj est", min_obj)
        print("Le max de list_obj est", max_obj)

        if type_operation == "plus":
            for sol in self.preferences:
                for i in range(0, nbLayer):
                    obj_sol = self.makespan(sol) + self.regularity(sol, n, m)
                    # Class the solutions in different layers depending on their makespan + regularity
                    if ((obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1) and obj_sol < min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i < nbLayer-1)
                    or (obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1)) and obj_sol <= min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i == (nbLayer-1)):
                        list_layers_fixed[i].append(sol)
        else:
            for sol in self.preferences:
                for i in range(0, nbLayer):
                    obj_sol = self.makespan(sol) * self.regularity(sol, n, m)
                    # Class the solutions in different layers depending on their makespan * regularity
                    if ((obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1) and obj_sol < min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i < nbLayer-1)
                    or (obj_sol >= min_obj + i*(max_obj-min_obj)/(nbLayer-1)) and obj_sol <= min_obj + (i+1)*(max_obj-min_obj)/(nbLayer-1) and i == (nbLayer-1)):
                        list_layers_fixed[i].append(sol)
                    

        return list_obj, list_layers_fixed
    


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


    
    # Function to get the matrix of the start of the preferences
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
    

    # Check if the order is coherent 
    def test_preferences(self, list_sols, type_operation, n, m):

        if type_operation == "plus":
            for i in range(len(list_sols) - 1):
                if (self.makespan(list_sols[i]) + self.regularity(list_sols[i], n, m) > self.makespan(list_sols[i+1]) + self.regularity(list_sols[i], n, m)):
                    return False
        else:
            for i in range(len(list_sols) - 1):
                if (self.makespan(list_sols[i]) * self.regularity(list_sols[i], n, m) > self.makespan(list_sols[i+1]) * self.regularity(list_sols[i], n, m)):
                    return False
        return True
    

    # Check that all the solutions are different
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

