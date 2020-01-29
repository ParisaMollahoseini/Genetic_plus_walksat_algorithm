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
            for i in range(5):
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


def objectiveFunction(pop_dict):
    bad_clauses.clear()
    # Population objective value
    satisfy = 1
    variable_true_no = 0
    for clause in clauses:
        temp=0
        #print(clause)
        for k in clause:
            if pop_dict[k] == 1:
                temp+=1
        if temp %2 != 0:
            satisfy = 0
            bad_clauses.append(clause)


    if satisfy == 0:
        return 10000000

    for val in pop_dict.values():
        if val == 1:
            variable_true_no += 1
    
    if variable_true_no == 0:
        return 10000000
    return variable_true_no


# Population size
initial_population = []

clauses = []
variables = {}
P_SIZE = 20

fileptr = open('small2.txt', 'r')
contents = fileptr.readlines()
for line in contents:
    if '\t' in line:
        lineContent = line.split('\t')
        lineContent[-1] = lineContent[-1].replace('\n','')
    else:
        lineContent = line.split(' ')
    
    if  lineContent[-1] == '' or lineContent[-1] == '\n':
        lineContent.pop()
    if lineContent[-1] == '0': 
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


for i in range(0, P_SIZE):
    objectivefunc[i] = objectiveFunction(initial_population[i])
    if bad_clauses:
        objectivefunc[i] += 10000000

answerIndex = objectivefunc.index(min(objectivefunc))
print(objectivefunc)
answerChromosome = lastPop[answerIndex]
print(answerChromosome, objectivefunc[answerIndex])






