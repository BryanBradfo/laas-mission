from docplex.cp.model import *
from docplex.cp.config import get_default
import time

class Solver:

    def __init__(self, data):
        print("\nSolver initialized !")
        self._variables = []
        self._constraints = []
        self._instance = data

    def set_variables(self, variables):
        self._variables = variables

    def add_variable(self, variable):
        self._variables.append(variable)

    def add_constraint(self, constraint):
        self._constraints.append(constraint)


    def solve(self, k, n, m, T_machine, T_duration, duration):

        model = CpoModel() 

        tps1 = time.time()

        # --------- Create the model variables 
        print("\nCreating the model variables...")
        # Create task interval variables and add them to the solver

        variables = [[None for j in range(m)] for i in range(n)]
        for i in range(n):
            for j in range(m):
                # print(duration[i][j])
                variables[i][j] = model.interval_var(size=int(duration[i][j]), name="T{}-{}".format(i,j))

        # ------------ Add variables to the solver
        self.set_variables(variables)
        print("Model variables created !")

        # ------------ Add constraints to the solver

        print("\nAdding precedence constraints to the solver...")
        # Add precedence constraints
        for i in range(n):
            for j in range(1,m):
                # print(variables[i][T_machine[i*m + j-1]])
                # print(variables[i][T_machine[i*m + j]])
                self.add_constraint(end_before_start(variables[i][T_machine[i*m + j-1]], variables[i][T_machine[i*m + j]]))
        print("Precedence constraints added !")

        print("\nAdding disjunctive constraints to the solver...")
        # Add disjunctive constraints 
        for machine in range(m):
            self.add_constraint(no_overlap([variables[i][machine] for i in range(n)]))
        print("Disjunctive constraints added !")

        # Add the constraints
        for constraint in self._constraints:
            model.add(constraint)

        # Create a solver and solve the model.
        # solver = CpoSolver()
        # status = solver.Solve(model)

        # msol = model.start_search(SearchType="DepthFirst", TimeLimit=10)

        msol = model.start_search(SearchType="DepthFirst", LogVerbosity="Quiet", TimeLimit=10)

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
        return list_sol[:k], nb_solution, tps2 - tps1
        