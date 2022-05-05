# cs267-project

1. Unzip the whole package in your scratch space 
    - cd $CSCRATCH
    - mkdir folder_name
    - cd folder_name 
    - tar -xvf ga_cs267.tar
2. load python & openmpi modules
    - module load openmpi/4.1.2
    - module load python/3.9-anaconda-2021.11
3. Install all required Python libraries. requirements.txt contains the Python dependency information
    - pip install -r requirements.txt
4. Run the program
    - For sync,
      salloc --nodes=[NODES] --ntasks-per-core=1 -A mp309 -t 10:00:00 --qos=regular -C haswell mpirun -np [NODES]*32 python sync_airfoil.py  [NUM_PROCS] [NUM_POPU] [NUM_GENS] 1> [log_file_name]
    - For async,
      salloc --nodes=[NODES] --ntasks-per-core=1 -A mp309 -t 10:00:00 --qos=regular -C haswell mpirun -np [NODES]*32 python async_airfoil.py [NUM_PROCS] [NUM_POPU] [NUM_GENS] 1> [log_file_name]

example) strong scaling --
salloc --nodes=2 --ntasks-per-node=32 --ntasks-per-core=1 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun -np 64 python sync_airfoil.py 64 64 5 1> log_proc64_pop64_gen5_sync.txt
salloc --nodes=1 --ntasks-per-node=32 --ntasks-per-core=1 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun -np 32 python sync_airfoil.py 32 64 5 1> log_proc32_pop64_gen5_sync.txt
salloc --nodes=1 --ntasks-per-node=16 --ntasks-per-core=1 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun -np 16 python sync_airfoil.py 16 64 5 1> log_proc16_pop64_gen5_sync.txt
salloc --nodes=1 --ntasks-per-node=4 --ntasks-per-core=1 -A mp309 -t 02:00:00 --qos=interactive -C haswell mpirun -np 4  python sync_airfoil.py 4 64 5 1> log_proc04_pop64_gen5_sync.txt
salloc --nodes=1 --ntasks-per-node=2 --ntasks-per-core=1 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun -np 2  python sync_airfoil.py 1 64 5 1> log_proc01_pop64_gen5_sync.txt 
(np 2 for serial bc dask-mpi's scheduler proc)

salloc --nodes=2 --ntasks-per-node=32 --ntasks-per-core=1 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun -np 64 python async_airfoil.py 64 64 5 1> log_proc64_pop64_gen5_async.txt
salloc --nodes=1 --ntasks-per-node=32 --ntasks-per-core=1 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun -np 32 python async_airfoil.py 32 64 5 1> log_proc32_pop64_gen5_async.txt
salloc --nodes=1 --ntasks-per-node=16 --ntasks-per-core=1 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun -np 16 python async_airfoil.py 16 64 5 1> log_proc16_pop64_gen5_async.txt
salloc --nodes=1 --ntasks-per-node=4 --ntasks-per-core=1 -A mp309 -t 02:00:00 --qos=interactive -C haswell mpirun -np 4  python async_airfoil.py 4 64 5 1> log_proc04_pop64_gen5_async.txt
salloc --nodes=1 --ntasks-per-node=2 --ntasks-per-core=1 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun -np 2  python async_airfoil.py 1 64 5 1> log_proc01_pop64_gen5_async.txt
(np 2 for serial bc dask-mpi's scheduler proc)