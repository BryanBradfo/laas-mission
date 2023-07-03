#############################
### Import libraries ###
#############################

from docplex.cp.model import *
from docplex.cp.config import get_default
import numpy as np
from Solver import *
from User import *

#############################
### Main program ###
#############################

print("\n--------Main program is loading...---------")

# Interaction with the solver

data = []

with open('./example.data', 'r') as f:    
    for line in f:
        data.append(line.strip().split())

n = int(data[0][0])
m = int(data[0][1])

T_machine = []
T_duration = []

for i in range(1,n+1):
    for j in range(0, 2*m, 2):
        T_machine.append(int(data[i][j]))
        T_duration.append(int(data[i][j+1]))

duration = np.zeros((n, m))

for i in range(n):
    for j in range(m):
        ind_machine = int(T_machine[i*m + j])
        duration[i][ind_machine] = T_duration[i*m + j]


# --------- Call Solver constructor in Solver.py

solver = Solver(data)

model = CpoModel() 

# --------- Create the model variables 
print("\nCreating the model variables...")
# Create task interval variables and add them to the solver

variables = [[None for j in range(m)] for i in range(n)]
for i in range(n):
    for j in range(m):
        # print(duration[i][j])
        variables[i][j] = model.interval_var(size=int(duration[i][j]), name="T{}-{}".format(i,j))

# ------------ Add variables to the solver
solver.set_variables(variables)
print("Model variables created !")

# ------------ Add constraints to the solver

print("\nAdding precedence constraints to the solver...")
# Add precedence constraints
for i in range(n):
    for j in range(1,m):
        # print(variables[i][T_machine[i*m + j-1]])
        # print(variables[i][T_machine[i*m + j]])
        solver.add_constraint(end_before_start(variables[i][T_machine[i*m + j-1]], variables[i][T_machine[i*m + j]]))
print("Precedence constraints added !")

print("\nAdding disjunctive constraints to the solver...")
# Add disjunctive constraints 
for machine in range(m):
    solver.add_constraint(no_overlap([variables[i][machine] for i in range(n)]))
print("Disjunctive constraints added !")

# ------------ Add objective function to the solver

# print("\nAdding objective function to the solver...")
# # print(variables[i][T_machine[i*m + m -1]])
# makespan = max([end_of(variables[i][T_machine[i*m + m -1]]) for i in range(n)])
# solver.add_constraint(model.minimize(makespan))
# print("Objective function added !")

# ------------ Solve the model

print("\nSolving the model...")
# makespan, solver = solver.solve_init(model)
msol, nb_solution = solver.solve_init(model, 3)

# ------------ Display the result

for sol in msol:
    sol.write()
print("Model solved !")


# ---------------- Interaction with the user

print("\n--------Interaction with the user...---------")

print("\nCreating the user...")
user = User()
print("User created !")

print("\nClassing solutions...")	
user.classerSolutions(msol)
print("Solutions classed !")

print("\nCreating preferences...")
pref = user.getPreferences()
print("Preferences created !")

print("\nDisplaying preferences...")
for sol in pref:
    sol.write()

print("\nPreferences : ", pref)
