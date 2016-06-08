# qsim-experiments

Scripts for driving all experiments described in the `qsim` manuscript.

### Clone repos

Clone the [`qsim`](https://github.com/BenLangmead/qsim) and [`qsim-experiments`](https://github.com/BenLangmead/qsim-experiments) repos.  The `qsim` repo contains the `qsim` software and scripts for building `qsim`-compatible versions of the relevant read aligners.  `qsim-experiments` contains everything else needed to run the experiments described in the manuscript.

```
cd $US/git
git clone git@github.com:BenLangmead/qsim.git
git clone git@github.com:BenLangmead/qsim-experiments.git
```

Substitute an appropriate directory for `$US/git` above.  `$US/git` is the user scratch directory on our MARCC cluster.

### Set up environment

Assuming you're still in the directory from which you did the `git clone`s:

```
export QSIM_HOME=`pwd`/qsim
export QSIM_EXPERIMENTS_HOME=`pwd`/qsim-experiments
```

Consider adding corresponding commands to `.bashrc` or the like.

### Build `qsim`

```
make -C $QSIM_HOME/src
$QSIM_HOME/src/qsim --version
```

`make` is required because, although most of `qsim` is in Python, some helper programs are C++.  You'll need a C++ compiler for this.

### Build software in `qsim-experiments`

Make the required software for read alignment and read simulation.  The read aligners are patched to be `qsim`-compatible.

```
make -f Makefile.src_linux -C qsim-experiments/software/art
make -C qsim-experiments/software/mason
make -C qsim-experiments/software/wgsim
make -C qsim-experiments/software/bowtie2
# For now: make -C qsim-experiments/software/bowtie2 -f Makefile.from_github
make -C qsim-experiments/software/bwa
make -C qsim-experiments/software/snap
```

MARCC note: making mason doesn’t work with `vtune` module loaded.

### Obtain reference genomes and build indexes

Reference genomes (`hg19`, `mm10` and `zm_AGPv3`) and indexes (`bowtie2`, `bwa mem` and `snap`) are used in these experiments.

```
pushd qsim-experiments/experiments/refs
sh get_refs.sh
```

`get_refs.sh` both downloads the relevant reference genomes and runs the `qsim-experiments/experiments/refs/remove_short.py` script on some of them, removing short contigs that cause issues for certain read simulators.

The `submit_index.sh` script submits nine index-building jobs, one for each aligner/genome combination.  The script was written for the MARCC cluster at JHU; you might have to tweak for your cluster.

```
sh index_marcc.sh
# copy and paste the printed sbatch commands to actually submit them
# these jobs will take a few hours
popd
```

### Simulate reads in `qsim-experiments`

```
pushd qsim-experiments/experiments/simulated_reads
python marcc_reads.py wet
# substitute "dry" for "wet" to just print the job-submission commands
popd
```

Many jobs are submitted here.  The longest job takes about 2 hours.

The script was written for the MARCC cluster at JHU; you might have to tweak for your cluster.

### Run `qsim` on simulated datasets in `qsim-experiments`

These scripts are described in more detail in the `qsim-experiments/experiments/simulated_reads/README.md` file.

```
pushd qsim-experiments/experiments/simulated_reads
python marcc_out.py wet
# substitute "dry" for "wet" to just print the job-submission commands
python gather.py --slurm
sbatch .gather.sh  # or edit as appropriate for your cluster
popd
```

Many jobs are submitted here.  All told, this takes about 4 hours for me on MARCC.

The script was written for the MARCC cluster at JHU; you might have to tweak for your cluster.

TODO: those steps do everything but the gathering of CID and CSED curves into a file that gets loaded into R.  Need at add that.

### Run `qsim` on real datasets in `qsim-experiments`

See `qsim-experiments/experiments/real_data/README.md` file for more details.

The user has to issue the commands to the distributed resource manager.  The `sbatch_align.sh` and `sbatch_multialign.sh` scripts generate the jobs and print appropriate submission commands without running them.

The `sbatch_*` scripts are intended for the SLURM DRM, which we use on the MARCC cluster.  You may have to modify the scripts for your cluster.

```
pushd qsim-experiments/experiments/real_data
sh get_real_reads.sh  # might want to submit to your DRM
sh sbatch_align.sh
# copy and paste all the alignment jobs to submit them
# ...when those are done, proceed
sh sbatch_multialign.sh
# copy and paste all the alignment jobs to submit them
popd
```
