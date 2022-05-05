import sys
# e.g. mpirun -np 32 python ~.py
NUM_PROCESSES = int(sys.argv[1])  # num of processors
NUM_POP       = int(sys.argv[2]) # size of population
NUM_GEN       = int(sys.argv[3])  # num of generations ! in async, it determines # of total birth as num_gen * num_pop

import numpy as np
import distributed
import abc, itertools
import uuid, time, os, platform
import matplotlib.pyplot as plt

from dask_mpi import initialize
from dask.distributed import Client, LocalCluster

from pymoo.core.repair import NoRepair
from pymoo.core.mating import Mating
from pymoo.core.duplicate import DefaultDuplicateElimination
from pymoo.core.problem import Problem
from pymoo.core.population import Population
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.operators.crossover.sbx import SimulatedBinaryCrossover
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.util.randomized_argsort import randomized_argsort
from pymoo.util.plotting import plot
from pymoo.factory import get_problem
from pymoo.algorithms.moo.nsga2 import NSGA2, RankAndCrowdingSurvival, calc_crowding_distance, binary_tournament

import subprocess

class Decoder(abc.ABC):
    @abc.abstractmethod
    def decode(self, genome, *args, **kwargs):
        pass

class IdentityDecoder(Decoder):
    def __init__(self):
        super().__init__()

    def decode(self, genome, *args, **kwargs):
        return genome

    def __repr__(self):
        return type(self).__name__ + "()"

class Individual:
    def __init__(self, genome, decoder=IdentityDecoder()):
        self.genome = genome
        self.decoder = decoder
        self.fitness = None
    
    @classmethod
    def create_population(cls, n, initialize, decoder):
        return [cls(genome=initialize(), decoder=decoder) for _ in range(n)]
    
    @classmethod
    def evaluate_population(cls, population):
        for individual in polulation:
            individual.evaluate()
        
        return population
    
    def decode(self, *args, **kwargs):
        return self.decoder.decode(self.gnome, args, kwargs)
    
    def evaluate(self): # airfoil
        try:
            process = subprocess.run(["./airfoil_exec "+" ".join(np.char.mod('%.12f', self.genome))], check=True, capture_output=True, text=True, shell=True).stdout
            f = np.array(process.split()).astype(np.float64)
            self.fitness = [-f[0], -f[1]] # negative signs for minimization
        except:
            self.fitness = [ 0.0 , 0.0 ] # any errorenous situations will be neglected
        
    def __iter__(self):
        return self.genome.__iter__()

    def __str__(self):
        return f'{self.genome!s} {self.fitness!s}'

    def __repr__(self):
        return f"{type(self).__name__}({self.genome.__repr__()}, " \
               f"{self.decoder.__repr__()})"
    
class DistributedIndividual(Individual):
    birth_id = itertools.count()
    
    def __init__(self, genome, decoder=None):
        super().__init__(genome, decoder)

        self.uuid = uuid.uuid4()
        self.birth_id = next(DistributedIndividual.birth_id)
        self.start_eval_time = None
        self.stop_eval_time = None
    
    def __str__(self):
        return f'{self.uuid} birth: {self.birth_id} fitness: {self.fitness!s} ' \
               f'genome: {self.genome!s} '

class RankAndCrowdingSurvivalMod(RankAndCrowdingSurvival):
    def _do(self, pops, *args, n_survive=None, **kwargs):
        F, P = [], []
        for pop in pops:
            F.append(pop.fitness)
            P.append(pop)
        F = np.array(F).astype(float, copy=False)

        survivors = []
        fronts = self.nds.do(F, n_stop_if_ranked=n_survive)

        for k, front in enumerate(fronts):
            crowding_of_front = calc_crowding_distance(F[front, :])
            if len(survivors) + len(front) > n_survive:
                I = randomized_argsort(crowding_of_front, order='descending', method='numpy')
                I = I[:(n_survive - len(survivors))]
            else:
                I = np.arange(len(front))
            survivors.extend(front[I])
        G = []
        for surv in survivors:
            G.append(P[surv])
        return G
    
