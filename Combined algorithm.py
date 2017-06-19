
import random
import time
import math
import re
import sys
import xlrd as excel

from numpy import array
from numpy import nonzero

#groupby is used to sort the tuples or list of lists

from itertools import groupby

# itemgetter is used in sorting

from operator import itemgetter,attrgetter,methodcaller

##########  parsing the inputs  ############

fmsproblem = open('fmsproblem1.txt','r')
sourcecode = fmsproblem.read()
formattedarray= open("formattedfilewitharray.txt","r").read()
splitproblemline = sourcecode.split('\n')
splitproblemarray=[]

for x in splitproblemline:
    splitproblemarray.append(x.split(","))

splitproblemarraywithoutcomma=[]

for x in splitproblemarray:
    for y in x:
        splitproblemarraywithoutcomma.append(y.split(" "))
    
# job array contains [parttype,operation no,batch size,time taken for the operation,
#                                    machine number,tool slots needed for operation ]
# the file is in string format so we convert it into integers

arrayofjobs=[map(int,x) for x in splitproblemarraywithoutcomma]

#replaced batchsize and unitprocessing time by multiplying both of them and removing batchsize

def replacingbatchsize(arrayofjobs):
    temparrayofjobs=arrayofjobs
    for i in temparrayofjobs:
        i[3]=i[2]*i[3]
        i.pop(2)
    return temparrayofjobs

replacedarray = replacingbatchsize(arrayofjobs)

# this function is used to pick elements from an array containing specified numbers
# or parts at specified position and returns a new array

def arraypicker(index,indexpos,arraytoevaluate):
    temparray=[]
    for i in arraytoevaluate:
        if(i[indexpos]==index):
            temparray.append(i)
    return temparray
    
# seperates essential operations from non essential and returns new array with essential
# at the beginning of array and followed by non essential operations
    
def operationseperator(arrayfromarraypicker):
    nonessential=[]
    essential=[]
    for key,group in groupby(arrayfromarraypicker,lambda x:x[1]):
        nonessential.append(list(group))
    for element in nonessential:
        if len(element)==1:
            essential.append(element)
            nonessential.remove(element)    
        
    
    return essential+nonessential
    
#############   evaluating a fitness for a given job sequence   #############
    
def fitnessevaluation(jobsequence):
    # machine time to be edited according to the given problem,same goes for the machine slots too
    # here number of machines is 4 but a '0' is added at the start for easier computation
    machinetime=[0,480,480,480,480]
    totalmachinetime=sum(machinetime)
    machineslot=[0,5,5,5,5]
    for parttype in jobsequence:
        for operation in operationseperator(arraypicker(parttype,0,replacedarray)):
            if len(operation)==1:
                if((machinetime[operation[0][3]]-operation[0][2])>0 and 
                (machineslot[operation[0][4]]-operation[0][4])>0):
                    
                    machinetime[operation[0][3]] = machinetime[operation[0][3]] - operation[0][2]
                    machineslot[operation[0][4]] = machineslot[operation[0][4]] - operation[0][4]
                else:
                    None
            elif (len(operation)>1):
                machineoperationarray = [element[3] for element in operation]
                machinetimeoperationarray=[machinetime[element] for element in machineoperationarray]
                selectedindex=machinetimeoperationarray.index(max(machinetimeoperationarray))
                machinenumber=machineoperationarray[selectedindex]
                timetakenforoperation=[element[2] for element in operation]
                selectedoperationtime=timetakenforoperation[selectedindex]
                slottakenforoperation=[element[4] for element in operation]
                selectedoperationslot=slottakenforoperation[selectedindex]
                
                if((machinetime[machinenumber]-selectedoperationtime>0) and 
                (machineslot[machinenumber]-selectedoperationslot>0)):
                    machinetime[machinenumber]=machinetime[machinenumber]-selectedoperationtime
                    machineslot[machinenumber]=machineslot[machinenumber]-selectedoperationslot    
                else:
                    None
            else:
                None
    return (float(sum(machinetime))/totalmachinetime)
    
#remove "#" for testing the fitness evaluation of given example below
#print "fitness for the job sequence [3,7,6,2,1,8,5,4] is ",fitnessevaluation([3,7,6,2,1,8,5,4])

##################################
#Genetic algorithm               #
##################################

# selects the individuals to be participated in the mating operation

def rouletteselection(population,fitnesses):
    totalfitness=float(sum(fitnesses))
    relativefitness=[(fitness/totalfitness) for fitness in fitnesses]
    probs=[sum(relativefitness[:i+1]) for i in range(len(relativefitness))]
    newpopulation=[]
    for iteration in range(len(population)):
        r=random.random()
        for (i,individual) in enumerate(population):
            if r<=probs[i]:
                newpopulation.append(individual)
                break
    return newpopulation

# takes two job sequences and cross them over by selecting a random postion and returns two new children
# by following the crossoverrate probability

def singlepointcrossover(parent1,parent2,crossoverrate):
    r=random.random()
    if (r<=crossoverrate):
        crossoversite=random.randint(0,len(parent1))
        child1=parent1[0:crossoversite]
        child2=parent2[0:crossoversite]
        for i in range(0,len(parent2)):
            if parent2[i] in parent1[crossoversite:len(parent1)]:                       
                child1.append(parent2[i])                                               
        for i in range(0,len(parent1)):                                                                     
            if parent1[i] in parent2[crossoversite:len(parent1)]:                                                       
                child2.append(parent1[i])                                                                                               
        return (child1,child2)
    else:
        return (parent1,parent2)

# performs mating operation on the population  in mating pool
# and returns new population after mating   
    
