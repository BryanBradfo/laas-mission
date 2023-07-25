# At each iteration, before injecting the NN model, we need to make sure that there 
# exist at least 2 perfect NN (fully accurate) independently from the scheduling problem.

from docplex.cp.model import *
from docplex.cp.config import get_default
import Solver
import FunctionMain as fm


def find_perfect_NN(data, n, m, sol_layers):

    solver = Solver(data)
    model = CpoModel() 

    nb_hidden_layers = model.integer_var(min=1, max=5, name="nb_hidden_layers")

    nb_neurons = [model.integer_var(min=1, max=10, name="nb_neurons{}".format(i)) for i in range(nb_hidden_layers+1)]

    # Create the weights of the neural network
    weights0 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]

    weights = weights0 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]

    for order in range(len(sol_layers)):
        for sol in sol_layers[order]:

            output_NN = fm.activation_function(model, solver, sol, weights, nb_hidden_layers, nb_neurons)

            if order == 0:
                solver.add_constraint(model, output_NN == 1)
            else:
                solver.add_constraint(model, output_NN == 0)

    msol = model.solve()

    return msol