"""
for large3.txt
prob_no: 0.5
prob_no: 0.525
prob_no: 0.55
prob_no: 0.5750000000000001
prob_no: 0.6000000000000001
prob_no: 0.6250000000000001
prob_no: 0.6500000000000001
prob_no: 0.6750000000000002
prob_no: 0.7000000000000002
prob_no: 0.7250000000000002
prob_no: 0.7500000000000002
prob_no: 0.7750000000000002
prob_no: 0.8000000000000003
prob_no: 0.8250000000000003
prob_no: 0.8500000000000003
prob_no: 0.8750000000000003
prob_no: 0.9000000000000004
prob_no: 0.9250000000000004
prob_no: 0.9500000000000004
prob_no: 0.9750000000000004
prob_no: 0.5
prob_no: 0.5125
prob_no: 0.5249999999999999
prob_no: 0.5374999999999999
prob_no: 0.5499999999999998
prob_no: 0.5624999999999998
prob_no: 0.5749999999999997
prob_no: 0.5874999999999997
prob_no: 0.5999999999999996
prob_no: 0.6124999999999996
prob_no: 0.6249999999999996
prob_no: 0.6374999999999995
prob_no: 0.6499999999999995
prob_no: 0.6624999999999994
prob_no: 0.6749999999999994
prob_no: 0.6874999999999993
prob_no: 0.6999999999999993
prob_no: 0.7124999999999992
prob_no: 0.7249999999999992
prob_no: 0.7374999999999992
prob_no: 0.7499999999999991
prob_no: 0.7624999999999991
prob_no: 0.774999999999999
prob_no: 0.787499999999999
prob_no: 0.7999999999999989
prob_no: 0.8124999999999989
prob_no: 0.8249999999999988
prob_no: 0.8374999999999988
prob_no: 0.8499999999999988
prob_no: 0.8624999999999987
prob_no: 0.8749999999999987
prob_no: 0.8874999999999986
prob_no: 0.8999999999999986
prob_no: 0.9124999999999985
prob_no: 0.9249999999999985
satifiable
prob_no: 0.9374999999999984
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
satifiable
[214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214, 214]
{'193': 0, '316': 1, '97': 1, '322': 0, '74': 1, '365': 1, '71': 1, '368': 0, '52': 0, '377': 1, '15': 0, '258': 0, '191': 0, '319': 1, '62': 1, '260': 1, '170': 0, '231': 1, '10': 0, '300': 1, '58': 1, '230': 0, '145': 1, '354': 1, '139': 0, '279': 0, '140': 1, '378': 1, '35': 0, '296': 0, '105': 0, '238': 0, '152': 0, '399': 0, '61': 0, '259': 0, '99': 1, '314': 1, '157': 0, '339': 1, '94': 1, '264': 0, '88': 0, '298': 1, '75': 1, '207': 0, '33': 1, '342': 1, '143': 0, '370': 0, '133': 0, '208': 0, '127': 0, '212': 0, '91': 1, '389': 0, '288': 1, '90': 1, '386': 0, '253': 0, '269': 0, '126': 0, '274': 1, '8': 1, '320': 0, '27': 0, '305': 1, '83': 1, '384': 1, '6': 1, '277': 0, '67': 0, '374': 0, '153': 0, '393': 1, '109': 1, '332': 0, '195': 0, '333': 0, '64': 1, '336': 0, '119': 0, '213': 1, '120': 0, '383': 0, '4': 0, '307': 1, '199': 1, '350': 0, '375': 0, '167': 1, '257': 0, '360': 0, '102': 1, '293': 1, '9': 1, '267': 1, '17': 0, '214': 1, '352': 1, '36': 0, '405': 1, '104': 0, '86': 0, '243': 0, '224': 1, '84': 1, '211': 0, '85': 0, '160': 1, '54': 0, '261': 0, '68': 1, '363': 1, '24': 0, '278': 0, '81': 1, '265': 1, '45': 1, '340': 1, '103': 1, '186': 1, '403': 0, '59': 0, '366': 0, '7': 1, '240': 0, '134': 0, '347': 1, '149': 0, '228': 1, '180': 0, '196': 0, '334': 1, '43': 1, '29': 0, '321': 1, '96': 0, '272': 0, '60': 1, '223': 1, '150': 1, '304': 1, '1': 1, '206': 0, '41': 0, '268': 1, '371': 1, '192': 1, '344': 1, '80': 0, '286': 1, '404': 1, '162': 0, '309': 1, '13': 0, '276': 0, '181': 1, '351': 0, '95': 0, '329': 0, '107': 0, '280': 1, '184': 1, '256': 1, '22': 1, '323': 0, '76': 1, '289': 1, '49': 0, '317': 0, '30': 0, '221': 0, '44': 0, '335': 1, '187': 0, '51': 1, '219': 1, '125': 1, '204': 1, '355': 0, '299': 1, '376': 0, '82': 1, '255': 1, '118': 0, '215': 0, '177': 1, '327': 0, '32': 1, '115': 0, '66': 0, '396': 0, '56': 0, '237': 1, '48': 1, '202': 0, '285': 1, '400': 0, '40': 1, '284': 0, '154': 0, '190': 1, '310': 0, '2': 0, '282': 1, '236': 1, '171': 0, '302': 1, '338': 1, '379': 1, '183': 0, '294': 0, '138': 0, '275': 1, '222': 1, '79': 1, '50': 0, '311': 0, '166': 1, '301': 1, '297': 0, '137': 1, '129': 1, '247': 0, '132': 0, '388': 1, '25': 0, '330': 1, '189': 0, '14': 0, '178': 1, '57': 1, '110': 1, '313': 0, '161': 1, '348': 1, '175': 0, '12': 0, '369': 0, '131': 1, '174': 1, '200': 1, '343': 0, '123': 0, '390': 1, '197': 1, '53': 1, '116': 0, '341': 1, '290': 1, '89': 0, '273': 1, '142': 0, '328': 0, '281': 1, '21': 0, '63': 1, '331': 0, '69': 1, '73': 0, '225': 1, '164': 1, '292': 0, '70': 1, '359': 1, '124': 1, '406': 1, '163': 1, '130': 1, '20': 1, '391': 0, '156': 0, '385': 0, '87': 1, '306': 0, '136': 0, '101': 1, '47': 0, '210': 0, '362': 0, '361': 1, '270': 1, '165': 1, '229': 0, '364': 1, '239': 0, '252': 1, '114': 1, '37': 1, '353': 1, '345': 1, '395': 0, '151': 0, '205': 0, '176': 0, '408': 0, '185': 1, '3': 1, '26': 1, '217': 0, '141': 0, '295': 0, '271': 1, '55': 1, '324': 0, '392': 1, '312': 1, '16': 1, '380': 0, '194': 1, '100': 1, '241': 1, '42': 0, '397': 1, '326': 0, '357': 1, '172': 1, '19': 1, '117': 0, '121': 1, '232': 1, '77': 0, '11': 1, '315': 0, '144': 0, '39': 0, '244': 1, '92': 0, '18': 0, '337': 1, '407': 0, '251': 0, '308': 1, '169': 0, '227': 1, '248': 0, '245': 1, '226': 0, '188': 0, '242': 1, '373': 1, '233': 1, '5': 0, '235': 0, '122': 1, '209': 1, '401': 0, '398': 1, '254': 0, '108': 0, '148': 0, '34': 0, '382': 1, '318': 1, '356': 0, '147': 1, '218': 1, '249': 1, '112': 1, '250': 0, '367': 1, '325': 0, '23': 0, '402': 1, '38': 1, '72': 1, '135': 0, '179': 1, '346': 1, '31': 1, '381': 0, '146': 1, '246': 1, '266': 1, '201': 1, '113': 0, '168': 1, '358': 0, '220': 0, '106': 1, '173': 1, '98': 1, '394': 1, '262': 1, '111': 1, '28': 1, '283': 1, '263': 1, '291': 0, '65': 1, '78': 1, '159': 0, '182': 0, '203': 1, '128': 1, '198': 1, '349': 0, '155': 1, '158': 0, '46': 0, '303': 1, '234': 0, '93': 0, '287': 1, '216': 1, '387': 0, '372': 0} 214
"""
