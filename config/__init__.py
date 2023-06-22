# Configure docplex to use a local solver
import os
import shutil
import sys
from docplex.cp.config import set_default, get_default, LOCAL_CONTEXT

DEFAULT_STUDENT_PARAMETERS = {
    'Presolve': 'Off',
    'Workers': 1
}

CPOPTIMIZER_EXEC = "cpoptimizer"

INSA_CPOPTIMIZER_PATH = \
  '/usr/local/insa/ibm_cplex_studio-12.9/cpoptimizer/bin/x86-64_linux'


def setup(**kargs):
    # Default parameters for students:
    for k, v in DEFAULT_STUDENT_PARAMETERS.items():
        kargs.setdefault(k, v)

    # Update log output (does not work... )
    LOCAL_CONTEXT['log_output'] = sys.stdout

    # Set default parameters
    LOCAL_CONTEXT['params'].update(**kargs)

    # Switch to local context
    set_default(LOCAL_CONTEXT)
    #Change this if you use your local machine with your installation and the right version 
    #os.environ['PATH'] += ':' + INSA_CPOPTIMIZER_PATH
    #My local installation 
    os.environ['PATH'] += ':/Users/msiala/Applications/CPLEX_Studio129/cpoptimizer/bin/x86-64_osx'
    
