# At each iteration, before injecting the NN model, we need to make sure that there 
# exist at least 2 perfect NN (fully accurate) independently from the scheduling problem.

from docplex.cp.model import *
from docplex.cp.config import get_default
from Solver import *
import FunctionMain as fm


# a = 1 means that the order of the sol is 0 
# a = 0 means that the order of the sol is not 0

def activation_function(model, solver, input, weights, nb_hidden_layers, nb_neurons, id_layer = 0):

    if id_layer == 0:
        sum_input = sum(input)
    else:
        sum_input = len(input)

    S = [model.integer_var(min=-sum_input, max=sum_input, name="S{}{}".format(id_layer, j)) for j in range(nb_neurons[id_layer])]
    a = [model.binary_var(name="a{}{}".format(id_layer, j)) for j in range(nb_neurons[id_layer])]
    model.add(S)
    model.add(a)

    output = []
    for j in range(nb_neurons[id_layer]):
        
        solver.add_constraint(model, S[j] == sum(input[k] * weights[id_layer][j][k] for k in range(len(input))))

        solver.add_constraint(model, a[j] == (S[j] > 0))

        if id_layer == nb_hidden_layers: 
            return a[j]
        else: 
            output.append(a[j])

    return activation_function(model, solver, output, weights, nb_hidden_layers, nb_neurons, id_layer + 1)
     


def find_perfect_NN(data, n, m, sol_layers, nb_hidden_layers, nb_neurons, nb_try = 0):

    solver = Solver(data)
    model = CpoModel() 

    # Create the weights of the neural network
    weights0 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]
    weights = weights0 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]
    
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            for k in range(len(weights[i][j])):
                model.add(weights[i][j][k])

    for order in range(len(sol_layers)):
        for sol in sol_layers[order]:

            output_NN = activation_function(model, solver, sol, weights, nb_hidden_layers, nb_neurons)

            if order == 0:
                solver.add_constraint(model, output_NN == 1)
            else:
                solver.add_constraint(model, output_NN == 0)

    msol = model.solve(TimeLimit=60, LogVerbosity='Quiet')
    # msol = model.solve(TimeLimit=20)

    print(model.get_statistics())  
    msol.print_solution()

    # list_sol = []
    # for sol in msol:
    #     list_sol.append(sol)

    NN = []

    if len(msol) == 0:
        print("No perfect neural network found, increase the number of neurons")
        nb_neurons[0] += 1
        return find_perfect_NN(data, n, m, sol_layers, nb_hidden_layers, nb_neurons)
            
    # Are the neural networks perfect ?
    for n in range(len(msol)):
        accuracy = accurate_NN(model, solver, sol_layers, weights, nb_hidden_layers, nb_neurons)
        if accuracy:
            NN.append(msol[n])
        
    if len(NN) == 0:
        print("No perfect neural network found, increase the number of neurons")
        nb_neurons[0] += 1
        return find_perfect_NN(data, n, m, sol_layers, nb_hidden_layers, nb_neurons)
    elif len(NN) == 1:
        print("Only one perfect neural network found !")
    else:
        NN = random.sample(NN, 2)
        print("2 perfect neural networks found !")

    return NN


def accurate_NN(model, solver, sol_layers, weights, nb_hidden_layers, nb_neurons):

    # Verify that there are fully accurate 
    for order in range(len(sol_layers)):
        for sol in sol_layers[order]:

            output_NN = activation_function(model, solver, sol, weights, nb_hidden_layers, nb_neurons)

            if (output_NN == 0 and order == 0) or (output_NN == 1 and order != 0):
                return False

    return True 