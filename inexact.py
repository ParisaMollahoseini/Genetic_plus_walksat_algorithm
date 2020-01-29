import random
from datetime import datetime
import copy


probabilityNumber = 0.5
satisfiabilityNumber = 0

def parentChance(objectiveValue):
    # Chance of being a parent for each chromosome
    parentSelectionProb = [0 for i in range(0,len(objectiveValue))]
    # Let chromosomes with -1 or 0 objective value have parental chance
    fitness = [1/objectiveValue[i] for i in range(0, len(objectiveValue))]
    s = sum(fitness)
    for i in range(0, len(objectiveValue)):
        parentSelectionProb[i] = (fitness[i] / s)

    return parentSelectionProb


def crossover(population, chance):
    newPop = []
    parents = []
    children = []


    sortedChances = copy.deepcopy(chance)
    sortedChances = sorted(sortedChances, reverse=True)
    for i in range(len(chance)):
        parentIndex = chance.index(sortedChances[i])
        parents.append(population[parentIndex])

    for i in range(0,int(P_SIZE/2)):
        newPop.append(parents[i])

    # Choose parents based on roulette wheel selection
    for i in range(0, len(population)):
        randomChance = random.random()
        accumulatedChance = 0
        for j in range(0, len(chance)):
            accumulatedChance += sortedChances[j]
            if accumulatedChance > randomChance:
                parent1 = parents[j]
                break
        randomChance = random.random()
        accumulatedChance = 0
        for j in range(0, len(chance)):
            accumulatedChance += sortedChances[j]
            if accumulatedChance > randomChance:
                parent2 = parents[j]
                break

        # Multi point crossover
        point1 = random.randint(1,len(parent1)-1)
        #point2 = random.randint(int(n/2), n-1)
        child = copy.deepcopy(parent1)
        for i,k in enumerate(parent1.keys()):
            if (i >= point1):
                child[k] = parent2[k]


        children.append(child)


    for i in range(0, P_SIZE):
        children[i] = walkSAT(children[i], probabilityNumber, 1000)

    for i in range(0, P_SIZE):
        objectivefunc[i] = objectiveFunction(children[i])
    childrenChance = parentChance(objectivefunc)

    sortedChildren = []
    sortedChances = copy.deepcopy(childrenChance)
    sortedChances = sorted(sortedChances, reverse=True)
    for i in range(len(childrenChance)):
        childIndex = childrenChance.index(sortedChances[i])
        sortedChildren.append(children[childIndex])

    for i in range(0, int(P_SIZE/2)):
        newPop.append(sortedChildren[i])

    return newPop


def mutation(population):
    for pop in population:
        j = random.randint(0,len(pop)-1)
        if random.random() > 0.08:
            pop[j] = (pop[j] + 1 )% 2



bad_clauses=[]
def walkSAT(pop_dict, p, max_flips):
    bad_clause = []
    for i in range(max_flips):
        objectiveFunction(pop_dict)
        if not bad_clauses:
            global satisfiabilityNumber
            print('satifiable')
            satisfiabilityNumber += 1
            return pop_dict
        else:
            rand1 = random.randint(0, len(bad_clauses)-1)
            bad_clause = bad_clauses[rand1]
            if random.random() > p:
                #print('if')
                rand2 = random.randint(0, len(bad_clause)-1)
                variable = bad_clause[rand2]
                pop_dict[variable] = pop_dict[variable] ^ 1
            else:
                #print('else')
                max1=0
                max_mem=0
                bad_clause_variables = [0 for i in range(0,len(bad_clause))]
                for member in bad_clause:
                    for one_bad_clause in bad_clauses:
                        if member in one_bad_clause:
                            bad_clause_variables[bad_clause.index(member)]+=1
                    if max1 < bad_clause_variables[bad_clause.index(member)]:
                        max_mem=member
                        max1=bad_clause_variables[bad_clause.index(member)]

                pop_dict[max_mem] = pop_dict[max_mem] ^ 1
    return pop_dict

flag_of_satisfy=0
def objectiveFunction(pop_dict):
    global flag_of_satisfy
    flag_of_satisfy = 0
    bad_clauses.clear()
    # Population objective value
    #satisfy = 1
    variable_true_no = 0
    for clause in clauses:
        temp=0
        #print(clause)
        for k in clause:
            if pop_dict[k] == 1:
                temp+=1
        if temp %2 != 0:
            flag_of_satisfy = 1
            bad_clauses.append(clause)

    for val in pop_dict.values():
        if val == 1:
            variable_true_no += 1



    if variable_true_no == 0:
        return 10000000

    return variable_true_no*10+len(bad_clauses)*100


# Population size
initial_population = []

clauses = []
variables = {}
P_SIZE = 20

random.seed()
fileptr = open('large2.txt', 'r')
contents = fileptr.readlines()
for line in contents:
    if '\t' in line:
        lineContent = line.split('\t')
        lineContent[-1] = lineContent[-1].replace('\n','')
    else:
        lineContent = line.split(' ')

    if  lineContent[-1] == '' or lineContent[-1] == '\n':
        lineContent.pop()
    while(lineContent[-1] == '0'):
        lineContent.pop()

    clauses.append(lineContent)
    for i in lineContent:
        variables[i] = random.randint(0,1)


for i in range(0, P_SIZE):
    temp = copy.deepcopy(variables)
    for i, key in enumerate(temp.keys()):
            temp[key] = random.randint(0,1)
    temp = walkSAT(temp, probabilityNumber, 1000)
    initial_population.append(temp)



iteration = 20
lastPop = []
add1 = 0.025
flag = 1
objectivefunc = [0 for i in range(0, P_SIZE)]
# Algorithm's main loop
while iteration > 0:
    satisfiabilityNumber = 0
    objectivefunc = [0 for i in range(0, P_SIZE)]
    for i in range(0, P_SIZE):
        objectivefunc[i] = objectiveFunction(initial_population[i])
    parentsChance = parentChance(objectivefunc)
    children = crossover(initial_population, parentsChance)
    initial_population = children
    #print('children : ',children)
    #mutation(children)
    lastPop = children

    if satisfiabilityNumber < 3:
        if probabilityNumber < 1:
            print("prob_no:",probabilityNumber)
            probabilityNumber += add1
            iteration += 1
        elif flag == 1:
            probabilityNumber = 0.5
            add1=0.0125
            iteration += 1
            flag = 0
        else:
            break
    #print(iteration)
    iteration -= 1


answerIndex = objectivefunc.index(min(objectivefunc))
print(objectivefunc)
answerChromosome = lastPop[answerIndex]
objectiveFunction(answerChromosome)
if flag_of_satisfy == 1:
    print("unsatisiable but the min no of bad clauses is  : ",len(bad_clauses))
print("answer is ",answerChromosome,"\n", sum(answerChromosome.values()))


