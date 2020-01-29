from __future__ import print_function
from ortools.linear_solver import pywraplp


def main():
    # Create the mip solver with the CBC backend.
    solver = pywraplp.Solver('simple_mip_program',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    timeLimit = 30
    clauses = []
    visited = []

    fileptr = open('small4.txt', 'r')
    contents = fileptr.readlines()
    for line in contents:
        if '\t' in line:
            lineContent = line.split('\t')
            lineContent[-1] = lineContent[-1].replace('\n','')
        else:
            lineContent = line.split(' ')
        
        if  lineContent[-1] == '' or lineContent[-1] == '\n':
            lineContent.pop()
        while (lineContent[-1] == '0'): 
            lineContent.pop()
            
        clauses.append([int(i) for i in lineContent])


    infinity = solver.infinity()
    
    variables = []
   
    print('Number of variables =', solver.NumVariables())
    
    #max of cluases
    max1=0
    for i in clauses:
        if max1 < max(i):
            max1 = max(i)
    variables=[0 for i in range(0,max1+1)]
    visited=[0 for i in range(0,max1+1)]

    for clause in clauses:
        for i in clause:
            visited[i]=1
#define visited and set 1 to visited members in clauses 

    for i in range(0,max1+1):
        if visited[i] == 1:
            variables[i] = solver.IntVar(0, 1, str('x{}'.format(i)))
#define a members 
    
    
    aux = [solver.IntVar(0, infinity, 'k{}'.format(i)) for i in range(0, len(visited))]
    constraints = []
    i = 0
    for clause in clauses:
        constraints.append(0)
        constraints[i] = 0
        for j in clause:
            constraints[i] += variables[j]
        solver.Add(constraints[i] == 2*aux[i])
        i += 1
    

    solver.Add(solver.Sum(variables) >= 1)
    print('Number of constraints =', solver.NumConstraints())
    
    solver.Minimize(solver.Sum(variables))
    solver.set_time_limit(timeLimit*1000)
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
        for i in range(0,max1+1):
            if visited[i] == 1:
                print(str('x{} ='.format(i)), variables[i].solution_value())
        
    else:
        print('The problem does not have an optimal solution.')

    print('\nAdvanced usage:')
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

    print('Objective value =', int(solver.Objective().Value()))

if __name__ == '__main__':
    main()