def create_rand_sequence(length, xl, xu):
    def create():
        zerotoone = np.random.random(length)
        norm = (xu - xl) * zerotoone + xl
        return norm
    
    return create

def evaluate(individual):
    worker = distributed.get_worker()
    
    individual.start_eval_time = time.time()

    if hasattr(worker, 'logger'):
        worker.logger.debug(
            f'Worker {worker.id} started evaluating {individual!s}')
        
    individual.evaluate()

    individual.stop_eval_time = time.time()
    individual.hostname = platform.node()
    individual.pid = os.getpid()
    
    if hasattr(worker, 'logger'):
        worker.logger.debug(
            f'Worker {worker.id} evaluated {individual!s} in '
            f'{individual.stop_eval_time - individual.start_eval_time} '
            f'seconds')

    return individual
        
if __name__ == "__main__":
    initialize()
    cluster = LocalCluster(dashboard_address=None, threads_per_worker=1)
    cluster.scale(NUM_PROCESSES)
    client = Client(cluster)
    print("STARTED. Async, Proc",f'{NUM_PROCESSES:03d}'," Popu ",f'{NUM_POP:06d}'," Gens ",f'{NUM_GEN:03d}')

    pop_size = NUM_POP
    birth_limit = NUM_GEN*NUM_POP # similar to gen_limit

    # # Wait for stabilization... not sure it's necessary though
    # print("WAIT FOR 5 SECONDS...")
    # time.sleep(5)
    # print("GA INITIALIZED")

    t_start = time.time()

    # Asynchronous population initialization
    init_pop = np.ceil(pop_size*2.).astype('int')
    parents = DistributedIndividual.create_population(init_pop, initialize=create_rand_sequence(25, xl=-1, xu=1), decoder=IdentityDecoder())
    
    # Population guess
    dat = np.genfromtxt("init.csv",delimiter=',')
    for i in range(len(parents)):
        parents[i].genome = dat[i]

    worker_futures = client.map(evaluate, parents, pure=False)
    as_completed_iter = distributed.as_completed(worker_futures)
    pop_bag = []

    num_offspring = 0 # initialize

    # # Wait for stabilization... not sure it's necessary though
    # print("WAIT FOR 5 MORE SECONDS...")
    # time.sleep(5)

    # print("GA STARTS")

    mating = Mating(selection=TournamentSelection(func_comp=binary_tournament),
                crossover=SimulatedBinaryCrossover(eta=15, prob=0.9),
                mutation=PolynomialMutation(prob=None, eta=20),
                repair=NoRepair(),
                eliminate_duplicates=DefaultDuplicateElimination(),
                n_max_iterations=100)
    
    # Main GA solver
    for i, evaluated_future in enumerate(as_completed_iter):
        if i == birth_limit:
            break
        evaluated = evaluated_future.result()
        # print(i+1, ', evaluated: ', evaluated.genome, evaluated.fitness)
        print(f'{i+1:06d}',
              ', worker: ',f'{evaluated.pid:06d}',
              ', evaluated: ', f'{evaluated.fitness[0]:12.4e}',', ',f'{evaluated.fitness[1]:12.4e}',
              ', end: ',f'{evaluated.stop_eval_time-t_start:.4f}', ' , start: ',f'{evaluated.start_eval_time-t_start:.4f}')

        pop_bag.append(evaluated)

        P = np.array([pop.genome for pop in pop_bag])
        F = np.array([pop.fitness for pop in pop_bag])
        Popu = Population.create(P)
        for j in range(np.shape(F)[0]):
            Popu[j].F = F[j]
            Popu[j].CV = np.zeros(1)
            
        if len(pop_bag) > pop_size:
            survival = RankAndCrowdingSurvival()
            Popu = survival.do(problem=Problem(), pop=Popu, n_survive=pop_size)
            survival = RankAndCrowdingSurvivalMod()
            pop_bag  = survival._do(pops=pop_bag, n_survive=pop_size)

            if num_offspring < birth_limit: 
                mating = Mating(selection=TournamentSelection(func_comp=binary_tournament),
                                crossover=SimulatedBinaryCrossover(eta=15, prob=0.9),
                                mutation=PolynomialMutation(prob=None, eta=20),
                                repair=NoRepair(),
                                eliminate_duplicates=DefaultDuplicateElimination(),
                                n_max_iterations=100)
                off = mating.do(problem=Problem(n_var=np.shape(Popu[0].X)[0], xl=0., xu=1.), pop=Popu, n_offsprings=1, algorithm=NSGA2())
                offspring = DistributedIndividual.create_population(1, initialize=create_rand_sequence(25, xl=0, xu=1), decoder=IdentityDecoder())
                offspring[0].genome=off.get("X").reshape((25,))

                as_completed_iter.add(client.submit(evaluate, offspring[0]))

        # Save pseudo-generational data
        if (i+1) % pop_size == 0:
            # print(f'{int((i+1)/pop_size):05d}')
            np.savetxt(fname='./GAdata/Async_Airf_Gen_'+f'{int((i+1)/pop_size):05d}'+'_Population.csv', delimiter=",", X=Popu.get("X"))
            np.savetxt(fname='./GAdata/Async_Airf_Gen_'+f'{int((i+1)/pop_size):05d}'+'_Score.csv', delimiter=",", X=Popu.get("F"))
                
        num_offspring += 1

