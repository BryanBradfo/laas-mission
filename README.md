# Tell Me How You Rank, I Tell You What You Like

This project is an implementation of the Job-shop problem, a well-known problem in the field of Operations Research. In this problem, you are given n jobs, each consisting of m tasks. There are m machines available to execute these tasks. Each task has a duration and is processed by a specific machine. The objective is to find the optimal allocation of tasks to machines in order to minimize the makespan, which is the completion time of the last task.

Additionally, we consider the user's preferences in task allocation. For example, the user may prefer task allocations with more evenly distributed waiting times. This preference is taken into account while finding the optimal solution.

## How to Run the Code 

To  try out the code, follow these steps:

1. Clone the project repository from GitHub.
2. Install the required dependencies, including docplex, numpy, and matplotlib. You can install docplex by running the command pip install docplex in your command prompt or terminal.
3. Launch the Jupyter Notebook file ITellYouWhatYouLike.ipynb.
4. You are now ready to run and explore the project.

## Requirements 

Before running the project, make sure you have the following libraries installed:

- docplex: This library provides the optimization capabilities required to solve the Job-shop problem. (pip install dcplex)
- numpy: This library is used for numerical computations and array manipulation.
- matplotlib: This library is used for visualizing the results.

If any of these libraries are missing, you can install them using pip, the Python package installer.

## Projet Structure

The project repository consists of the following files:

- ITellYouWhatYouLike.ipynb: This Jupyter Notebook contains the main code for solving the Job-shop problem with user preferences.
- README.md: This file provides an overview of the project and instructions for running the code.
- Solver.py, User.py, clustering.py, FunctionMain.py : Python classes which are essentials for running the code. 

If you have any questions or feedback, please don't hesitate to reach out.

Happy coding!
