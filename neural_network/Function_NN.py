# At each iteration, before injecting the NN model, we need to make sure that there 
# exist at least 2 perfect NN (fully accurate) independently from the scheduling problem.

from docplex.cp.model import *
from docplex.cp.config import get_default
sys.path.append("..")
from Solver import *
import FunctionMain as fm


# a = 1 means that the order of the sol is 0 
# a = 0 means that the order of the sol is not 0


def activation_function(model, solver, input, weights, nb_hidden_layers, nb_neurons, optimalval, id_layer = 0):

    # sum_input defines the domain of the sum of the inputs of the neuron S
    if type(input[0])!=int and input[0].is_type(Type_IntExpr):
        sum_input = 2*optimalval
    else:
        if id_layer == 0:
            sum_input = sum(input)
        else:
            sum_input = len(input)

    # Sum of the weights multiplied by the inputs
    S = [model.integer_var(min=-sum_input, max=sum_input, name="S{}{}".format(id_layer, j)) for j in range(nb_neurons[id_layer])]
    # Activation function that is 1 or 0
    a = [model.binary_var(name="a{}{}".format(id_layer, j)) for j in range(nb_neurons[id_layer])]
    model.add(S)
    model.add(a)

    output = []
    for j in range(nb_neurons[id_layer]):
        # for each neurons, compute the sum of the weights multiplied by the inputs
        solver.add_constraint(model, S[j] == sum(input[k] * weights[id_layer][j][k] for k in range(len(input))))

        # if the sum is positive, then the activation function is 1, else it is 0
        solver.add_constraint(model, a[j] == (S[j] > 0))

        # if we are at the last layer we return the output, else we continue
        if id_layer == nb_hidden_layers: 
            return a[j]
        else: 
            output.append(a[j])

    # call the function again with the output of the previous layer as input of the next layer 
    return activation_function(model, solver, output, weights, nb_hidden_layers, nb_neurons, optimalval, id_layer + 1)
     

# function that verifies if there exists at least 1 perfect NN and return one or 2 perfect NN
def find_perfect_NN(file, sol_layers, nb_hidden_layers, nb_neurons):

    n, m, data, _, _, _, optimalval = fm.get_data_from_file(file)

    # new solver and new model
    solver = Solver(data)
    model = CpoModel() 


    # Create the weights of the neural network
    weights0 = [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(0,j,k)) for k in range(n*m)] for j in range(nb_neurons[0])]]
    weights = weights0 + [[[model.integer_var(min=-1, max=1, name="w{}-{}-{}".format(i,j,k)) for k in range(nb_neurons[i-1])] for j in range(nb_neurons[i])] for i in range(1, nb_hidden_layers + 1)]
    
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            for k in range(len(weights[i][j])):
                model.add(weights[i][j][k])

    # Train the neural network
    for order in range(len(sol_layers)):
        for sol in sol_layers[order]:

            output_NN = activation_function(model, solver, sol, weights, nb_hidden_layers, nb_neurons, optimalval)
            if order == 0:
                solver.add_constraint(model, output_NN == 1)
            else:
                solver.add_constraint(model, output_NN == 0)

    print("Searching for perfect neural networks...")
    msol = model.solve(TimeLimit=20, LogVerbosity='Quiet')
    # msol = model.solve(TimeLimit=20)

    # Get the list of all the solutions
    list_sol = []
    list_sol = msol.get_all_var_solutions()
    # print(len(list_sol))

    NN = []

    # if there is no solution, we increase the number of neurons and we try again
    if list_sol == None:
        print("No perfect neural network found, increase the number of neurons")
        nb_neurons[0] += 1
        print(nb_neurons)
        return find_perfect_NN(file, sol_layers, nb_hidden_layers, nb_neurons)
            
    # Are the neural networks perfect ?
    for n in range(len(list_sol)):
        # Verify that there are fully accurate
        accuracy = accurate_NN(model, solver, sol_layers, weights, nb_hidden_layers, nb_neurons, optimalval)
        if accuracy:
            # add the NN to the list of perfect NN if it is fully accurate
            NN.append(list_sol[n])
    
    # if there is no perfect NN, we increase the number of neurons and we try again
    if len(NN) == 0:
        print("No perfect neural network found, increase the number of neurons")
        nb_neurons[0] += 1
        return find_perfect_NN(file, sol_layers, nb_hidden_layers, nb_neurons)
    elif len(NN) == 1:
        print("Only one perfect neural network found !")
    else:
        # if there are 2 or more perfect NN, we return 2 of them randomly
        NN = random.sample(NN, 2)
        print("2 perfect neural networks found !")
        # print(NN)

    return NN



def accurate_NN(model, solver, sol_layers, weights, nb_hidden_layers, nb_neurons, optimalval):

    # Verify that there are fully accurate 
    for order in range(len(sol_layers)):
        for sol in sol_layers[order]:

            output_NN = activation_function(model, solver, sol, weights, nb_hidden_layers, nb_neurons, optimalval)

            if (output_NN.equals(0) and order == 0) or (output_NN.equals(1) and order != 0):
                return False

    return True 