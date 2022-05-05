import numpy as np
import subprocess
import time

if __name__ == "__main__":
    for i in range(25):
        test_genome = np.zeros(25)
        test_genome[i] = 1
        
        # test_genome = np.array([0, 0, 0, 0, 1,
        #                         0, 0, 0, 0, 0,
        #                         0, 0, 0, 0, 0,
        #                         0, 0, 0, 0, 0, 
        #                         0, 0, 0, 0, 0]) # this example yields the fifth baseline shape evaluation
        
        start_time = time.time()
        try:
            process = subprocess.run(["./airfoil_exec "+" ".join(np.char.mod('%.12f', test_genome))], check=True, capture_output=True, text=True, shell=True).stdout
            f = np.array(process.split()).astype(np.float64)
            evaluation = [-f[0], -f[1]] # negative signs for minimization
        except: # any errorenous/failing situations will be neglected
            evaluation = [ 0.1 , 0.1 ] 
        end_time = time.time()
        print(i+1,', ',evaluation,'run time: ', end_time-start_time,' seconds')