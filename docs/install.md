
## Insallation of panpipes



##### Step 1 create virutal environment:

It is advisable to run everything in a virtual environment either pip or conda.

Using pip venv
Navigate to where you want to create your virtual environment  and follow the steps below to create a pip virtual environment
```
mkdir panpipes
cd panpipes
python3 -m venv --prompt=panpipes python3-venv-panpipes/
# This will create a panpipes/venv folder
```

activate the environment

```
cd my-project
source python3-venv-panpipes/bin/activate
```

**OR** using conda:

```
conda create --name pipeline_env python=3.8.6
conda activate pipeline_env
```

we include an environment.yml for a conda environment tested on all the pipelines packaged in this version of Panpipes.

##### Step 2 Download and install this repo


```
git clone https://github.com/DendrouLab/panpipes
cd panpipes
pip install .
```

<!-- 
```
pip install git+https://github.com/DendrouLab/panpipes
``` -->

The pipelines are now installed as a local python package.


### Step 3 installing R requirements
The pipelines use R (mostly for ggplot visualisations). 

If you are using a venv virtual environment,  the pipeline will call a local R installation, so make sure R is installed and install the required pacakges by running the run the code in  `R/install_R_libs.R`

If you are using a conda virtual environment, R *and the required packages (check this)* will be installed along with the python packages. 

### Step 4 pipeline configuration (for SGE or SLURM)
Create a yml file for the cgat core pipeline software to read

```
vim ~/.cgat.yml
```

For SGE servers:
```
cluster:
  queue_manager: sge
  queue: short
condaenv:
```


For Slurm servers:
```
cluster:
    queue_manager: slurm
    queue: short
```

There are likely other options that relate to **your specific server**, e.g. 
These are added as 
```
cluster:
    queue_manager: slurm
    queue: short
    options: --qos=xxx --exclude=compute-node-0[02-05,08-19],compute-node-010-0[05,07,35,37,51,64,68-71]

```

See [cgat-core documentation](https://cgat-core.readthedocs.io/en/latest/getting_started/Cluster_config.html) for cluster specific additional configuration instructions.

Note that there is extra information on the .cgat.yml for Oxford BMRC rescomp users in [docs/installation_rescomp](https://github.com/DendrouLab/sc_pipelines/blob/master/docs/installation_rescomp.md)


### Conda environments
If one or more conda environments are needed to run each of the pipelines, (i.e. one pipeline = one environment) the environment (s) should be specified in the .cgat.yml file or in the pipeline.yml configuration file and it will be picked up by the pipeline as the default environment.

If no environment is specified, the default behaviour of the pipeline is to inherit environment variables from the node where the pipeline is run. However there have been reported issues on SLURM clusters where this was not the default behaviour. In those instances we recommend to add the conda environment param in the .cgat.yml file or in each of the pipeline.yml independently.

i.e. :

```

cluster:
    queue_manager: slurm
    queue: cpu_p
    options: --qos=xxx --exclude=compute-node-0[02-05,08-19],compute-node-010-0[05,07,35,37,51,64,68-71]
condaenv: pipeline_env
```


To check the installation was successful run the following line
```
panpipes --help
```
A list of available pipelines should appear!