# **Tell Me How You Rank, I Tell You What You Like**

This project is an implementation of the Job-shop problem, a well-known problem in the field of Operations Research. In this problem, you are given n jobs, each consisting of m tasks. There are m machines available to execute these tasks. Each task has a duration and is processed by a specific machine. The objective is to find the optimal allocation of tasks to machines in order to minimize the makespan, which is the completion time of the last task.

Additionally, we consider the user's preferences in task allocation. For example, the user may prefer task allocations with more evenly distributed waiting times. This preference is taken into account while finding the optimal solution.

## How to Run the Code 

To  try out the code, follow these steps:

1. Clone the project repository from GitHub.
2. Install the required dependencies, including docplex, numpy, and matplotlib. You can install docplex by running the command pip install docplex in your command prompt or terminal. (for a restricted version of docplex otherwise you can follow (*) below)
3. You are now ready to run and explore the project.

(*) In order to have a unrestricted version, you can install the academic version of docplex. For this, you can do it as follows : 
- Go to https://www.ibm.com/products/ilog-cplex-optimization-studio?_gl=1*1m090s2*_ga*MTczODI4NjA2MC4xNjgzMDYwMTI1*_ga_FYECCCS21D*MTY5MDE4NzExOS4zOS4wLjE2OTAxODcxMTkuMC4wLjA and enter your student e-mail address.
- Fill in the forms and follow the instructions.
- Once logged in, go to https://www.ibm.com/academic/topic/data-science and check that you are logged in.
- Scroll down to "Courseware, Software, Resources", then click on Software.
- After clicking, press the arrow associated with the ILOG CPLEX Optimization Studio box and follow the download.
- Once the download is complete, open your command terminal as an administrator.
- Then go to C:/User/Programs/IBM/ILOG/CPLEX_Studio2211/python (make a cd).
- Finally, run python3 setup.py install and check that the installation is correct.
- Then open jupyter notebook and the Python API is up and running.
## How to get the objective value of regularity + makespan

To get the objective value of regularity + makespan, you need to run the following jupyter notebook files:

**Optimal_regularity.ipynb**

N.B. : You have to possess the academic license of CPLEX to run this code.

## I Tell You What You Like with clustering

If you want to run the code with clustering, you need to run the following jupyter notebook files:

**ITellYouWhatYouLikeClustering.ipynb**: The main code for solving the Job-shop problem with user preferences and clustering.

This file calls different functions from the following files:
- Solver.py: This file contains the class Solver which is used to solve the Job-shop problem.
- User.py: This file contains the class User which is used to create a user with his preferences.
- FunctionMain.py: This file contains the main functions used in the code.
- my_clustering.py: This file contains the functions used for clustering.

N.B. : ITellYouWhatYouLike.ipynb is the old version of the Jupyter Notebook that contains the main code for solving the Job-shop problem with user preferences.

## I Tell You What You Like with neural network

* If you want to run the code with neural network, you need to run the following jupyter notebook files:

**NeuralNetwork.ipynb**: The main code for solving the Job-shop problem with user preferences and neural network.
In this file, the problem is solved with two neural netwoks. 

This file calls different functions from the following files:
- Solver.py: This file contains the class Solver which is used to solve the Job-shop problem.
- User.py: This file contains the class User which is used to create a user with his preferences.

* If you want to test the code with the neural network approach, you need to run the following jupyter notebook files and modify it :

test_NN.ipynb: The main code for solving the Job-shop problem with user preferences and neural network.


## Requirements 

Before running the project, make sure you have the following libraries installed:

- docplex: This library provides the optimization capabilities required to solve the Job-shop problem. (pip install dcplex)
- numpy: This library is used for numerical computations and array manipulation.
- matplotlib: This library is used for visualizing the results.

If any of these libraries are missing, you can install them using pip, the Python package installer.

## Projet Structure

The project repository consists of the following files and folders:

- Clustering_binaire: Solving the problem by the approach of "binary clustering", you can just execute if you would like to try this approach :
    - main_cb.py
- Clustering_agglo: Solving the problem by the approach of "agglomerative clustering", you can just execute if you would like to try this approach :
    - main_ca.py
- bdt: Solving the problem by the approach of "binary decision tree", you can just execute if you would like to test:
    - main_dt.py
- optimal_value : Computing the optimal objective value of a certain instance (for the different types of operations : sum between makespan and regularity, multiplication between makespan and regularity and just the optimization of makespan)
    - main_optval.py
 - test : Comparing every approaches for a list of instance and among a list of operations. Compute this comparison with
    - script_text.py

- ITellYouWhatYouLike.ipynb: This Jupyter Notebook contains the main code for solving the Job-shop problem with user preferences.
- README.md: This file provides an overview of the project and instructions for running the code.
- Solver.py, User.py, clustering.py, FunctionMain.py : Python classes which are essentials for running the code. 

If you have any questions or feedback, please don't hesitate to reach out.

Happy coding!