#         if (i+1) == pop_size:
#             survival = RankAndCrowdingSurvival()
#             Popu = survival.do(problem=Problem(), pop=Popu, n_survive=pop_size)
#             for p in Popu:
#                 p.CV = np.zeros(1)
#             off = mating.do(problem=Problem(n_var=np.shape(Popu[0].X)[0], xl=-1., xu=1.), pop=Popu, n_offsprings=pop_size, algorithm=NSGA2())
#             offspring = DistributedIndividual.create_population(pop_size, initialize=create_rand_sequence(25, xl=-1, xu=1), decoder=IdentityDecoder())
#             for k in range(pop_size):
#                 offspring[k].genome = off.get("X").reshape((25,len(offspring)))[:,k]
#                 as_completed_iter.add(client.submit(evaluate, offspring[k]))

#         if len(pop_bag) >= 2*pop_size:
#             survival = RankAndCrowdingSurvival()
#             Popu = survival.do(problem=Problem(), pop=Popu, n_survive=pop_size)
#             for p in Popu:
#                 p.CV = np.zeros(1)
#             survival = RankAndCrowdingSurvivalMod()
#             pop_bag  = survival._do(pops=pop_bag, n_survive=pop_size)

#             off = mating.do(problem=Problem(n_var=np.shape(Popu[0].X)[0], xl=-1., xu=1.), pop=Popu, n_offsprings=pop_size, algorithm=NSGA2())
#             offspring = DistributedIndividual.create_population(pop_size, initialize=create_rand_sequence(25, xl=-1, xu=1), decoder=IdentityDecoder())
#             for k in range(pop_size):
#                 offspring[k].genome = off.get("X").reshape((25,len(offspring)))[:,k]
#                 as_completed_iter.add(client.submit(evaluate, offspring[k]))
#             # offspring[0].genome=off.get("X").reshape((25,))

#             # as_completed_iter.add(client.submit(evaluate, offspring[0]))

#             num_offspring += pop_size

    t_end = time.time()
    print('DASK:',t_end-t_start)
    
#     # X: genome, F: fitness
#     X = Popu.get("X")
#     F = Popu.get("F")
    
#     # Design space plot
#     xl, xu = 0, 1
#     plt.figure(figsize=(7, 5))
#     plt.scatter(X[:, 0], X[:, 1], s=30, facecolors='none', edgecolors='r')
#     plt.xlim(xl, xu)
#     plt.ylim(xl, xu)
#     plt.title("Design Space")
#     plt.show()

#     # Objective space plot
#     plt.figure(figsize=(7, 5))
#     plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue', label="Solutions")
#     plt.title("Objective Space (ZDT3)")
#     pf = get_problem("zdt3").pareto_front(use_cache=False, flatten=True)
#     plt.plot(pf[:, 0], pf[:, 1], alpha=0.5, marker="o", linewidth=0, color="red", label="Pareto-front")
#     plt.legend()
#     plt.show()
    
    # Close the DASK client
    as_completed_iter.clear()
    client.close()
