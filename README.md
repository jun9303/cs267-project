# cs267-project

0. Go to Cori Jupyter Hub[https://jupyter.nersc.gov/hub/]. Turn on the terminal in a notebook environment.
    - You may need to set up the modules (via cori_module_list.txt), conda env (via conda_environments.yml, use py37) and python libs (via python_requirements.txt)

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
4. Run the program (2 procs, rank 0 & 1, are non-workers and instead used as a scheduler & master, respectively)
    - For sync,
      salloc --nodes=NODES --ntasks=PROCS+2 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py POPS GENS 1> log_filename_sync.txt 2> /dev/null &
    - For async,
      salloc --nodes=NODES --ntasks=PROCS+2 -A mp309 -t 01:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py POPS GENS 1> log_filename_sync.txt 2> /dev/null &

ex) strong scaling -- run ./run_strong.sh
ex) weak scaling -- run ./run_weak.sh