def mating(population,crossoverrate):
    newpopulation=[]
    count=0
    random.shuffle(population)
    for iteration in range(len(population)/2):
        (A,B)=singlepointcrossover(population[count],population[count+1],crossoverrate)
        newpopulation.append(A)
        newpopulation.append(B)
        count=count+2
    return newpopulation

# randomly mutates any two positions in the population following the mutation rate
# and returns new population

def mutation(population,mutationrate):
    r=random.random()
    if(r<mutationrate):
        A=random.randint(0,len(population))
        B=random.randint(0,len(population[0]))
        C=random.randint(0,len(population[0]))
        
        population[A][B],population[A][C]=population[A][C],population[A][B]
    return population

# newgeneticalgo.txt saves the output from the genetic algorithm process

f=open("newgeneticalgo.txt","a")

# we need to generate population initially (which is random) for the process to begin
# generates given specified population and returns list of individuals

def generatepopulation(numberofpopulation,numberofjobs):
    temparray=[]
    for eachind in range(numberofpopulation):
        array1=range(1,numberofjobs+1)
        random.shuffle(array1)
        temparray.append(array1)
    return temparray

# runs genetic algorithm for specified number of iterations

def rungeneticsimulation(iterations,Initializedarray,crossoverrate,mutationrate):
    temparray=Initializedarray
    for iteration in range(iterations):
        
        fitnessarray=[fitnessevaluation(eachpopulation) for eachpopulation in temparray]
#        f.write(" Iteration "+str(iteration)+" Fitness "+str(fitnessarray)+"\n")
        temparray=rouletteselection(temparray,fitnessarray)
        temparray=mating(temparray,crossoverrate)
        temparray=mutation(temparray,mutationrate)
#        f.write(" Iteration "+str(iteration)+" Population "+str(temparray)+"\n")
#        print "Iteration ",str(iteration),fitnessarray,"\n"
#        print temparray
## add timedelta in the argument at the end if one uncommets it        
#        if (time.time() > timedelta):
#            break
        
    return temparray[fitnessarray.index(max(fitnessarray))]

#################################
# Particle swarm algorithm      #
#################################

# creates a particle in given constraints
# returns the created particle

# A particle class is defined here 

class Particle:
    pass

# We need to evaluate the job sequence.So we convert the particle into \
# job sequence using this fucntion

def converttojobsequence(numparr):
    weightarr=array(numparr)
    sortedweightarr=sorted(weightarr)
    sortedseq=range(1,len(weightarr)+1)
    B=[1 for i in range(len(weightarr))]
    for (i,j) in zip(sortedweightarr,sortedseq):
        z=nonzero(weightarr==i)
        B[z[0][0]]=j
    return B


# To improve the efficiency we use this fucntion for fitness evaluation

def fitnesscalc(weightarray):
    return fitnessevaluation(converttojobsequence(weightarray))

# Initialization of the particles and returns the particle array

def createparticles(numberofpopulation,numberofjobs):
    particles = []
    for i in range(numberofpopulation):
        p = Particle()
        p.params = array([random.random() for i in range(numberofjobs)])
        p.fitness = 0.0
        p.v = 0.0
        particles.append(p)
    return particles
    
 
# This code runs the particle swarm algorithm and returns global best

def runparticlesimulation(iter_max,particles,c1,c2):
    gbest = particles[0]
    i=0
    
    while i < iter_max :
        for p in particles:
            fitness = fitnesscalc(p.params)
            if fitness > p.fitness:
                p.fitness = fitness
                p.best = p.params
     
            if fitness > gbest.fitness:
                gbest = p
            v = p.v + c1 * random.random() * (p.best - p.params) \
                    + c2 * random.random() * (gbest.params - p.params)
            p.params = p.params + v
# add time delta in the parameters argument for another approach
#        if(time.time() > timedelta):
#            break
        i  += 1
        #progress bar. '.' = 10%
#        if i % (iter_max/10) == 0:
#            print '.'
    #know fitness by adding gbest.fitness
    return gbest.params


def converttoweightarr(numpsequence):
    sequence=array(numpsequence)
    sortedseq=sorted(sequence)
    sortedweightarr=sorted([random.random() for i in range(len(sequence))])
    B=[1 for i in range(len(numpsequence))]
    for (i,j) in zip(sortedweightarr,sortedseq):
        z=nonzero(numpsequence==j)
        B[z[0][0]]=i
    return B
   
    
    
    
def mainsimulation(iterations,numofpopulation,numofjobs):
    iterations=((numofpopulation*numofjobs)/16)
    previousgabest=rungeneticsimulation(iterations,generatepopulation(numofpopulation,numofjobs),0.9,0.0)
    for i in range(iterations):
        gapop=generatepopulation(numofpopulation-1,numofjobs)
        gapop.append(previousgabest)
        gabest=rungeneticsimulation(iterations,gapop,0.9,0.0)
        psopop=createparticles(numofpopulation-1,numofjobs)
        beforeparticle=converttoweightarr(gabest)
        p=Particle()
        p.params=array(beforeparticle)
        p.fitness=0.0
        p.v=0.0
        
        
        psopop.append(p)
        psobest=runparticlesimulation(iterations,psopop,2,2)
        previousgabest=converttojobsequence(psobest)
    return previousgabest

a=[]
b=[]
for i in range(5):
    z=mainsimulation(30,30,8)
    a.append(z)
    b.append(fitnessevaluation(z))
for i in range(5):
    print a[i]
for i in range(5):
    print b[i]    

print sum(b)/5
    

       
    
    



