# salloc --nodes=1 --ntasks=3  -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 5 1> log_proc001_pop064_gen005_sync.txt 2> /dev/null & # 1 procs
# salloc --nodes=1 --ntasks=3  -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 5 1> log_proc001_pop064_gen005_async.txt 2> /dev/null & # 1 procs
# wait
salloc --nodes=1 --ntasks=4  -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 10 1> log_proc002_pop064_gen010_sync.txt 2> /dev/null & # 2 procs
salloc --nodes=1 --ntasks=4  -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 10 1> log_proc002_pop064_gen010_async.txt 2> /dev/null & # 2 procs
wait
salloc --nodes=1 --ntasks=6  -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 20 1> log_proc004_pop064_gen020_sync.txt 2> /dev/null & # 4 procs
salloc --nodes=1 --ntasks=6  -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 20 1> log_proc004_pop064_gen020_async.txt 2> /dev/null & # 4 procs
wait
salloc --nodes=1 --ntasks=10 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 40 1> log_proc008_pop064_gen040_sync.txt 2> /dev/null & # 8 procs
salloc --nodes=1 --ntasks=10 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 40 1> log_proc008_pop064_gen040_async.txt 2> /dev/null & # 8 procs
wait
salloc --nodes=1 --ntasks=14 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 60 1> log_proc012_pop064_gen060_sync.txt 2> /dev/null & # 12 procs
salloc --nodes=1 --ntasks=14 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 60 1> log_proc012_pop064_gen060_async.txt 2> /dev/null & # 12 procs
wait
salloc --nodes=1 --ntasks=18 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 80 1> log_proc016_pop064_gen080_sync.txt 2> /dev/null & # 16 procs
salloc --nodes=1 --ntasks=18 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 80 1> log_proc016_pop064_gen080_async.txt 2> /dev/null & # 16 procs
wait
salloc --nodes=1 --ntasks=26 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 120 1> log_proc024_pop064_gen120_sync.txt 2> /dev/null & # 24 procs
salloc --nodes=1 --ntasks=26 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 120 1> log_proc024_pop064_gen120_async.txt 2> /dev/null & # 24 procs
wait
salloc --nodes=1 --ntasks=32 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 64 150 1> log_proc030_pop064_gen150_sync.txt 2> /dev/null & # 30 procs, 1 node
salloc --nodes=1 --ntasks=32 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 64 150 1> log_proc030_pop064_gen150_async.txt 2> /dev/null & # 30 procs, 1 node
wait
salloc --nodes=2 --ntasks=64 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 128 150 1> log_proc062_pop128_gen150_sync.txt 2> /dev/null & # 62 procs, 2 nodes
salloc --nodes=2 --ntasks=64 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 128 150 1> log_proc062_pop128_gen150_async.txt 2> /dev/null & # 62 procs, 2 nodes
wait
salloc --nodes=3 --ntasks=96 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 192 150 1> log_proc094_pop192_gen150_sync.txt 2> /dev/null & # 94 procs, 3 nodes
salloc --nodes=3 --ntasks=96 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 192 150 1> log_proc094_pop192_gen150_async.txt 2> /dev/null & # 94 procs, 3 nodes
wait
salloc --nodes=4 --ntasks=128 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python sync_airfoil.py 256 150 1> log_proc126_pop256_gen150_sync.txt 2> /dev/null & # 126 procs, 4 nodes
salloc --nodes=4 --ntasks=128 -A mp309 -t 04:00:00 --qos=interactive -C haswell mpirun python async_airfoil.py 256 150 1> log_proc126_pop256_gen150_async.txt 2> /dev/null & # 126 procs, 4 nodes