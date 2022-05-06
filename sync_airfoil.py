import sys
# e.g. mpirun -np 32 python ~.py
# NUM_PROCESSES = int(sys.argv[1])  # num of processors
NUM_POP       = int(sys.argv[1])  # size of population
NUM_GEN       = int(sys.argv[2])  # num of generations ! in async, it determines # of total birth as num_gen * num_pop

#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import array
import random
import json
import subprocess
import time, os

import numpy

import dask
from dask_mpi import initialize
from dask.distributed import Client, LocalCluster, performance_report
import dask.bag as db
from mpi4py import MPI
# import multiprocessing

from math import sqrt

from deap import algorithms
from deap import base
from deap import benchmarks
from deap.benchmarks.tools import diversity, convergence, hypervolume
from deap import creator
from deap import tools

import jupyter_server_proxy

def dask_map(func, iterable):
    bag = db.from_sequence(iterable).map(func)
    return bag.compute()

t_start = time.time()

creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

# Problem definition
# Functions zdt1, zdt2, zdt3, zdt6 have bounds [0, 1]
BOUND_LOW, BOUND_UP = -1.0, 1.0

# Functions zdt4 has bounds x1 = [0, 1], xn = [-5, 5], with n = 2, ..., 10
# BOUND_LOW, BOUND_UP = [0.0] + [-5.0]*9, [1.0] + [5.0]*9

# Functions zdt1, zdt2, zdt3 have 30 dimensions, zdt4 and zdt6 have 10
NDIM = 25

def uniform(low, up, size=None):
    try:
        return [random.uniform(a, b) for a, b in zip(low, up)]
    except TypeError:
        return [random.uniform(a, b) for a, b in zip([low] * size, [up] * size)]

toolbox.register("attr_float", uniform, BOUND_LOW, BOUND_UP, NDIM)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_float)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def initPopulation(pcls, ind_init, file):
    dat = numpy.genfromtxt(file,delimiter=',')
    return pcls(ind_init(c) for c in dat[:NUM_POP])

toolbox.register("population_guess", initPopulation, list, creator.Individual, "init.csv")

def evaluate(ind):
    w = numpy.array([])
    for x in ind:
        w = numpy.append(w,[x])

    st = time.time()
    try:
        process = subprocess.run(["./airfoil_exec "+" ".join(numpy.char.mod('%.12f', w))], check=True, capture_output=True, text=True, shell=True).stdout
        f = numpy.array(process.split()).astype(numpy.float64)
        fitness = [-f[0], -f[1]] # negative signs for minimization
    except:
        fitness = [ 0.0 , 0.0  ] # any errorenous situations will be neglected    
    et = time.time()
    
    print('worker: ',f'{os.getpid():06d}',
          ', evaluated: ', f'{fitness[0]:12.4e}',', ',f'{fitness[1]:12.4e}',
          ', end: ',f'{et-start:.4f}', ' , start: ',f'{st-start:.4f}')
#     print("evaluated on " + multiprocessing.current_process().name + ": ",fitness)
        
    return fitness

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=BOUND_LOW, up=BOUND_UP, eta=15.0)
toolbox.register("mutate", tools.mutPolynomialBounded, low=BOUND_LOW, up=BOUND_UP, eta=20.0, indpb=1.0/NDIM)
toolbox.register("select", tools.selNSGA2)

# Synchronous stuff -----
# pool = multiprocessing.Pool(processes=NUM_PROCESSES) # CHANGE NUM PROCESSES
toolbox.register('map', dask_map)
# toolbox.register("map", pool.map)

def recordData(pop, gen):
    x = numpy.empty([len(pop),NDIM])
    f = numpy.empty([len(pop),2])
    itera = 0
    for ind in pop:
        x[itera] = numpy.array([val for val in ind])
        f[itera] = numpy.array(ind.fitness.values)
        itera += 1
    numpy.savetxt(fname='./GAdata/Sync_Airf_Gen_'+f'{gen+1:05d}'+'_Population.csv', delimiter=",", X=x)
    numpy.savetxt(fname='./GAdata/Sync_Airf_Gen_'+f'{gen+1:05d}'+'_Score.csv', delimiter=",", X=f)

def main(seed=None):
    random.seed(seed)

    NGEN = NUM_GEN
    MU = NUM_POP
    CXPB = 0.9

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    # stats.register("avg", numpy.mean, axis=0)
    # stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    # pop = toolbox.population(n=MU)
    pop = toolbox.population_guess()
    
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop] # if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    # pop = toolbox.select(pop, len(pop))

    # record = stats.compile(pop)
    # logbook.record(gen=0, evals=len(invalid_ind), **record)
    # print(logbook.stream)

    recordData(pop, 0)   
    
    # Begin the generational process
    for gen in range(1, NGEN):
        # Vary the population
        offspring = toolbox.select(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]

        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)

            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring] # if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)
        # record = stats.compile(pop)
        # logbook.record(gen=gen, evals=len(invalid_ind), **record)
        # print(logbook.stream)

        recordData(pop, gen)

    print("Final population hypervolume is %f" % hypervolume(pop, [11.0, 11.0]))

    return pop, logbook

if __name__ == "__main__":
    dask.config.config["distributed"]["dashboard"]["link"] = "{JUPYTERHUB_SERVICE_PREFIX}proxy/{host}:{port}/status"
    initialize(nthreads=1)
    # cluster = LocalCluster(dashboard_address=":0", threads_per_worker=1)
    # cluster.scale(NUM_PROCESSES)
    client = Client()
    
    # Wait for stabilization... not sure it's necessary though
    print("WAIT FOR 5 SECONDS...")
    time.sleep(5)
    print(client)
    print("STARTED. Sync") # , Proc",f'{MPI.COMM_WORLD.Get_size()-2:03d}'," Popu ",f'{NUM_POP:06d}'," Gens ",f'{NUM_GEN:03d}

    # with open("pareto_front/zdt1_front.json") as optimal_front_data:
    #     optimal_front = json.load(optimal_front_data)
    # Use 500 of the 1000 points in the json file
    # optimal_front = sorted(optimal_front[i] for i in range(0, len(optimal_front), 2))
    
    start = time.time()
    with performance_report(filename='report_proc'+f'{MPI.COMM_WORLD.Get_size()-2:03d}'+'_pop'+f'{NUM_POP:03d}'+'_gen'+f'{NUM_GEN:03d}'+'_sync.html'):
        pop, stats = main()

    end = time.time()
    print(end - start)

    # pop.sort(key=lambda x: x.fitness.values)

    # print(stats)
    # print("Convergence: ", convergence(pop, optimal_front))
    # print("Diversity: ", diversity(pop, optimal_front[0], optimal_front[-1]))

    # import matplotlib.pyplot as plt
    # import numpy

    # front = numpy.array([ind.fitness.values for ind in pop])
    # optimal_front = numpy.array(optimal_front)
    # plt.scatter(optimal_front[:,0], optimal_front[:,1], c="r")
    # plt.scatter(front[:,0], front[:,1], c="b")
    # plt.axis("tight")
    # plt.show()

    # Close the DASK client
    client.close()