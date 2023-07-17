from docplex.cp.model import *
from docplex.cp.config import get_default
import time
import random
import numpy as np

class Solver:

    def __init__(self, data):
        self._variables = []
        self._constraints = []
        self._instance = data

    def set_variables(self, variables):
        self._variables = variables

    def get_variables(self):
        return self._variables

    def add_variable(self, variable):
        self._variables.append(variable)

    def add_constraint(self, model, constraint):
        self._constraints.append(constraint)
        model.add(constraint)



    def create_variables(self, model, n, m, duration):

        # --------- Create the model variables 
        print("\nCreating the model variables...")
        # Create task interval variables and add them to the solver

        variables = [[None for j in range(m)] for i in range(n)]
        for i in range(n):
            for j in range(m):
                # print(duration[i][j])
                variables[i][j] = model.interval_var(size=int(duration[i][j]), name="T{}-{}".format(i,j))

        # ------------ Add variables to the solver
        self.add_variable(variables)
        print("Model variables created !")

    def solve(self, model, k, n, m, T_machine, optimalval, total_time, nb_iteration):

        tps1 = time.time()

        list_variables = self.get_variables()
        variables = list_variables[0]

        # ------------ Add constraints to the solver

        print("\nAdding precedence constraints to the solver...")
        # Add precedence constraints
        for i in range(n):
            for j in range(1,m):
                # print(variables[i][T_machine[i*m + j-1]])
                # print(variables[i][T_machine[i*m + j]])
                self.add_constraint(model, end_before_start(variables[i][T_machine[i*m + j-1]], variables[i][T_machine[i*m + j]]))
        print("Precedence constraints added !")

        print("\nAdding disjunctive constraints to the solver...")
        # Add disjunctive constraints 
        for machine in range(m):
            self.add_constraint(model, no_overlap([variables[i][machine] for i in range(n)]))
        print("Disjunctive constraints added !")

        # Add constraints that makespan < 2*optimalval
        makespan = max([end_of(variables[i][T_machine[i*m + m -1]]) for i in range(n)])
        self.add_constraint(model, makespan <= 2*optimalval)
        # self.add_constraint(model, makespan < 691)

        # # Add the constraints
        # for constraint in self._constraints:
        #     model.add(constraint)

        # Create a solver and solve the model.
        # solver = CpoSolver()
        # status = solver.Solve(model)
        variables_s_p = [variables[i][j] for j in range(m) for i in range(n)]
        SearchPhase = model.search_phase(variables_s_p, 
                                            varchooser=model.select_random_var(),
                                            valuechooser=model.select_random_value())
        model.add_search_phase(SearchPhase)
        
        msol = model.start_search(SearchType="DepthFirst", LogVerbosity="Quiet", TimeLimit=10) #total_time//nb_iteration
        # msol = model.start_search(SearchType="DepthFirst", LogVerbosity="Quiet", SolutionLimit = k, RandomSeed = k)
        # SolutionLimit=3*k, MultiPointNumberOfSearchPoints=30 +2*ind, RandomSeed = 5, DefaultInferenceLevel='Extended', OptimalityTolerance=6

        nb_solution = 0
        for sol in msol:
            nb_solution += 1
                
        # print(list_value_solution)

        list_sol = []
        for sol in msol:
            list_sol.append(sol)

        tps2 = time.time()
                
        # Renvoie les k premieres solutions (makespan)

        # return solver, status
        if k > len(list_sol):
            raise ValueError("Le nombre de solutions demandé est supérieur à la taille de la liste.")
        #récupérer les k dernières solutions
        solutions_aleatoires = random.sample(list_sol, k)
        # solutions_aleatoires = list_sol[:k]

        return solutions_aleatoires, nb_solution, tps2 - tps1
        


        
                
        