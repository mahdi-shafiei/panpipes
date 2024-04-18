import multiprocessing 


import scanpy as sc
import pandas as pd
import matplotlib.pyplot as plt
import scvi
import argparse
import os
import muon as mu

import panpipes.funcs as pp
from panpipes.funcs.io import read_anndata, read_yaml
from panpipes.funcs.scmethods import run_neighbors_method_choice, X_is_raw

import sys
import logging
L = logging.getLogger()
L.setLevel(logging.INFO)
log_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
L.addHandler(log_handler)

# load arguments 
parser = argparse.ArgumentParser()
parser.add_argument('--scaled_anndata',
                    default='adata_scaled.h5ad',
                    help='')
parser.add_argument('--raw_anndata',
                    default=None,
                    help='')
parser.add_argument('--output_csv', default='batch_correction/umap_bc_scvi.csv',
                    help='')
parser.add_argument('--integration_col', default='batch',
                    help='')
parser.add_argument('--figdir', default='./figures',
                    help='')
parser.add_argument('--neighbors_n_pcs',
                    help="n_pcs")
parser.add_argument('--neighbors_method',
                    help="neighbours method, scanpy or hnsw")
parser.add_argument('--neighbors_k',
                    help="neighbors k")
parser.add_argument('--neighbors_metric',
                    help="neighbor metric, e.g. euclidean or cosine")


args, opt = parser.parse_known_args()
L.info(args)

threads_available = multiprocessing.cpu_count()

# load parameters
params = read_yaml("pipeline.yml")

# scanpy settings
sc.set_figure_params(facecolor="white")
sc.settings.autoshow = False
sc.settings.figdir = args.figdir


# test_script=params['rna']['scvi']['testrun']
test_script=False
if test_script:
    L.info("this is a test run")
    params['rna']['scvi']['training_args']['max_epochs'] = 10


# load an process the scaled snRNAseq dataset --------------------------------------------------


L.info("Reading in Data from '%s'" % args.scaled_anndata)
mdata = mu.read(args.scaled_anndata)
if type(mdata) is mu.MuData:
    rna = mdata['rna']
    L.info(rna)
elif type(mdata) is sc.AnnData:
    rna = mdata
    L.info(rna)
else:
    L.error("Unknown file type. File not MuData or Anndata")
    sys.exit("Unknown file type. File not MuData or Anndata")

# this is a copy so we can subset vars and obs without changing the original object


# in case of more than 1 variable, create a fake column with combined information
columns = [x.strip() for x in args.integration_col.split(",")]
if len(columns) > 1:
    L.info("Using 2 columns to integrate on more variables")
    # bc_batch = "_".join(columns)
    rna.obs["bc_batch"] = rna.obs[columns].apply(lambda x: '|'.join(x), axis=1)

    # make sure that batch is a categorical
    rna.obs["bc_batch"] = rna.obs["bc_batch"].astype("category")
else:
    rna.obs['bc_batch'] = rna.obs[args.integration_col]


# add in raw counts as a layer 
# add in test to see if raw layer exists alread
if "raw_counts" in rna.layers.keys():
    L.info("Found raw counts in .layers['raw_counts']")
elif X_is_raw(rna):
    L.info("Found raw counts in .X. Saving raw counts to .layers['raw_counts']")
    rna.layers["raw_counts"] = rna.X.copy()
else:
    L.info("Merging in raw counts from '%s" % args.raw_anndata)
    sc_raw = read_anndata(args.raw_anndata, use_muon=True, modality="rna")
    #filter by barcodes in the scaled object
    sc_raw = sc_raw[sc_raw.obs_names.isin(rna.obs_names),: ]
    L.info("Saving raw counts to .layers['raw_counts]")
    rna.layers["raw_counts"] = sc_raw.X.copy()


# filter out mitochondria
if params['rna']['scvi']['exclude_mt_genes']:
    L.info("Filtering out mitochondrial genes")
    rna = rna[:, ~rna.var[params['rna']['scvi']['mt_column']]]

# filter by Hvgs
L.info("Filtering by HVGs")
rna = rna[:, rna.var.highly_variable]


if test_script:
    nn=1000
    L.info("this is a test so downsampling the dataset to %i cells" % nn)
    sc.pp.subsample(rna, n_obs=nn)

rna = rna.copy()


L.info("Setting up AnnData")
scvi.model.SCVI.setup_anndata(
    rna,
    layer="raw_counts",
    batch_key='bc_batch'
)

scvi_model_args =  {k: v for k, v in params['rna']['scvi']['model_args'].items() if v is not None}
scvi_training_args =  {k: v for k, v in params['rna']['scvi']['training_args'].items() if v is not None}
scvi_training_plan =  {k: v for k, v in params['rna']['scvi']['training_plan'].items() if v is not None}

L.info("Defining model")
vae = scvi.model.SCVI(rna, **scvi_model_args) 
L.info("Running scVI")
vae.train(**scvi_training_args, plan_kwargs=scvi_training_plan) 

vae.save(os.path.join("batch_correction", "scvi_model"), 
                  anndata=False)

# no early stopping?
L.info("Plotting ELBO")
vae.history["elbo_train"].plot()
plt.savefig(os.path.join(args.figdir, "scvi_elbo_train.png"))

fig, axs = plt.subplots(nrows=4, ncols=4, figsize=(16,10))
axs = axs.ravel()
for i, kk in enumerate(vae.history.keys()):
    vae.history[kk].plot(ax=axs[i])
    
fig.tight_layout()
plt.savefig(os.path.join(args.figdir, "scvi_metrics.png"))

# vae.history['elbo_train']['elbo_train'].to_list()
L.info("Extracting latent space")
latent = vae.get_latent_representation()
L.info("Saving latent to X_scVI")
rna.obsm["X_scVI"] = latent
rna.obs['bc_batch'] = rna.obs['bc_batch']

L.info("Plotting latent")
sc.pl.embedding(rna, "X_scVI", color="bc_batch", save="_batch.png")

plot_df = pd.DataFrame(latent[:, 0:2])
plot_df['bc_batch'] = rna.obs['bc_batch'].tolist()

if int(args.neighbors_n_pcs) > rna.obsm['X_scVI'].shape[1]:
    L.warn(f"N PCs is larger than X_scVi dimensions, reducing n PCs to  {rna.obsm['X_scVI'].shape[1] -1}")

n_pcs= min(int(args.neighbors_n_pcs), rna.obsm['X_scVI'].shape[1]-1)

# use scVI latent space for UMAP generation
# sc.pp.neighbors(rna,n_neighbors=int(args.n_neighbors), use_rep="X_scVI")
L.info("Computing neighbors")
run_neighbors_method_choice(rna, 
    method=args.neighbors_method, 
    n_neighbors=int(args.neighbors_k), 
    n_pcs=n_pcs, 
    metric=args.neighbors_metric, 
    use_rep='X_scVI',
    nthreads=max([threads_available, 6]))

L.info("Computing UMAP")
sc.tl.umap(rna)

L.info("Plotting UMAP")
sc.pl.umap(
    rna,
    color=["bc_batch",],
    frameon=False, save="_scvi_batch.png"
)

L.info("Saving UMAP coordinates to csv file '%s" % args.output_csv)
umap = pd.DataFrame(rna.obsm['X_umap'], rna.obs.index)
umap.to_csv(args.output_csv)

# save anndata to be used by other scvi tools applications
L.info("Saving AnnData to 'tmp/scvi_scaled_adata_rna.h5ad'")
rna.write(os.path.join("tmp", "scvi_scaled_adata_rna.h5ad"))

L.info("Done")

