#Constructeur de la classe User
class User:

    def __init__(self):
        self.preferences = []
        
    def objectiveFunction(listeSolutions):
        #Prendre le max des ends
        k=0
        ends= []
        for sol in listeSolutions:
            ends.append([])
            for i in sol.get_all_var_solutions():
                ends[k].append(i.get_end())
            k+=1
        ends_max = []
        for i in ends:
            ends_max.append(max(i))
        return ends_max

    def classerSolutions(self, listeSolutions):
        self.preferences.append(sol for sol in listeSolutions)
        objFunction = self.objectiveFunction(self.preferences)
        #Trier les ends_max par ordre croissant
        objFunction.sort()
        #recupérer les index des ends_max
        index = []
        for i in objFunction:
            index.append(objFunction.index(i))
        #classer les solutions par ordre de index
        self.preferences = [self.preferences[i] for i in index]

    def getPreferences(self):
        return self.preferences