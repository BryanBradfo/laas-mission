from docplex.cp.model import CpoModel, CpoSolver
from config import setup
setup()

class Solver:

    def __init__(self, data):
        print("\nSolver initialized !")
        self._variables = []
        self._constraints = []
        self._instance = data

    def set_variables(self, variables):
        self._variables = variables


    def add_constraint(self, constraint):
        self._constraints.append(constraint)


    def solve_init(self, model, k):
    
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
                
        # Renvoie les k premieres solutions (makespan)

        # return solver, status
        return list_sol[:k], nb_solution
        
    
    # def solve(self):

    #     # Build the model
    #     model = CpoModel() 

    #     self.add_constraint(contrainst)
    
    #     # Add the constraints
    #     for constraint in self._constraints:
    #         model.add(constraint)

    #     # Create a solver and solve the model.
    #     solver = CpoSolver()
    #     status = solver.Solve(model)

    #     # Renvoie les k premieres solutions (makespan)

    #     return solver, status