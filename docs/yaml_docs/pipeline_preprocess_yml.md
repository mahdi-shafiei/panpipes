<style>
  .parameter {
    border-top: 4px solid lightblue;
    background-color: rgba(173, 216, 230, 0.2);
    padding: 4px;
    display: inline-block;
    font-weight: bold;
  }
</style>

# Preprocess YAML

In this documentation, the parameters of the `preprocess` configuration yaml file are explained. 
This file is generated by running `panpipes preprocess config`.  <br> The individual steps run by the pipeline are described in the [preprocess workflow](../workflows/preprocess.md). 

When running the preprocess workflow, panpipes provides a basic `pipeline.yml` file.
To run the workflow on your own data, you need to specify the parameters described below in the `pipeline.yml` file to meet the requirements of your data.
However, we do provide pre-filled versions of the `pipeline.yml` file for individual [tutorials](https://panpipes-pipelines.readthedocs.io/en/latest/tutorials/index.html).

For more information on functionalities implemented in `panpipes` to read the configuration files, such as reading blocks of parameters and reusing blocks with  `&anchors` and `*scalars`, please check [our documentation](./useful_info_on_yml.md).


You can download the different preprocess `pipeline.yml` files here:
- Basic `pipeline.yml` file (not prefilled) that is generated when calling `panpipes preprocess config: [Download here](https://github.com/DendrouLab/panpipes/blob/main/panpipes/panpipes/pipeline_preprocess/pipeline.yml).
- Prefilled `pipeline.yml` file for the [preprocess tutorial](https://panpipes-tutorials.readthedocs.io/en/latest/filtering_data/filtering_data_with_panpipes.html): [Download here](https://github.com/DendrouLab/panpipes-tutorials/blob/main/docs/filtering_data/pipeline.yml).

## Compute resources options

<span class="parameter">resources</span><br>
Computing resources to use, specifically the number of threads used for parallel jobs.
Specified by the following three parameters:
  - <span class="parameter">threads_high</span> `Integer`, Default: 2<br>
        Number of threads used for high intensity computing tasks. 
        For each thread, there must be enough memory to load all your input files at once and create the MuData object.

  - <span class="parameter">threads_medium</span> `Integer`, Default: 2<br>
        Number of threads used for medium intensity computing tasks.
        For each thread, there must be enough memory to load your mudata and do computationally light tasks.

  - <span class="parameter">threads_low</span> `Integer`, Default: 1<br>
  	    Number of threads used for low intensity computing tasks.
        For each thread, there must be enough memory to load text files and do plotting, requires much less memory than the other two.

<span class="parameter">condaenv</span> `String` (Path)<br>
    Path to conda environment that should be used to run panpipes.
    Leave blank if running native or your cluster automatically inherits the login node environment.
    For more information on this, please refer to the detailed explanation [here](https://panpipes-pipelines.readthedocs.io/en/latest/install.html#specifying-conda-environments-to-run-panpipes).

## General project specifications

<span class="parameter">sample_prefix</span> `String`<br>
    Prefix for sample names.

<span class="parameter">unfiltered_obj</span> `String`<br>
    If running this on prefiltered data, complete the following steps:
        1. Leave `unfiltered_obj` (this parameter) blank
        2. Rename your filtered file so that it matches the format PARAMS['sample_prefix'] + '.h5mu'
        3. Put the renamed file in the same folder as the `pipeline.yml`
        4. Set `filtering run` to `False` below

<span class="parameter">modalities</span><br>
    Specify which modalities are included in the data by setting the respective modality to True.
    Leave empty (None) or False to signal this modality is not part of the experiment.
    The modalities are processed in the order of the following list:
  - <span class="parameter">rna</span> `Boolean`, Default: True<br>

  - <span class="parameter">prot</span> `Boolean`, Default: False<br>

  - <span class="parameter">rep</span> `Boolean`, Default: False<br>

  - <span class="parameter">atac</span> `Boolean`, Default: False<br>

## Filtering Cells and Features
Filtering in panpipes is done sequentially for all modalities, filtering first cells and then features.
For each modality, the pipeline.yml file contains a dictionary with the following structure:

```yaml
MODALITY:
    obs:
        min:
        max:
        bool:
    var:
        min:
        max:
        bool:
```

This format can be applied to any modality by editing the filtering dictionary  
You are not restricted by the columns given as default.

This is fully customizable to any columns in the mudata.obs or var object.
When specifying a column name, make sure it exactly matches the column name in the h5mu object.

Example:
```yaml
rna:
  obs:
    min:  # Any column for which you want to run a minimum filter
      n_genes_by_counts: 500  # i.e. will filter out cells with a value less than 500 in the n_genes_by_counts column
    max:  # Any column for which you want to run a maximum filter
      pct_counts_mt: 20  # i.e. each cell may have a maximum of 20 in the pct_counts_mt column
                         # be careful with any columns named after gene sets. 
                         # The column will be named based on the gene list input file, 
                         # so if the mitochondrial genes are in group "mt" 
                         # as in the example given in the resource file,
                         # then the column will be named "pct_counts_mt".
    bool: 
       is_doublet: False  # if you have any boolean columns you want to filter on, 
                          # then use this section of the modality dictionary
                          # in this case any obs['is_doublet'] that are False will be retained in the dataset.
```

<span class="parameter">filtering</span><br>
  - <span class="parameter">run</span> `Boolean`, Default: True<br>
    If set to False, no filtering is applied to the `MuData` object.

  - <span class="parameter">keep_barcodes</span> `String` (Path)<br>
    Path to a file containing specific cell barcodes you want to keep; leave blank if not applicable.

### RNA-specific filtering (rna)
<span class="parameter">obs</span><br>
    Parameters for obs, i.e. cell level filtering:

  - <span class="parameter">min</span><br>
    Filtering cells based on a minimum value in a column. Leave parameters blank if you do not want to filter by them.

    - <span class="parameter">n_genes_by_counts</span> `Integer`<br>
      Minimum number of genes by counts per cell.
      For instance, setting the parameter to 500, will filter out cells with a value less than 500 in the n_genes_by_counts column.

  - <span class="parameter">max</span><br>
    Filtering cells based on a maximum value in a column. Leave parameters blank if you do not want to filter by them.
    
    - <span class="parameter">total_counts</span> `Integer`<br>
      Cells with a total count greater than this value will be filtered out.
    
    - <span class="parameter">n_genes_by_counts</span> `Integer`<br>
      Maximum number of genes by counts per cell.

    - <span class="parameter">pct_counts_mt</span> `Integer` (in Percent)<br>
      Percent of counts that are mitochondrial genes. Cells with a value greater than this will be filtered out.
      Should be a value between 0 and 100 (%).
    
    - <span class="parameter">pct_counts_rp</span> `Integer` (in Percent)<br>
      Percent of counts that are ribosomal genes. Cells with a value greater than this will be filtered out.
      Should be a value between 0 and 100 (%).

    - <span class="parameter">doublet_scores</span> `Integer`<br>
      If you want to apply a custom scrublet threshold per input sample you can specify it here.
      Provide either as one score for all samples (e.g. 0.25), or a csv file with two columns sample_id, and cut off.

  - <span class="parameter">bool</span><br>
      You can add a new column to the mudata['rna'].obs with boolean (True/False) values, and then list
      that column under this bool section. This can be done for any modality.

<span class="parameter">var</span><br>
    Parameters for var, i.e. gene (feature) level filtering:

  - <span class="parameter">min</span><br>

    - <span class="parameter">n_cells_by_counts</span> `Integer`<br>

  - <span class="parameter">max</span><br>

    - <span class="parameter">total_counts</span> `Integer`<br>

    - <span class="parameter">n_cells_by_counts</span> `Integer`<br>

### Protein-specific filtering (prot)
<span class="parameter">obs</span><br>
    Parameters for obs, i.e. cell level filtering:

  - <span class="parameter">max</span><br>
    Filtering cells based on a maximum value in a column. Leave parameters blank if you do not want to filter by them.
    
    - <span class="parameter">total_counts</span> `Integer`<br>
      Cells with a total count greater than this value will be filtered out.
    
### ATAC-specific filtering (atac)
<span class="parameter">var</span><br>
    Parameters for var, i.e. gene (feature) level filtering:

  - <span class="parameter">nucleosome_signal</span><br>

## Intersecting cell barcodes
<span class="parameter">intersect_mods</span> `String`<br>
    Taking observations present only in modalities listed in mods, or all modalities if set to None.  
    Provide a comma separated list where you want to keep only the intersection of barcodes. e.g. rna,prot 

## Downsampling cell barcodes
<span class="parameter">downsample_n</span> `Integer`<br>
    Number of cells to downsample to, leave blank to keep all cells.

<span class="parameter">downsample_col</span> `String`<br>
    If you want to equalise by dataset or sample_id, then specifiy a column in obs of the adata to downsample by here.
    If specified, the data will be subset to n cells **per** downsample_col value.

<span class="parameter">downsample_mods</span> `String` (comma separated)<br>
    Specify which modalities you want to subsample.
    If more than one modality is added then these will be intersected.
    Provide as a comma separated String, e.g.: rna,prot

## Plotting variables
<span class="parameter">plotqc</span><br>
    All metrics in this section should be provided as a comma separated string without spaces e.g. a,b,c
    Leave blank to avoid plotting.

  - <span class="parameter">grouping_var</span> `String` (comma separated), Default: sample_id<br>
        Use these categorical variables to plot/split by.

  - <span class="parameter">rna_metrics</span> `String` (comma separated), Default: pct_counts_mt,pct_counts_rp,pct_counts_hb,pct_counts_ig,doublet_scores<br>
        Specify the metrics in the metadata of the RNA modality to plot.

  - <span class="parameter">prot_metrics</span> `String` (comma separated), Default: total_counts,log1p_total_counts,n_prot_by_counts,pct_counts_isotype<br>
        Specify the metrics in the metadata of the Protein modality to plot.

  - <span class="parameter">atac_metrics</span> `String` (comma separated)<br>
        Specify the metrics in the metadata of the ATAC modality to plot.

  - <span class="parameter">rep_metrics</span> `String` (comma separated)<br>
        Specify the metrics in the metadata of the Rep modality to plot.

## RNA preprocessing steps
Currently, only standard preprocessing steps (sc.pp.normalize_total followed by sc.pp.log1p) is offered for the RNA modality.

<span class="parameter">log1p</span> `Boolean`, Default: True<br>
    If set to False, the log1p transformation is not applied to the RNA modality.

<span class="parameter">hvg</span><br>
Options for the detection of highly variable genes (HVGs) in the RNA modality.

  - <span class="parameter">flavor</span> `String`, Default: seurat<br>
        Choose one of the supported hvg_flavor options: "seurat", "cell_ranger", "seurat_v3".
        For the dispersion based methods "seurat" and "cell_ranger", you can specify parameters: `min_mean`, `max_mean`, `min_disp`(listed below).
        For "seurat_v3" a different method is used, and you need to specify how many variable genes to find by specifying the parameter `n_top_genes`.
        If you specify `n_top_genes`, then the other parameters (`min_mean`, `max_mean`, `min_disp`) are nulled.
        For further reading on this, please refer to the [scanpy API](https://scanpy.readthedocs.io/en/stable/api/scanpy.pp.highly_variable_genes.html).

  - <span class="parameter">batch_key</span> `String`<br>
      If `batch_key` is specified, highly-variable genes are selected within each batch separately and merged.
      For details on this, please refer to the [scanpy API](https://scanpy.readthedocs.io/en/stable/generated/scanpy.pp.highly_variable_genes.html#:~:text=or%20return%20them.-,batch_key,-%3A%20Optional%5B).
      If you want to use more than one obs column as covariates, specify this as as "covariate1,covariate2" (comma separated list).
      Leave blank if no batch should be accounted for in the HVG detection (default behavior).

  - <span class="parameter">n_top_genes</span> `Integer`, Default: 2000<br>
      Number of highly-variable genes to keep. You must specify this parameter if flavor is "seurat_v3".
    
  - <span class="parameter">min_mean</span> `Float`<br>
      Minimum mean expression of genes to be considered as highly variable genes.
      Ignored if `n_top_genes` is specified or if flavor is set to "seurat_v3".
    
  - <span class="parameter">max_mean</span> `Float`<br>
      Maximum mean expression of genes to be considered as highly variable genes.
      Ignored if `n_top_genes` is specified or if flavor is set to "seurat_v3".
    
  - <span class="parameter">min_disp</span> `Float`<br>
      Minimum dispersion of genes to be considered as highly variable genes.
      Ignored if `n_top_genes` is specified or if flavor is set to "seurat_v3".

  - <span class="parameter">exclude_file</span> `String` (Path)<br>
      It may be useful to exclude some genes from the HVG selection.
      In this case, you can provide a file with a list of genes to exclude.
      We provide an example for genes that could be excluded when analyzing immune cells [here](https://github.com/DendrouLab/panpipes/blob/main/panpipes/resources/qc_genelist_1.0.csv).
      When examining this file, you will note that it has three columns, the first specifying the modality, the second one the gene id and the third the groups to which the respective gene belongs.
      This workflow will exclude the genes that are marked accordingly by their group name.
      By default, the workflows will remove the genes that are flagged as "exclude" in the group column from HVG detection.
      You can customize the gene list and change the name of the gene group in the `exclude:` parameter (see below) accordingly.

  - <span class="parameter">exclude</span> `String`<br>
      This variable defines the group name tagging the genes to be excluded in file specified in the previous parameter.
      Leave empty if you don't want to exclude genes from HVG detection.

  - <span class="parameter">filter</span> `Boolean`, Default: False<br>
      Set to True if you want to filter the object to retain only Highly Variable Genes.

<span class="parameter">regress_variables</span> `String` <br>
    Regression variables, specify the variables you want to regress out.
    Leave blank if you don't want to regress out anything.
    We recommend not regressing out anything unless you have good reason to.

### Scaling
Scaling has the effect that all genes are weighted equally for downstream analysis.
Whether applying scaling or not is still a matter of debate, as stated in the [Leucken et al Best Practices paper](https://doi.org/10.15252/msb.20188746):
> "There is currently no consensus on whether or not to perform normalization over genes. 
    While the popular Seurat tutorials (Butler et al, 2018) generally apply gene scaling, 
    the authors of the Slingshot method opt against scaling over genes in their tutorial (Street et al, 2018). 
    The preference between the two choices revolves around whether all genes should be weighted equally for downstream analysis, 
    or whether the magnitude of expression of a gene is an informative proxy for the importance of the gene."


<span class="parameter">run_scale</span> `Boolean`, Default: True <br>
    Set to False if you do not want to scale the data.

<span class="parameter">scale_max_value</span> `Float`<br>
    Clip to this value after scaling.
    If left blank, scaling is run with default parameters, as described in the [scanpy API](https://scanpy.readthedocs.io/en/stable/api/scanpy.pp.scale.html).

### RNA Dimensionality Reduction
<span class="parameter">pca</span><br>
    Parameters for PCA dimensionality reduction.

  - <span class="parameter">n_pcs</span> `Integer`, Default: 50<br>
        Number of principal components to compute.

  - <span class="parameter">solver</span> `String`, Default: default<br>
        Setting this parameter to "default" will use the `arpack` solver.
        If you want to use a different solver, you can specify it as described in the [scanpy API](https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.pca.html).
  
  - <span class="parameter">color_by</span> `String`, Default: sample_id<br>
      The variable to color the PCA plot by. Should be a column in the obs of the adata.


## Protein (PROT) preprocessing steps
<span class="parameter">prot</span><br>
    Parameters for the preprocessing of the protein modality.

  - <span class="parameter">normalisation_methods</span> `String` (comma-separated), Default: clr,dsb<br>
        Comma separated string of normalisation options.
        Available options are: dsb,clr .
        For more details, please refer to the [muon documentation](https://muon.readthedocs.io/en/latest/omics/citeseq.html).
        Muon also provides separate information on [dsb normalisation](https://muon.readthedocs.io/en/latest/api/generated/muon.prot.pp.dsb.html) 
        and [clr normalisation](https://muon.readthedocs.io/en/latest/api/generated/muon.prot.pp.clr.html) methods.
        The normalised count matrices are stored in layers called 'clr' and 'dsb', along with a layer called 'raw_counts'. 
        If you choose to run both (dsb and clr), then 'dsb' is stored in X as default.
        For downstream visualisation, you can either specify the layer, or take the default stored in X.

  - <span class="parameter">clr_margin</span> `Integer` (0 or 1), Default: 1<br>
        Parameter for CLR normalisation.
        The CLR margin determines whether you normalise per cell (as you would normalise RNA data), or by feature (recommended, due to the variable nature of protein assays). 
        Hence, CLR margin 1 is recommended for informative qc plots in this pipeline.
    - 0 = normalise row-wise (per cell)
    - 1 = normalise column-wise (per feature)
  
  - <span class="parameter">background_obj</span> `String` (Path)<br>
        Parameter for DSB normalisation.
        You must specify the path to the background `MuData` (h5mu) object created in the ingest pipeline in order to run dsb normalisation.

  - <span class="parameter">quantile_clipping</span> `Boolean`, Default: True<br>
        Parameter for DSB normalisation.
        Whether to perform quantile clipping on the normalised data.
        Despite normalisation, some cells get extreme outliers which can be clipped as discussed [here](https://github.com/niaid/dsb).
        The maximum value will be set at the 99.5% quantile value, applied per feature.
        Please note that this feature is in the default muon `mu.pp.dsb` code, but manually implemented in this code.

  - <span class="parameter">store_as_X</span> `String`<br>
        If you choose to run more than one normalisation method, specify which normalisation method should be stored in the X slot.
        If left blank, 'dsb' is the default that will be stored in X.

  - <span class="parameter">save_norm_prot_mtx</span> `Boolean`, Default: False<br>
       Specify if you want to save the prot normalised assay additionally as a txt file.

  - <span class="parameter">pca</span> `Boolean`, Default: False<br>
       Specify if you want to run PCA on the normalised protein data. This might be useful, when you have more than 50 features in your protein assay.

  - <span class="parameter">n_pcs</span> `Integer`, Default: 50<br>
       Number of principal components to compute. Specify at least n_pcs <= number of features -1.

  - <span class="parameter">solver</span> `String`, Default: default<br>
       Which solver to use for PCA. If set to "default", the 'arpack' solver is used. 

  - <span class="parameter">color_by</span> `String`, Default: sample_id<br>
       Column to be fetched from the protein layer .obs to color the PCA plot by.

## ATAC preprocessing steps
<span class="parameter">atac</span><br>
    Parameters for the preprocessing of the ATAC modality.

  - <span class="parameter">binarize</span> `Boolean`, Default: False<br>
        If set to True, the data will be binarized.

  - <span class="parameter">normalize</span> `String`, Default: TFIDF<br>
        What normalisation method to use. Available options are "log1p" or "TFIDF".

  - <span class="parameter">TFIDF_flavour</span> `String`, Default: signac<br>
        TFIDF normalisation flavor. Leave blank if you don't use TFIDF normalisation.
        Available options are: "signac", "logTF" or "logIDF".

  - <span class="parameter">feature_selection_flavour</span> `String`, Default: signac<br>
        Flavor for selecting highly variable features (HVF).
        HVF selection either with scanpy's `pp.highly_variable_genes()` function or a `pseudo-FindTopFeatures()` function of the signac package.
        Accordingly, available options are: "signac" or "scanpy".

  - <span class="parameter">min_mean</span> `Float`, Default: 0.05<br>
        Applicable if `feature_selection_flavour` is set to "scanpy".
        You can leave this parameter blank if you want to use the default value.

  - <span class="parameter">max_mean</span> `Float`, Default: 1.5<br>
        Applicable if `feature_selection_flavour` is set to "scanpy".
        You can leave this parameter blank if you want to use the default value.

  - <span class="parameter">min_disp</span> `Float`, Default: 0.5<br>
        Applicable if `feature_selection_flavour` is set to "scanpy".
        You can leave this parameter blank if you want to use the default value.

  - <span class="parameter">n_top_features</span> `Integer`<br>
        Applicable if `feature_selection_flavour` is set to "scanpy".
        Number of highly-variable features to keep.
        If specified, overwrites previous defaults for HVF selection.

  - <span class="parameter">filter_by_hvf</span> `Boolean`, Default: False<br>
        Applicable if `feature_selection_flavour` is set to "scanpy".
        Set to True if you want to filter the ATAC layer to retain only HVFs.

  - <span class="parameter">min_cutoff</span> `String`, Default: q5<br>
        Applicable if `feature_selection_flavour` is set to "signac".
        Can be specified as follows:
    - "q[x]": "q" followed by the minimum percentile, e.g. q5 will set the top 95% most common features as higly variable.
    - "c[x]": "c" followed by a minimum cell count, e.g. c100 will set features present in > 100 cells as highly variable.
    - "tc[x]": "tc" followed by a minimum total count, e.g. tc100 will set features with total counts > 100 as highly variable.
    - "NULL": All features are assigned as highly variable.
    - "NA": Highly variable features won't be changed.

  - <span class="parameter">dimred</span> `String`, Default: LSI<br>
        Available options are: PCA or LSI.
        LSI will only be computed if TFIDF normalisation was used.

  - <span class="parameter">n_comps</span> `Integer`, Default: 50<br>
        Number of components to compute.

  - <span class="parameter">solver</span> `String`, Default: default<br>
        If using PCA, which solver to use. Setting this parameter to "default", will use the 'arpack' solver.

  - <span class="parameter">color_by</span> `String`, Default: sample_id<br>
        Specify the covariate you want to use to color the dimensionality reduction plot.

  - <span class="parameter">dim_remove</span> `TODO`<br>
        Whether to remove the component(s) associated to technical artifacts.
        For instance, it is common to remove the first LSI component, as it is often associated with batch effects.
        Leave blank to avoid removing any.







